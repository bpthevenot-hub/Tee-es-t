"""Exercise robot failures and publication against local Git repositories."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

PUBLISHER = Path(__file__).resolve().parents[1] / "publish_status.sh"
CONFIG_CHECK = Path(__file__).resolve().parents[1] / "check_config.sh"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


@pytest.fixture
def git_repos(tmp_path: Path) -> tuple[Path, Path, Path]:
    remote = tmp_path / "remote.git"
    robot = tmp_path / "robot"
    writer = tmp_path / "writer"
    git(tmp_path, "init", "--bare", "--initial-branch=main", str(remote))
    git(tmp_path, "clone", str(remote), str(robot))
    git(robot, "config", "user.name", "Test writer")
    git(robot, "config", "user.email", "test@example.com")
    (robot / "docs").mkdir()
    (robot / "docs/status.json").write_text('{"run": 0}\n')
    (robot / "README.md").write_text("Initial content\n")
    git(robot, "add", ".")
    git(robot, "commit", "-m", "Initial state")
    git(robot, "push", "origin", "main")
    git(tmp_path, "clone", str(remote), str(writer))
    git(writer, "config", "user.name", "Other writer")
    git(writer, "config", "user.email", "writer@example.com")
    return remote, robot, writer


def publish(robot: Path, **env: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(PUBLISHER), "followup"],
        cwd=robot,
        env={**os.environ, **env},
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_publish_status_without_optional_missions(git_repos):
    remote, robot, _ = git_repos
    (robot / "docs/status.json").write_text('{"run": 1}\n')
    result = publish(robot)
    assert result.returncode == 0, result.stderr
    assert json.loads(git(remote, "show", "main:docs/status.json")) == {"run": 1}


def test_publish_no_changes_does_not_create_commit(git_repos):
    remote, robot, _ = git_repos
    before = git(remote, "rev-parse", "main")
    assert publish(robot).returncode == 0
    assert git(remote, "rev-parse", "main") == before


def test_publish_includes_generated_mission(git_repos):
    remote, robot, _ = git_repos
    missions = robot / "docs/missions"
    missions.mkdir()
    (missions / "response.txt").write_text("Generated response\n")
    result = publish(robot)
    assert result.returncode == 0, result.stderr
    assert git(remote, "show", "main:docs/missions/response.txt") == "Generated response"


def test_publish_retries_transient_push_failure(git_repos, tmp_path):
    remote, robot, _ = git_repos
    real_git = shutil.which("git")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    marker = tmp_path / "rejected_once"
    wrapper = bin_dir / "git"
    wrapper.write_text(
        '#!/bin/sh\n'
        f'if [ "$1" = push ] && [ ! -e "{marker}" ]; then\n'
        f'  touch "{marker}"\n'
        '  exit 1\n'
        'fi\n'
        f'exec "{real_git}" "$@"\n'
    )
    wrapper.chmod(0o755)
    (robot / "docs/status.json").write_text('{"run": 1}\n')
    result = publish(robot, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    assert result.returncode == 0, result.stderr
    assert marker.exists()
    assert "nouvelle tentative (1/4)" in result.stdout
    assert json.loads(git(remote, "show", "main:docs/status.json")) == {"run": 1}


def test_publish_preserves_concurrent_unrelated_commit(git_repos):
    remote, robot, writer = git_repos
    (writer / "README.md").write_text("Other writer's change\n")
    git(writer, "commit", "-am", "Unrelated change")
    git(writer, "push", "origin", "main")
    (robot / "docs/status.json").write_text('{"run": 1}\n')
    result = publish(robot)
    assert result.returncode == 0, result.stderr
    assert git(remote, "show", "main:README.md") == "Other writer's change"
    assert json.loads(git(remote, "show", "main:docs/status.json")) == {"run": 1}


def test_publish_conflict_aborts_rebase_and_preserves_remote(git_repos):
    remote, robot, writer = git_repos
    (writer / "docs/status.json").write_text('{"run": "other"}\n')
    git(writer, "commit", "-am", "Competing status")
    git(writer, "push", "origin", "main")
    remote_head = git(remote, "rev-parse", "main")
    (robot / "docs/status.json").write_text('{"run": "robot"}\n')
    result = publish(robot)
    assert result.returncode == 1
    assert git(remote, "rev-parse", "main") == remote_head
    assert not (robot / ".git/rebase-merge").exists()
    assert not (robot / ".git/rebase-apply").exists()
    assert json.loads((robot / "docs/status.json").read_text()) == {"run": "robot"}


def test_publish_permission_denial_fails_without_force_push(git_repos, tmp_path):
    remote, robot, _ = git_repos
    remote_head = git(remote, "rev-parse", "main")
    hook = remote / "hooks/pre-receive"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    # Backoff timing is irrelevant to this permission failure regression.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    sleep = bin_dir / "sleep"
    sleep.write_text("#!/bin/sh\nexit 0\n")
    sleep.chmod(0o755)
    (robot / "docs/status.json").write_text('{"run": 1}\n')
    result = publish(robot, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    assert result.returncode == 1
    assert "apres 4 tentatives" in result.stdout
    assert git(remote, "rev-parse", "main") == remote_head


def check_config(tmp_path: Path, **env: str) -> tuple[subprocess.CompletedProcess[str], str, str]:
    output = tmp_path / "github_output"
    summary = tmp_path / "github_summary"
    result = subprocess.run(
        ["bash", str(CONFIG_CHECK)],
        cwd=tmp_path,
        env={
            "PATH": os.environ["PATH"],
            "GITHUB_OUTPUT": str(output),
            "GITHUB_STEP_SUMMARY": str(summary),
            "GITHUB_SERVER_URL": "https://github.com",
            "GITHUB_REPOSITORY": "owner/repo",
            **env,
        },
        capture_output=True,
        text=True,
        timeout=30,
    )
    return (
        result,
        output.read_text() if output.exists() else "",
        summary.read_text() if summary.exists() else "",
    )


def test_config_check_reports_ready_when_secrets_present(tmp_path):
    result, output, summary = check_config(
        tmp_path, ANTHROPIC_API_KEY="test-anthropic-value", HUBSPOT_API_KEY="test-hubspot-value"
    )
    assert result.returncode == 0, result.stderr
    assert "config_ready=true" in output
    assert "Configuration presente" in summary
    assert "::warning::" not in result.stdout
    # Secret values must never leak into logs, outputs or summaries.
    assert "test-anthropic-value" not in result.stdout + result.stderr + output + summary
    assert "test-hubspot-value" not in result.stdout + result.stderr + output + summary


def test_config_check_skips_gracefully_when_all_secrets_missing(tmp_path):
    result, output, summary = check_config(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "config_ready=false" in output
    assert "Robot suspendu" in summary
    assert "ANTHROPIC_API_KEY" in summary
    assert "HUBSPOT_API_KEY" in summary
    assert result.stdout.count("::warning::") == 2
    assert "::error::" not in result.stdout


def test_config_check_lists_only_the_missing_secret(tmp_path):
    result, output, summary = check_config(tmp_path, HUBSPOT_API_KEY="test-hubspot-value")
    assert result.returncode == 0, result.stderr
    assert "config_ready=false" in output
    assert result.stdout.count("::warning::") == 1
    assert "ANTHROPIC_API_KEY" in summary
    assert "- `HUBSPOT_API_KEY`" not in summary
    assert "test-hubspot-value" not in result.stdout + result.stderr + output + summary


def test_config_check_treats_blank_secret_as_missing(tmp_path):
    result, output, _ = check_config(
        tmp_path, ANTHROPIC_API_KEY="   ", HUBSPOT_API_KEY="test-hubspot-value"
    )
    assert result.returncode == 0, result.stderr
    assert "config_ready=false" in output
    assert result.stdout.count("::warning::") == 1
    assert "ANTHROPIC_API_KEY" in result.stdout


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
def test_robot_exit_code_preserves_report(result, expected_code, monkeypatch, tmp_path):
    import autonomous

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["autonomous.py", "followup"])
    monkeypatch.setattr(autonomous, "run_autonomous", lambda routine: result)
    assert autonomous.main() == expected_code
    reports = list((tmp_path / "reports").glob("followup_*.txt"))
    assert len(reports) == 1
    assert result in reports[0].read_text()
