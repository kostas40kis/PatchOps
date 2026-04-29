from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchops.llm_browser import commands


def _html_with_bundle(filename: str = "patch_d0_26_audit_log_readback_cli_patchops_bundle.zip") -> str:
    return f"""
    <article data-message-author-role="assistant">
      <a href="/downloads/{filename}?download=1">{filename}</a>
    </article>
    <textarea id="prompt-textarea"></textarea>
    """


def _write_events(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event_type": "dry_run_result",
                        "event_id": "one",
                        "timestamp": "2026-04-29T19:45:00+00:00",
                        "source": "unit",
                        "status": "FAIL",
                        "state": "BLOCKED_ARTIFACT_MISSING",
                        "reason": "no_patchops_bundle_candidates",
                        "metadata": {
                            "planned_actions": ["would_acquire_run_lock", "scan_latest_assistant_reply_for_patchops_bundle"],
                            "side_effects_performed": [],
                        },
                    }
                ),
                json.dumps(
                    {
                        "event_type": "integration_result",
                        "event_id": "two",
                        "timestamp": "2026-04-29T19:46:00+00:00",
                        "source": "unit",
                        "status": "UNKNOWN",
                        "state": "DOWNLOADING",
                        "artifact_filename": "patch_d0_26_audit_log_readback_cli_patchops_bundle.zip",
                        "metadata": {
                            "planned_actions": [
                                "would_acquire_run_lock",
                                "scan_latest_assistant_reply_for_patchops_bundle",
                                "would_click_download_candidate_and_wait_for_stable_file",
                            ],
                            "side_effects_performed": [],
                        },
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_audit_log_help_has_readback_options_without_mutating_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["audit-log", "--help"])

    out = capsys.readouterr().out

    assert exc.value.code == 0
    assert "--path" in out
    assert "--limit" in out
    assert "--event-type" in out
    assert "--status" in out
    assert "--json" in out
    assert "--auto-send" not in out
    assert "--delete" not in out
    assert "--clear" not in out


def test_llm_browser_parser_includes_audit_log_command(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["--help"])

    out = capsys.readouterr().out

    assert exc.value.code == 0
    assert "audit-log" in out
    assert "dry-run" in out
    assert "run-once" in out


def test_audit_log_json_readback_returns_events(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    audit_log = tmp_path / "audit.jsonl"
    _write_events(audit_log)

    code = commands.main(["audit-log", "--path", str(audit_log), "--json"])

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["path"] == str(audit_log)
    assert payload["exists"] is True
    assert payload["count"] == 2
    assert payload["events"][0]["event_type"] == "dry_run_result"
    assert payload["events"][1]["artifact_filename"] == "patch_d0_26_audit_log_readback_cli_patchops_bundle.zip"
    assert payload["events"][1]["metadata"]["planned_actions"][-1] == "would_click_download_candidate_and_wait_for_stable_file"


def test_audit_log_text_readback_is_compact(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    audit_log = tmp_path / "audit.jsonl"
    _write_events(audit_log)

    code = commands.main(["audit-log", "--path", str(audit_log), "--limit", "1"])

    out = capsys.readouterr().out

    assert code == 0
    assert f"Audit log: {audit_log}" in out
    assert "Events   : 1" in out
    assert "integration_result" in out
    assert "Artifact: patch_d0_26_audit_log_readback_cli_patchops_bundle.zip" in out
    assert "Side effects: none" in out
    assert "dry_run_result" not in out


def test_audit_log_filters_by_event_type_and_status(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    audit_log = tmp_path / "audit.jsonl"
    _write_events(audit_log)

    code = commands.main(
        [
            "audit-log",
            "--path",
            str(audit_log),
            "--event-type",
            "dry_run_result",
            "--status",
            "fail",
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["count"] == 1
    assert payload["events"][0]["event_id"] == "one"


def test_audit_log_limit_zero_returns_all_filtered_events(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    audit_log = tmp_path / "audit.jsonl"
    _write_events(audit_log)

    code = commands.main(["audit-log", "--path", str(audit_log), "--limit", "0", "--json"])

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["count"] == 2


def test_audit_log_missing_file_is_ok(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    audit_log = tmp_path / "missing.jsonl"

    code = commands.main(["audit-log", "--path", str(audit_log), "--json"])

    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["exists"] is False
    assert payload["count"] == 0
    assert payload["events"] == []


def test_audit_log_negative_limit_raises_clear_error(tmp_path: Path) -> None:
    audit_log = tmp_path / "audit.jsonl"
    _write_events(audit_log)

    with pytest.raises(ValueError, match="limit"):
        commands.main(["audit-log", "--path", str(audit_log), "--limit", "-1"])


def test_dry_run_audit_event_then_readback_roundtrip(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    audit_log = tmp_path / "audit.jsonl"

    dry_code = commands.main(
        [
            "dry-run",
            "--snapshot-html",
            _html_with_bundle(),
            "--audit-log",
            str(audit_log),
            "--json",
        ]
    )
    dry_payload = json.loads(capsys.readouterr().out)
    assert dry_code == 0
    assert dry_payload["snapshot"]["state"] == "DOWNLOADING"

    read_code = commands.main(["audit-log", "--path", str(audit_log), "--json"])
    read_payload = json.loads(capsys.readouterr().out)

    assert read_code == 0
    assert read_payload["count"] == 1
    assert read_payload["events"][0]["event_type"] == "dry_run_result"
    assert read_payload["events"][0]["artifact_filename"] == "patch_d0_26_audit_log_readback_cli_patchops_bundle.zip"
