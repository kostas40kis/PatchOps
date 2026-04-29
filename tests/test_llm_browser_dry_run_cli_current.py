from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchops.llm_browser import commands


def _html_with_bundle(filename: str = "patch_d0_21_dry_run_cli_command_patchops_bundle.zip") -> str:
    return f"""
    <article data-message-author-role="assistant">
      <a href="/downloads/{filename}?download=1">{filename}</a>
    </article>
    <textarea id="prompt-textarea"></textarea>
    """


def test_dry_run_help_lists_command_without_auto_send(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["dry-run", "--help"])

    out = capsys.readouterr().out
    assert exc.value.code == 0
    assert "dry-run" in out
    assert "--snapshot-file" in out
    assert "--snapshot-html" in out
    assert "--runner-status" in out
    assert "--auto-send" not in out


def test_llm_browser_parser_includes_dry_run_command(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["--help"])

    out = capsys.readouterr().out
    assert exc.value.code == 0
    assert "doctor" in out
    assert "open" in out
    assert "dry-run" in out


def test_dry_run_json_blocks_when_no_artifact(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(
        [
            "dry-run",
            "--snapshot-html",
            '<article data-message-author-role="assistant">no zip here</article><textarea></textarea>',
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["blocked"] is True
    assert payload["snapshot"]["state"] == "BLOCKED_ARTIFACT_MISSING"
    assert payload["artifact_detection"]["reason"] == "no_patchops_bundle_candidates"
    assert payload["side_effects_performed"] == []


def test_dry_run_strict_returns_nonzero_when_blocked(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(
        [
            "dry-run",
            "--snapshot-html",
            '<article data-message-author-role="assistant">no zip here</article><textarea></textarea>',
            "--json",
            "--strict",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert code == 1
    assert payload["blocked"] is True


def test_dry_run_text_output_lists_planned_actions(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(
        [
            "dry-run",
            "--snapshot-html",
            _html_with_bundle(),
        ]
    )

    out = capsys.readouterr().out

    assert code == 0
    assert "PatchOps browser-runner summary:" in out
    assert "Planned actions:" in out
    assert "would_click_download_candidate_and_wait_for_stable_file" in out
    assert "Side effects performed: none" in out


def test_dry_run_json_reaches_summary_ready_with_supplied_facts(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    snapshot_file = tmp_path / "snapshot.html"
    snapshot_file.write_text(_html_with_bundle(), encoding="utf-8")
    report = tmp_path / "patchops_run_package_20260429_193000.txt"
    report.write_text(
        "Result : PASS\nExitCode : 0\nPatch : D0.21 dry-run CLI command\n",
        encoding="utf-8",
    )
    downloaded = tmp_path / "patch_d0_21_dry_run_cli_command_patchops_bundle.zip"

    code = commands.main(
        [
            "dry-run",
            "--snapshot-file",
            str(snapshot_file),
            "--downloaded-path",
            str(downloaded),
            "--runner-status",
            "pass",
            "--report-path",
            str(report),
            "--browser",
            "edge",
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["ok"] is True
    assert payload["blocked"] is False
    assert payload["snapshot"]["state"] == "SUMMARY_READY"
    assert payload["pasteback_summary"]["status"] == "PASS"
    assert "would_paste_summary_without_submit" in payload["planned_actions"]
    assert payload["side_effects_performed"] == []


def test_dry_run_json_missing_report_path_is_fail_closed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    downloaded = tmp_path / "patch_d0_21_dry_run_cli_command_patchops_bundle.zip"
    missing_report = tmp_path / "missing_report.txt"

    code = commands.main(
        [
            "dry-run",
            "--snapshot-html",
            _html_with_bundle(),
            "--downloaded-path",
            str(downloaded),
            "--runner-status",
            "pass",
            "--report-path",
            str(missing_report),
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["blocked"] is True
    assert payload["snapshot"]["state"] == "BLOCKED_REPORT_MISSING"
    assert payload["pasteback_summary"]["status"] == "FAIL"
    assert payload["pasteback_summary"]["next_action"] == "Stop and inspect why the canonical report was not found."


def test_dry_run_respects_processed_artifact(capsys: pytest.CaptureFixture[str]) -> None:
    filename = "patch_d0_21_dry_run_cli_command_patchops_bundle.zip"
    code = commands.main(
        [
            "dry-run",
            "--snapshot-html",
            _html_with_bundle(filename),
            "--processed-artifact",
            filename,
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["snapshot"]["state"] == "BLOCKED_ARTIFACT_MISSING"
    assert payload["artifact_detection"]["reason"] == "artifact_already_processed"
