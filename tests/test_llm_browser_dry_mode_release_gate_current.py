from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchops.llm_browser import commands
from patchops.llm_browser.dry_mode_release_gate import (
    evaluate_dry_mode_release_gate,
    render_release_gate_report,
)


ROOT = Path(__file__).resolve().parents[1]


def test_release_gate_report_passes_for_current_repo() -> None:
    report = evaluate_dry_mode_release_gate(
        repo_root=ROOT,
        cli_surface_names=commands.llm_browser_command_names(),
    )

    assert report.ok is True
    assert report.status == "PASS"
    assert report.exit_code == 0
    names = [check.name for check in report.checks]
    assert "passive_modules_import" in names
    assert "safety_policy_rejects_auto_send_and_dry_side_effects" in names
    assert "audit_metadata_json_arrays" in names
    assert "dry_run_blocks_without_side_effects" in names
    assert "dry_mode_docs_contract" in names
    assert "cli_surface_contract" in names


def test_release_gate_report_fails_when_cli_surface_is_missing() -> None:
    report = evaluate_dry_mode_release_gate(
        repo_root=ROOT,
        cli_surface_names=("doctor", "open", "dry-run"),
    )

    assert report.ok is False
    assert report.exit_code == 1
    failed = [check for check in report.checks if not check.ok]
    assert any(check.name == "cli_surface_contract" for check in failed)


def test_release_gate_report_fails_when_docs_are_missing(tmp_path: Path) -> None:
    report = evaluate_dry_mode_release_gate(
        repo_root=tmp_path,
        cli_surface_names=commands.llm_browser_command_names(),
    )

    assert report.ok is False
    failed = [check for check in report.checks if not check.ok]
    assert any(check.name == "dry_mode_docs_exist" for check in failed)


def test_render_release_gate_report_is_compact() -> None:
    report = evaluate_dry_mode_release_gate(
        repo_root=ROOT,
        cli_surface_names=commands.llm_browser_command_names(),
    )

    text = render_release_gate_report(report)

    assert "Release gate: llm_browser_dry_mode_release_gate" in text
    assert "Status      : PASS" in text
    assert "Checks:" in text
    assert "PASS passive_modules_import" in text


def test_release_gate_help_has_no_live_or_send_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["release-gate", "--help"])

    out = capsys.readouterr().out

    assert exc.value.code == 0
    assert "release-gate" in out
    assert "--repo-root" in out
    assert "--json" in out
    assert "--auto-send" not in out
    assert "--allow-send" not in out
    assert "--live" not in out


def test_llm_browser_help_includes_release_gate(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["--help"])

    out = capsys.readouterr().out

    assert exc.value.code == 0
    assert "release-gate" in out
    assert "dry-run" in out
    assert "audit-log" in out


def test_release_gate_cli_json_passes(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(["release-gate", "--repo-root", str(ROOT), "--json"])

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["name"] == "llm_browser_dry_mode_release_gate"
    assert payload["status"] == "PASS"
    assert payload["exit_code"] == 0
    assert all(check["status"] == "PASS" for check in payload["checks"])


def test_release_gate_cli_text_passes(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(["release-gate", "--repo-root", str(ROOT)])

    out = capsys.readouterr().out

    assert code == 0
    assert "Release gate: llm_browser_dry_mode_release_gate" in out
    assert "Status      : PASS" in out
