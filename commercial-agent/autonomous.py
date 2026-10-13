"""Autonomous Commercial Agent — runs unattended on a schedule.

This script performs a full morning routine:
1. Check unread emails → identify real prospects → draft responses
2. Check HubSpot tasks due today
3. Follow up on stale prospects
4. Log activity summary

agent.log and reports/ live in the project root, or in $AGENT_DATA_DIR when
set — never in whatever directory the script happens to be launched from.
"""

import logging
import sys
from datetime import datetime

from dotenv import load_dotenv

# Load .env before importing modules that resolve settings at import time.
load_dotenv()

from agent_loop import run_agent_loop  # noqa: E402
from config import paths  # noqa: E402
from config.routines import ROUTINES  # noqa: E402
from config.system_prompt import get_system_prompt  # noqa: E402
from tools import ALL_TOOLS, execute_tool  # noqa: E402

log = logging.getLogger("commercial-agent")

# The shared loop reports failures as text rather than exceptions.
FAILURE_PREFIXES = ("API Error", "Error:", "Agent stopped:")


def _configure_logging() -> None:
    log_path = paths.log_file()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
        # The SDK installs its own root handler when ANTHROPIC_LOG is set; without
        # force, agent.log would stay empty and update_status.py would see nothing.
        force=True,
    )


def run_autonomous(routine: str) -> str:
    """Run an autonomous routine via the shared agent loop."""
    if routine not in ROUTINES:
        log.error(f"Unknown routine: {routine}. Available: {list(ROUTINES.keys())}")
        return f"Error: unknown routine '{routine}'"

    log.info(f"Starting routine: {routine}")

    result = run_agent_loop(
        user_prompt=ROUTINES[routine],
        system_prompt=get_system_prompt(),
        tools=ALL_TOOLS,
        execute_tool=execute_tool,
        max_iterations=25,
        on_text=lambda text: log.info(f"  Agent: {text[:200]}"),
    )

    log.info(f"Routine '{routine}' result:\n{result[:500]}")
    return result


def main() -> int:
    """Entry point — determines which routine to run based on args or time."""
    _configure_logging()

    if len(sys.argv) > 1:
        routine = sys.argv[1]
    else:
        # Auto-select based on time of day
        hour = datetime.now().hour
        weekday = datetime.now().weekday()

        if weekday == 4 and hour >= 16:  # Friday afternoon
            routine = "weekly_audit"
        elif hour < 12:
            routine = "morning"
        else:
            routine = "followup"

    log.info(f"=== AUTONOMOUS AGENT — {routine.upper()} — {datetime.now().isoformat()} ===")
    result = run_autonomous(routine)

    # Save report
    report_dir = paths.reports_dir()
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"{routine}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"=== {routine.upper()} — {datetime.now().isoformat()} ===\n\n")
        f.write(result)

    log.info(f"Report saved: {report_file}")
    # Propagate failures to cron/CI instead of exiting 0 after an API error,
    # an unknown routine or the iteration cap. The report is kept for diagnosis.
    if result.startswith(FAILURE_PREFIXES):
        log.error("Routine failed; report saved for diagnosis.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
