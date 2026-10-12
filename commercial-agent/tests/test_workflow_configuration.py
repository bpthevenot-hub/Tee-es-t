from __future__ import annotations

import os
import subprocess
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/robot.yml"


def configuration_script() -> str:
    lines = WORKFLOW.read_text().splitlines()
    step_start = lines.index("      - name: Check required configuration")
    run_start = lines.index("        run: |", step_start)
    script = []
    for line in lines[run_start + 1 :]:
        if line.startswith("      - name: "):
            break
        script.append(line[10:] if line.startswith("          ") else "")
    return "\n".join(script)


def run_configuration(
    tmp_path: Path, event_name: str, secrets: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    summary = tmp_path / "summary"
    output = tmp_path / "output"
    env = os.environ | {
        "GITHUB_EVENT_NAME": event_name,
        "GITHUB_STEP_SUMMARY": str(summary),
        "GITHUB_OUTPUT": str(output),
        "GITHUB_SERVER_URL": "https://github.com",
        "GITHUB_REPOSITORY": "bpthevenot-hub/Tee-es-t",
        "ANTHROPIC_API_KEY": (secrets or {}).get("ANTHROPIC_API_KEY", ""),
        "HUBSPOT_API_KEY": (secrets or {}).get("HUBSPOT_API_KEY", ""),
    }
    return subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", configuration_script()],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )


def test_scheduled_run_skips_when_required_secrets_are_missing(tmp_path: Path) -> None:
    result = run_configuration(tmp_path, "schedule")

    assert result.returncode == 0
    assert "::warning::" in result.stdout
    assert "::error::" not in result.stdout
    assert "configured=false" in (tmp_path / "output").read_text()
    summary = (tmp_path / "summary").read_text()
    assert "ANTHROPIC_API_KEY" in summary
    assert "HUBSPOT_API_KEY" in summary


def test_manual_run_fails_when_required_secrets_are_missing(tmp_path: Path) -> None:
    result = run_configuration(tmp_path, "workflow_dispatch")

    assert result.returncode == 1
    assert "Configurer les secrets Actions" in result.stdout


def test_configured_run_continues_past_configuration_check(tmp_path: Path) -> None:
    result = run_configuration(
        tmp_path,
        "schedule",
        {"ANTHROPIC_API_KEY": "test", "HUBSPOT_API_KEY": "test"},
    )

    assert result.returncode == 0
    assert "configured=true" in (tmp_path / "output").read_text()
    assert (
        WORKFLOW.read_text().count(
            "if: steps.configuration.outputs.configured == 'true' "
            "&& inputs.configuration_only != true"
        )
        == 6
    )
