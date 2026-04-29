from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchops.llm_browser import commands
from patchops.llm_browser.dry_mode_checkpoint import (
    build_commit_hint,
    evaluate_dry_mode_checkpoint,
    read_git_checkpoint,
    render_checkpoint_report,
)


ROOT = Path(__file__).resolve().parents[1]


def _fake_dirty_git(args, cwd: Path, timeout_seconds: int):
    assert tuple(args) == ("git", "status", "--short", "--branch")
    assert cwd == ROOT
    assert timeout_seconds == 120
    return 0, "## main...origin/main\n M patchops/llm_browser/commands.py\n?? new_file.py\n", ""


def _fake_clean_git(args, cwd: Path, timeout_seconds: int):
    return 0, "## main...origin/main\n", ""


def _fake_git_missing(args, cwd: Path, timeout_seconds: int):
    raise FileNotFoundError("git not found")


def test_read_git_checkpoint_detects_dirty_status() -> None:
    git = read_git_checkpoint(ROOT, run_command=_fake_dirty_git)

    assert git.available is True
    assert git.exit_code == 0
    assert git.dirty is True
    assert "commands.py" in git.status_text


def test_read_git_checkpoint_detects_clean_status() -> None:
    git = read_git_checkpoint(ROOT, run_command=_fake_clean_git)

    assert git.available is True
    assert git.dirty is False


def test_read_git_checkpoint_handles_missing_git() -> None:
    git = read_git_checkpoint(ROOT, run_command=_fake_git_missing)

    assert git.available is False
    assert git.exit_code is None
    assert git.dirty is False
    assert "git not found" in git.stderr


def test_build_commit_hint_sanitizes_quotes() -> None:
    assert build_commit_hint(commit_message='D0.29 "quoted" message') == "git add -A; git commit -m \"D0.29 'quoted' message\""


def test_checkpoint_report_passes_and_recommends_commit_when_dirty() -> None:
    report = evaluate_dry_mode_checkpoint(
        repo_root=ROOT,
        run_command=_fake_dirty_git,
        commit_message="D0.29 checkpoint browser runner dry mode",
    )

    assert report.ok is True
    assert report.status == "PASS"
    assert report.exit_code == 0
    assert report.release_gate.ok is True
    assert report.git.dirty is True
    assert report.commit_recommended is True
    assert report.commit_hint == 'git add -A; git commit -m "D0.29 checkpoint browser runner dry mode"'
    assert any("pytest -q" in command for command in report.broad_validation_commands)


def test_checkpoint_report_handles_clean_repo() -> None:
    report = evaluate_dry_mode_checkpoint(
        repo_root=ROOT,
        run_command=_fake_clean_git,
    )

    assert report.ok is True
    assert report.commit_recommended is False
    assert any("clean" in note for note in report.notes)


def test_render_checkpoint_report_is_operator_readable() -> None:
    report = evaluate_dry_mode_checkpoint(
        repo_root=ROOT,
        run_command=_fake_dirty_git,
    )

    text = render_checkpoint_report(report)

    assert "Checkpoint: llm_browser_commit_broad_validation_checkpoint" in text
    assert "Status    : PASS" in text
    assert "Release gate:" in text
    assert "Commit recommended: true" in text
    assert "git add -A; git commit -m" in text
    assert "Broad validation commands:" in text
    assert "py -m pytest -q" in text


def test_checkpoint_help_has_no_mutating_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["checkpoint", "--help"])

    out = capsys.readouterr().out

    assert exc.value.code == 0
    assert "checkpoint" in out
    assert "--repo-root" in out
    assert "--commit-message" in out
    assert "--json" in out
    assert "--commit " not in out
    assert "--push" not in out
    assert "--run-tests" not in out
    assert "--auto-send" not in out
    assert "--live" not in out


def test_llm_browser_help_includes_checkpoint(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["--help"])

    out = capsys.readouterr().out

    assert exc.value.code == 0
    assert "checkpoint" in out
    assert "release-gate" in out
    assert "audit-log" in out


def test_checkpoint_cli_json_passes(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(["checkpoint", "--repo-root", str(ROOT), "--json"])

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["name"] == "llm_browser_commit_broad_validation_checkpoint"
    assert payload["status"] == "PASS"
    assert payload["release_gate"]["status"] == "PASS"
    assert "git add -A; git commit -m" in payload["commit_hint"]
    assert any("pytest -q" in command for command in payload["broad_validation_commands"])


def test_checkpoint_cli_text_passes(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(["checkpoint", "--repo-root", str(ROOT)])

    out = capsys.readouterr().out

    assert code == 0
    assert "Checkpoint: llm_browser_commit_broad_validation_checkpoint" in out
    assert "Status    : PASS" in out
