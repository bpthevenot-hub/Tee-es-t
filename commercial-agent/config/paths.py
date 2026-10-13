"""Filesystem locations used by the commercial agent.

Every file the agent reads or writes is resolved here, against the project
root rather than the current working directory. `main.py`, `autonomous.py`,
`update_status.py`, `setup_gmail.py` and the tests therefore agree on where
things live whichever directory they are launched from.

Runtime outputs (``agent.log``, ``reports/``, ``livrables/``) default to the
project root — the layout used by GitHub Actions, Docker and Railway — and can
be moved elsewhere with ``AGENT_DATA_DIR``, e.g. to keep a cloud checkout clean.

Overrides (relative values are resolved from the project root):

- ``AGENT_DATA_DIR``          agent.log, reports/, livrables/
- ``AGENT_STATUS_FILE``       website status JSON (default ``../docs/status.json``)
- ``GMAIL_TOKEN_PATH``        authorized Gmail token (default ``config/gmail_token.json``)
- ``GMAIL_CREDENTIALS_PATH``  Gmail OAuth client (default ``config/gmail_credentials.json``)

Kept dependency-free, and every value is read at call time, so settings loaded
from ``.env`` or set by tests are honoured.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _path_from_env(name: str) -> Path | None:
    """Return the path stored in env var ``name``, or None when unset/blank."""
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    path = Path(raw).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


def data_dir() -> Path:
    """Base directory for runtime outputs."""
    return _path_from_env("AGENT_DATA_DIR") or PROJECT_ROOT


def log_file() -> Path:
    """Routine log written by autonomous.py and parsed by update_status.py."""
    return data_dir() / "agent.log"


def reports_dir() -> Path:
    """One text report per autonomous routine run."""
    return data_dir() / "reports"


def livrables_dir() -> Path:
    """Generated quotes and proposals (HTML + JSON metadata)."""
    return data_dir() / "livrables"


def status_file() -> Path:
    """Website status JSON written by update_status.py.

    Defaults to ``../docs/status.json``: the site root of the Tee-es-t monorepo,
    which runs this code from its ``commercial-agent/`` folder and publishes
    that file. A standalone checkout sets AGENT_STATUS_FILE (e.g. docs/status.json).
    """
    return _path_from_env("AGENT_STATUS_FILE") or PROJECT_ROOT.parent / "docs" / "status.json"


def gmail_token_path() -> Path:
    """Authorized-user Gmail token created by setup_gmail.py."""
    return _path_from_env("GMAIL_TOKEN_PATH") or PROJECT_ROOT / "config" / "gmail_token.json"


def gmail_credentials_path() -> Path:
    """Gmail OAuth client file downloaded from Google Cloud Console."""
    return (
        _path_from_env("GMAIL_CREDENTIALS_PATH")
        or PROJECT_ROOT / "config" / "gmail_credentials.json"
    )
