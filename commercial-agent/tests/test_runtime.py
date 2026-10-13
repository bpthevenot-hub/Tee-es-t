"""Regression tests for running the agent outside its own directory.

Covers the problems surfaced by the cloud environment setup:

- files resolved from the working directory (Gmail token, agent.log, reports)
  instead of the project, so interactive and autonomous runs disagreed;
- the Gmail browser consent flow starting in unattended runs and blocking;
- GH_TOKEN being ignored when GITHUB_TOKEN is unset;
- routine failures exiting 0.

No network access: Google, GitHub and Anthropic are never called.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from config import paths

ROOT = paths.PROJECT_ROOT
PATH_VARS = ("AGENT_DATA_DIR", "AGENT_STATUS_FILE", "GMAIL_TOKEN_PATH", "GMAIL_CREDENTIALS_PATH")
SECRET_VARS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "HUBSPOT_API_KEY",
    "NOTION_API_KEY",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "GMAIL_TOKEN_JSON",
    "GMAIL_CREDENTIALS_JSON",
)
VALID_TOKEN = {
    "token": "access-token",
    "refresh_token": "refresh-token",
    "client_id": "client-id",
    "client_secret": "client-secret",
    "expiry": "2999-01-01T00:00:00Z",
}
CLIENT_CONFIG = {"installed": {"client_id": "client-id", "client_secret": "client-secret"}}


@pytest.fixture
def clean_env(monkeypatch):
    for name in PATH_VARS + SECRET_VARS + ("CI",):
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def run_python(args: list[str], cwd: Path, **env_extra: str) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k not in PATH_VARS + SECRET_VARS}
    env.update(env_extra, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=120
    )


# --- config.paths ------------------------------------------------------------


def test_defaults_are_anchored_on_project_not_cwd(clean_env, tmp_path):
    clean_env.chdir(tmp_path)
    assert paths.log_file() == ROOT / "agent.log"
    assert paths.reports_dir() == ROOT / "reports"
    assert paths.livrables_dir() == ROOT / "livrables"
    assert paths.gmail_token_path() == ROOT / "config" / "gmail_token.json"
    assert paths.gmail_credentials_path() == ROOT / "config" / "gmail_credentials.json"


def test_status_file_keeps_monorepo_site_root_by_default(clean_env, tmp_path):
    # Tee-es-t runs this code from commercial-agent/ and publishes <repo>/docs/status.json.
    clean_env.chdir(tmp_path)
    assert paths.status_file() == ROOT.parent / "docs" / "status.json"


def test_agent_data_dir_moves_runtime_outputs_only(clean_env, tmp_path):
    clean_env.setenv("AGENT_DATA_DIR", str(tmp_path))
    assert paths.log_file() == tmp_path / "agent.log"
    assert paths.reports_dir() == tmp_path / "reports"
    assert paths.livrables_dir() == tmp_path / "livrables"
    assert paths.gmail_token_path() == ROOT / "config" / "gmail_token.json"
    assert paths.status_file() == ROOT.parent / "docs" / "status.json"


def test_relative_overrides_resolve_from_project_root(clean_env, tmp_path):
    clean_env.chdir(tmp_path)
    clean_env.setenv("GMAIL_CREDENTIALS_PATH", "./config/gmail_credentials.json")
    clean_env.setenv("AGENT_STATUS_FILE", "docs/status.json")  # standalone checkout
    assert paths.gmail_credentials_path() == ROOT / "config" / "gmail_credentials.json"
    assert paths.status_file() == ROOT / "docs" / "status.json"


def test_blank_override_falls_back_to_default(clean_env):
    clean_env.setenv("AGENT_DATA_DIR", "   ")
    assert paths.data_dir() == ROOT


# --- entry points agree on files, whatever the working directory ------------


@pytest.mark.parametrize("anthropic_log", ["", "info"])
def test_unknown_routine_fails_and_writes_only_to_data_dir(anthropic_log, tmp_path):
    # ANTHROPIC_LOG makes the SDK install a root handler at import; agent.log
    # must still be written, since update_status.py parses it.
    launch_dir = tmp_path / "launch"
    data_dir = tmp_path / "data"
    launch_dir.mkdir()

    proc = run_python(
        [str(ROOT / "autonomous.py"), "no_such_routine"],
        cwd=launch_dir,
        AGENT_DATA_DIR=str(data_dir),
        ANTHROPIC_LOG=anthropic_log,
    )

    assert proc.returncode == 1, proc.stderr
    reports = list((data_dir / "reports").glob("no_such_routine_*.txt"))
    assert len(reports) == 1
    assert "unknown routine" in reports[0].read_text(encoding="utf-8")
    assert "Unknown routine" in (data_dir / "agent.log").read_text(encoding="utf-8")
    assert list(launch_dir.iterdir()) == []


def test_update_status_reads_where_autonomous_writes(tmp_path):
    data_dir = tmp_path / "data"
    code = (
        "import update_status as u; "
        "print(u.LOG_FILE); print(u.LIVRABLES_DIR); print(u.STATUS_FILE)"
    )

    proc = run_python(
        ["-c", code], cwd=tmp_path, AGENT_DATA_DIR=str(data_dir), PYTHONPATH=str(ROOT)
    )

    assert proc.returncode == 0, proc.stderr
    log_file, livrables_dir, status_file = proc.stdout.splitlines()[-3:]
    assert Path(log_file) == data_dir / "agent.log"
    assert Path(livrables_dir) == data_dir / "livrables"
    assert Path(status_file) == ROOT.parent / "docs" / "status.json"


def test_livrables_follow_agent_data_dir(tmp_path):
    data_dir = tmp_path / "data"
    devis = {
        "client_name": "Client Test",
        "client_email": "client@example.com",
        "objet": "Audit IA",
        "lignes": [{"description": "Audit", "quantite": 1, "prix_unitaire": 100}],
    }
    code = (
        "import json, sys; from tools import execute_tool; "
        "print(json.loads(execute_tool('livrables_create_devis', json.loads(sys.argv[1])))['path'])"
    )

    proc = run_python(
        ["-c", code, json.dumps(devis)],
        cwd=tmp_path,
        AGENT_DATA_DIR=str(data_dir),
        PYTHONPATH=str(ROOT),
    )

    assert proc.returncode == 0, proc.stderr
    created = Path(proc.stdout.strip().splitlines()[-1])
    assert created.parent == data_dir / "livrables"
    assert created.exists()


# --- autonomous.py exit codes (same contract as the Tee-es-t robot) ----------


@pytest.mark.parametrize(
    ("result", "expected_code"),
    [
        ("Routine completed", 0),
        ("API Error (auth): invalid key", 1),
        ("API Error (bad request): invalid model", 1),
        ("API Error: rate limit", 1),
        ("Error: unknown routine 'invalid'", 1),
        ("Agent stopped: maximum iterations reached.", 1),
    ],
)
def test_exit_code_reflects_result_and_report_is_kept(result, expected_code, clean_env, tmp_path):
    import autonomous

    clean_env.setenv("AGENT_DATA_DIR", str(tmp_path))
    clean_env.setattr("sys.argv", ["autonomous.py", "followup"])
    clean_env.setattr(autonomous, "run_autonomous", lambda routine: result)
    # Real logging setup replaces root handlers; it is covered by the subprocess test.
    clean_env.setattr(autonomous, "_configure_logging", lambda: None)

    assert autonomous.main() == expected_code
    reports = list((tmp_path / "reports").glob("followup_*.txt"))
    assert len(reports) == 1
    assert result in reports[0].read_text(encoding="utf-8")


def test_missing_api_key_becomes_a_failed_result(clean_env):
    import anthropic

    from agent_loop import run_agent_loop

    # Closed local port: nothing leaves the machine even if credentials were found.
    client = anthropic.Anthropic(base_url="http://127.0.0.1:9", max_retries=0)
    result = run_agent_loop(
        user_prompt="hello",
        system_prompt="system",
        tools=[],
        execute_tool=lambda name, data: "",
        client=client,
    )

    assert result.startswith("API Error")


# --- GitHub token -------------------------------------------------------------


def test_github_falls_back_to_gh_token(clean_env):
    from tools import github_tools

    clean_env.setenv("GH_TOKEN", "gh-token")
    assert github_tools._headers()["Authorization"] == "Bearer gh-token"


def test_github_token_wins_over_gh_token(clean_env):
    from tools import github_tools

    clean_env.setenv("GITHUB_TOKEN", "primary")
    clean_env.setenv("GH_TOKEN", "secondary")
    assert github_tools._headers()["Authorization"] == "Bearer primary"


def test_missing_github_token_names_both_variables(clean_env):
    from tools import github_tools
    from tools.http_utils import AuthError

    with pytest.raises(AuthError, match="GITHUB_TOKEN or GH_TOKEN"):
        github_tools._headers()


# --- Gmail: never block an unattended run --------------------------------------


@pytest.fixture
def gmail(clean_env, tmp_path):
    from tools import gmail as gmail_module

    if not gmail_module.GMAIL_AVAILABLE:
        pytest.skip("Google client libraries not installed")

    def no_browser(*args, **kwargs):
        raise AssertionError("the browser consent flow must not start in unattended runs")

    clean_env.setattr(gmail_module, "_service", None)
    clean_env.setattr(gmail_module, "_is_interactive", lambda: False)
    clean_env.setattr(gmail_module.InstalledAppFlow, "from_client_secrets_file", no_browser)
    clean_env.setattr(gmail_module.InstalledAppFlow, "from_client_config", no_browser)
    clean_env.setenv("GMAIL_TOKEN_PATH", str(tmp_path / "token.json"))
    clean_env.setenv("GMAIL_CREDENTIALS_PATH", str(tmp_path / "credentials.json"))
    return gmail_module


def test_unattended_run_without_token_errors_instead_of_waiting(gmail, clean_env, tmp_path):
    clean_env.setenv("GMAIL_CREDENTIALS_JSON", json.dumps(CLIENT_CONFIG))

    result = gmail.execute_gmail_tool("gmail_search_messages", {"query": "is:unread"})

    assert result.startswith("Error executing gmail_search_messages")
    assert "setup_gmail.py" in result
    assert not (tmp_path / "credentials.json").exists()  # client secret not copied to disk


def test_placeholder_token_json_is_reported_clearly(gmail, clean_env):
    clean_env.setenv("GMAIL_TOKEN_JSON", "proxy-placeholder-not-json")

    result = gmail.execute_gmail_tool("gmail_search_messages", {"query": "is:unread"})

    assert "GMAIL_TOKEN_JSON: not valid JSON" in result


def test_corrupt_token_file_is_reported_clearly(gmail, clean_env, tmp_path):
    (tmp_path / "token.json").write_text('{"token": "trunc')

    result = gmail.execute_gmail_tool("gmail_search_messages", {"query": "is:unread"})

    assert "unreadable token" in result
    assert "setup_gmail.py" in result


def test_revoked_token_is_reported_clearly(gmail, clean_env, tmp_path):
    expired = {**VALID_TOKEN, "expiry": "2000-01-01T00:00:00Z"}
    (tmp_path / "token.json").write_text(json.dumps(expired))

    def revoked(self, request):
        raise gmail.RefreshError("invalid_grant: Token has been expired or revoked.")

    clean_env.setattr(gmail.Credentials, "refresh", revoked)

    result = gmail.execute_gmail_tool("gmail_search_messages", {"query": "is:unread"})

    assert "refresh failed (invalid_grant" in result


def test_revoked_env_token_falls_back_to_valid_file(gmail, clean_env, tmp_path):
    # A valid-syntax GMAIL_TOKEN_JSON whose refresh is revoked must not shadow a
    # good token file (e.g. one just re-created by setup_gmail.py).
    stale = {**VALID_TOKEN, "expiry": "2000-01-01T00:00:00Z"}
    clean_env.setenv("GMAIL_TOKEN_JSON", json.dumps(stale))
    (tmp_path / "token.json").write_text(json.dumps(VALID_TOKEN))

    def revoked(self, request):
        raise gmail.RefreshError("invalid_grant: Token has been expired or revoked.")

    # Only the stale env token is expired and hits refresh; the file is valid.
    clean_env.setattr(gmail.Credentials, "refresh", revoked)
    service = object()
    clean_env.setattr(gmail, "build", lambda *args, **kwargs: service)

    assert gmail._get_gmail_service() is service


def test_transport_error_env_token_falls_back_to_valid_file(gmail, clean_env, tmp_path):
    # A network failure (not an OAuth RefreshError) refreshing GMAIL_TOKEN_JSON
    # must still fall through to a valid token file rather than escape the loop.
    from google.auth.exceptions import TransportError

    stale = {**VALID_TOKEN, "expiry": "2000-01-01T00:00:00Z"}
    clean_env.setenv("GMAIL_TOKEN_JSON", json.dumps(stale))
    (tmp_path / "token.json").write_text(json.dumps(VALID_TOKEN))

    def transport_fail(self, request):
        raise TransportError("Failed to resolve 'oauth2.googleapis.com'")

    clean_env.setattr(gmail.Credentials, "refresh", transport_fail)
    service = object()
    clean_env.setattr(gmail, "build", lambda *args, **kwargs: service)

    assert gmail._get_gmail_service() is service


def test_refreshed_token_survives_read_only_disk(gmail, clean_env, tmp_path):
    from datetime import datetime

    expired = {**VALID_TOKEN, "expiry": "2000-01-01T00:00:00Z"}
    (tmp_path / "token.json").write_text(json.dumps(expired))

    def refreshed(self, request):
        self.token = "new-access-token"
        self.expiry = datetime(2999, 1, 1)

    def read_only(path, content):
        raise OSError(30, "Read-only file system")

    service = object()
    clean_env.setattr(gmail.Credentials, "refresh", refreshed)
    clean_env.setattr(gmail, "_write_private", read_only)
    clean_env.setattr(gmail, "build", lambda *args, **kwargs: service)

    assert gmail._get_gmail_service() is service


def test_placeholder_token_json_falls_back_to_token_file(gmail, clean_env, tmp_path):
    clean_env.setenv("GMAIL_TOKEN_JSON", "proxy-placeholder-not-json")
    (tmp_path / "token.json").write_text(json.dumps(VALID_TOKEN))
    service = object()
    clean_env.setattr(gmail, "build", lambda *args, **kwargs: service)

    assert gmail._get_gmail_service() is service


def test_token_file_is_found_from_another_directory(gmail, clean_env, tmp_path):
    (tmp_path / "token.json").write_text(json.dumps(VALID_TOKEN))
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    clean_env.chdir(elsewhere)
    service = object()
    clean_env.setattr(gmail, "build", lambda *args, **kwargs: service)

    assert gmail._get_gmail_service() is service
    assert list(elsewhere.iterdir()) == []


def test_env_token_is_not_copied_to_disk(gmail, clean_env, tmp_path):
    clean_env.setenv("GMAIL_TOKEN_JSON", json.dumps(VALID_TOKEN))
    service = object()
    clean_env.setattr(gmail, "build", lambda *args, **kwargs: service)

    assert gmail._get_gmail_service() is service
    assert not (tmp_path / "token.json").exists()


def test_interactive_terminal_keeps_browser_consent(gmail, clean_env, tmp_path):
    class FakeCreds:
        valid = True

        def to_json(self) -> str:
            return '{"token": "fresh"}'

    class FakeFlow:
        def run_local_server(self, port: int, timeout_seconds: int | None = None) -> FakeCreds:
            assert timeout_seconds, "consent wait must be bounded"
            return FakeCreds()

    (tmp_path / "credentials.json").write_text(json.dumps(CLIENT_CONFIG))
    clean_env.setattr(gmail, "_is_interactive", lambda: True)
    clean_env.setattr(
        gmail.InstalledAppFlow, "from_client_secrets_file", lambda *a, **k: FakeFlow()
    )
    clean_env.setattr(gmail, "build", lambda *args, **kwargs: "service")

    assert gmail._get_gmail_service() == "service"
    token_file = tmp_path / "token.json"
    assert token_file.read_text() == '{"token": "fresh"}'
    assert token_file.stat().st_mode & 0o777 == 0o600


def test_ci_is_never_interactive(clean_env):
    from tools import gmail as gmail_module

    clean_env.setenv("CI", "true")
    assert gmail_module._is_interactive() is False
