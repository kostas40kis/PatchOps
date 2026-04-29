from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchops.llm_browser import commands


def _html_with_bundle(filename: str = "patch_d0_23_browser_runner_integration_cli_dry_mode_patchops_bundle.zip") -> str:
    return f"""
    <article data-message-author-role="assistant">
      <a href="/downloads/{filename}?download=1">{filename}</a>
    </article>
    <textarea id="prompt-textarea"></textarea>
    """


def test_run_once_help_exposes_dry_run_mode_without_auto_send(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["run-once", "--help"])

    out = capsys.readouterr().out

    assert exc.value.code == 0
    assert "run-once" in out
    assert "--dry-run" in out
    assert "--snapshot-file" in out
    assert "--snapshot-html" in out
    assert "--auto-send" not in out
    assert "--allow-send" not in out


def test_llm_browser_parser_includes_run_once_command(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["--help"])

    out = capsys.readouterr().out

    assert exc.value.code == 0
    assert "doctor" in out
    assert "open" in out
    assert "dry-run" in out
    assert "run-once" in out


def test_run_once_live_mode_is_rejected(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(["run-once"])

    out = capsys.readouterr().out

    assert code == 2
    assert "live mode is not enabled" in out


def test_run_once_dry_run_requires_snapshot(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(["run-once", "--dry-run"])

    out = capsys.readouterr().out

    assert code == 2
    assert "requires --snapshot-file or --snapshot-html" in out


def test_run_once_dry_run_json_from_snapshot_html_stops_before_download(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(
        [
            "run-once",
            "--dry-run",
            "--snapshot-html",
            _html_with_bundle(),
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["ok"] is False
    assert payload["blocked"] is False
    assert payload["options"]["dry_run_only"] is True
    assert payload["options"]["safety"]["side_effects_enabled"] is False
    assert payload["dry_run"]["snapshot"]["state"] == "DOWNLOADING"
    assert "would_click_download_candidate_and_wait_for_stable_file" in payload["dry_run"]["planned_actions"]
    assert payload["side_effects_performed"] == []
    assert payload["dry_run"]["side_effects_performed"] == []


def test_run_once_dry_run_text_output_lists_integration_actions(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(
        [
            "run-once",
            "--dry-run",
            "--snapshot-html",
            _html_with_bundle(),
        ]
    )

    out = capsys.readouterr().out

    assert code == 0
    assert "PatchOps browser-runner summary:" in out
    assert "Integration planned actions:" in out
    assert "would_click_download_candidate_and_wait_for_stable_file" in out
    assert "Integration side effects performed: none" in out


def test_run_once_dry_run_strict_returns_nonzero_when_blocked(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(
        [
            "run-once",
            "--dry-run",
            "--snapshot-html",
            '<article data-message-author-role="assistant">no artifact</article><textarea></textarea>',
            "--json",
            "--strict",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert code == 1
    assert payload["blocked"] is True
    assert payload["dry_run"]["snapshot"]["state"] == "BLOCKED_ARTIFACT_MISSING"


def test_run_once_dry_run_blocks_side_effect_flags(capsys: pytest.CaptureFixture[str]) -> None:
    code = commands.main(
        [
            "run-once",
            "--dry-run",
            "--snapshot-html",
            _html_with_bundle(),
            "--allow-download-click",
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["blocked"] is True
    assert payload["blocked_reason"] == "dry_run_only_disallows_side_effects"
    assert payload["side_effects_performed"] == []


def test_run_once_dry_run_respects_processed_artifact(capsys: pytest.CaptureFixture[str]) -> None:
    filename = "patch_d0_23_browser_runner_integration_cli_dry_mode_patchops_bundle.zip"
    code = commands.main(
        [
            "run-once",
            "--dry-run",
            "--snapshot-html",
            _html_with_bundle(filename),
            "--processed-artifact",
            filename,
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["blocked"] is True
    assert payload["dry_run"]["artifact_detection"]["reason"] == "artifact_already_processed"


def test_run_once_dry_run_snapshot_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    snapshot = tmp_path / "snapshot.html"
    snapshot.write_text(_html_with_bundle(), encoding="utf-8")

    code = commands.main(
        [
            "run-once",
            "--dry-run",
            "--snapshot-file",
            str(snapshot),
            "--browser",
            "opera",
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["options"]["browser"] == "opera"
    assert payload["dry_run"]["snapshot"]["browser"] == "opera"
