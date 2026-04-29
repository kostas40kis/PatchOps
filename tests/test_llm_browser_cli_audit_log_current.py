from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchops.llm_browser import commands


def _html_with_bundle(filename: str = "patch_d0_25_wire_audit_log_into_cli_patchops_bundle.zip") -> str:
    return f"""
    <article data-message-author-role="assistant">
      <a href="/downloads/{filename}?download=1">{filename}</a>
    </article>
    <textarea id="prompt-textarea"></textarea>
    """


def test_dry_run_help_includes_audit_log_without_auto_send(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["dry-run", "--help"])

    out = capsys.readouterr().out

    assert exc.value.code == 0
    assert "--audit-log" in out
    assert "--audit-source" in out
    assert "--auto-send" not in out


def test_run_once_help_includes_audit_log_without_auto_send(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        commands.main(["run-once", "--help"])

    out = capsys.readouterr().out

    assert exc.value.code == 0
    assert "--audit-log" in out
    assert "--audit-source" in out
    assert "--auto-send" not in out
    assert "--allow-send" not in out


def test_dry_run_cli_writes_audit_log_jsonl(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    audit_log = tmp_path / "audit.jsonl"

    code = commands.main(
        [
            "dry-run",
            "--snapshot-html",
            _html_with_bundle(),
            "--audit-log",
            str(audit_log),
            "--audit-source",
            "unit-dry-run",
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    audit_payload = json.loads(audit_log.read_text(encoding="utf-8").strip())

    assert code == 0
    assert payload["snapshot"]["state"] == "DOWNLOADING"
    assert audit_payload["event_type"] == "dry_run_result"
    assert audit_payload["source"] == "unit-dry-run"
    assert audit_payload["state"] == "DOWNLOADING"
    assert audit_payload["artifact_filename"] == "patch_d0_25_wire_audit_log_into_cli_patchops_bundle.zip"
    assert audit_payload["metadata"]["planned_actions"] == payload["planned_actions"]
    assert audit_payload["metadata"]["side_effects_performed"] == []


def test_dry_run_cli_appends_one_audit_event_per_invocation(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    audit_log = tmp_path / "audit.jsonl"

    for _ in range(2):
        code = commands.main(
            [
                "dry-run",
                "--snapshot-html",
                '<article data-message-author-role="assistant">no zip here</article><textarea></textarea>',
                "--audit-log",
                str(audit_log),
                "--json",
            ]
        )
        assert code == 0
        json.loads(capsys.readouterr().out)

    lines = audit_log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert all(json.loads(line)["event_type"] == "dry_run_result" for line in lines)


def test_run_once_cli_writes_integration_audit_log_jsonl(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    audit_log = tmp_path / "audit.jsonl"

    code = commands.main(
        [
            "run-once",
            "--dry-run",
            "--snapshot-html",
            _html_with_bundle(),
            "--audit-log",
            str(audit_log),
            "--audit-source",
            "unit-run-once",
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    audit_payload = json.loads(audit_log.read_text(encoding="utf-8").strip())

    assert code == 0
    assert payload["dry_run"]["snapshot"]["state"] == "DOWNLOADING"
    assert audit_payload["event_type"] == "integration_result"
    assert audit_payload["source"] == "unit-run-once"
    assert audit_payload["state"] == "DOWNLOADING"
    assert audit_payload["artifact_filename"] == "patch_d0_25_wire_audit_log_into_cli_patchops_bundle.zip"
    assert audit_payload["metadata"]["planned_actions"] == payload["dry_run"]["planned_actions"]
    assert audit_payload["metadata"]["side_effects_performed"] == []


def test_run_once_text_output_mentions_audit_log(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    audit_log = tmp_path / "audit.jsonl"

    code = commands.main(
        [
            "run-once",
            "--dry-run",
            "--snapshot-html",
            _html_with_bundle(),
            "--audit-log",
            str(audit_log),
        ]
    )

    out = capsys.readouterr().out

    assert code == 0
    assert f"Audit log: {audit_log}" in out
    assert audit_log.exists()


def test_run_once_live_mode_rejection_does_not_write_audit_log(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    audit_log = tmp_path / "audit.jsonl"

    code = commands.main(
        [
            "run-once",
            "--audit-log",
            str(audit_log),
        ]
    )

    out = capsys.readouterr().out

    assert code == 2
    assert "live mode is not enabled" in out
    assert not audit_log.exists()
