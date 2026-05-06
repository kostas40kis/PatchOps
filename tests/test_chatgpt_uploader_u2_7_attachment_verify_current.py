from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from patchops.chatgpt_uploader import recover_upload_verify_stage as stage
from patchops.chatgpt_uploader.attachment_verifier import attachment_verifier_safety_flags
from patchops.chatgpt_uploader.recover_upload_verify_stage import verify_stage_safety_flags

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_attachment_verifier_flags_do_not_send_or_log_conversation() -> None:
    flags = attachment_verifier_safety_flags(inspected=True)
    assert flags["attachment_verification_attempted"] is True
    assert flags["edge_uia_inspected"] is True
    assert flags["expected_filename_only"] is True
    assert flags["conversation_text_logged"] is False
    assert flags["chatgpt_submit_performed"] is False
    assert flags["selenium_used"] is False
    assert flags["webdriver_used"] is False
    assert flags["browser_dom_automation_used"] is False


def test_verify_stage_flags_combine_upload_and_attachment_without_send() -> None:
    upload = SimpleNamespace(
        safety_flags={
            "normal_edge_launch_attempted": True,
            "configured_target_open_attempted": True,
            "canonical_picker_trigger_attempted": True,
            "file_picker_open_attempted": True,
            "safe_click_attempted": True,
            "slash_sent": True,
            "file_path_written": True,
            "picker_enter_pressed": True,
            "file_upload_attempted": True,
        }
    )
    attachment = SimpleNamespace(status="PASS_ATTACHMENT_VISIBLE_NO_SEND", safety_flags={"attachment_verification_attempted": True})
    flags = verify_stage_safety_flags(upload=upload, attachment=attachment)
    assert flags["normal_edge_launch_attempted"] is True
    assert flags["attachment_verification_attempted"] is True
    assert flags["attachment_visible"] is True
    assert flags["chatgpt_submit_performed"] is False
    assert flags["conversation_text_logged"] is False
    assert flags["tab_sent"] is False
    assert flags["second_enter_attempted"] is False


def test_recover_upload_verify_success(monkeypatch, tmp_path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("body\n", encoding="utf-8")
    upload = SimpleNamespace(
        status="PASS_UPLOAD_ATTEMPTED_PICKER_CLOSED_NO_SEND",
        reason="upload ok",
        report_path=str(report),
        safety_flags={
            "normal_edge_launch_attempted": True,
            "configured_target_open_attempted": True,
            "canonical_picker_trigger_attempted": True,
            "file_picker_open_attempted": True,
            "safe_click_attempted": True,
            "slash_sent": True,
            "file_path_written": True,
            "picker_enter_pressed": True,
            "file_upload_attempted": True,
        },
        to_payload=lambda: {"status": "PASS_UPLOAD_ATTEMPTED_PICKER_CLOSED_NO_SEND"},
    )
    attachment = SimpleNamespace(
        status="PASS_ATTACHMENT_VISIBLE_NO_SEND",
        reason="visible",
        expected_filename=report.name,
        safety_flags={"attachment_verification_attempted": True},
        to_payload=lambda: {"status": "PASS_ATTACHMENT_VISIBLE_NO_SEND"},
    )
    monkeypatch.setattr(stage, "run_edge_recovery_then_type_path_enter_no_send", lambda **kwargs: upload)
    monkeypatch.setattr(stage, "wait_for_attachment_visible", lambda **kwargs: attachment)
    monkeypatch.setattr(stage, "write_attachment_verification_evidence", lambda result, evidence_dir: (tmp_path / "a.json", tmp_path / "a.txt"))
    result = stage.run_recover_upload_verify_attachment_no_send(
        target_config_path=tmp_path / "target.json",
        report_path=report,
        evidence_dir=tmp_path,
        allow_launch_edge=True,
        allow_open_picker=True,
    )
    assert result.status == "PASS_ATTACHMENT_VERIFIED_NO_SEND"
    assert result.safety_flags["attachment_visible"] is True
    assert result.safety_flags["chatgpt_submit_performed"] is False


def test_recover_upload_verify_blocks_if_upload_did_not_pass(monkeypatch, tmp_path) -> None:
    upload = SimpleNamespace(
        status="BLOCKED_TRIGGER_NOT_PASS",
        reason="blocked",
        report_path=str(tmp_path / "report.txt"),
        safety_flags={"chatgpt_submit_performed": False},
        to_payload=lambda: {"status": "BLOCKED_TRIGGER_NOT_PASS"},
    )
    monkeypatch.setattr(stage, "run_edge_recovery_then_type_path_enter_no_send", lambda **kwargs: upload)
    result = stage.run_recover_upload_verify_attachment_no_send(
        target_config_path=tmp_path / "target.json",
        report_path=tmp_path / "report.txt",
        evidence_dir=tmp_path,
        allow_launch_edge=True,
        allow_open_picker=True,
    )
    assert result.status == "BLOCKED_UPLOAD_NOT_PASS_NO_SEND"
    assert result.attachment_result is None
    assert result.safety_flags["chatgpt_submit_performed"] is False


def test_recover_upload_verify_script_requires_gate_for_live_actions(tmp_path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("body\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_recover_upload_verify_attachment_no_send.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--report-path",
            str(report),
            "--evidence-dir",
            str(tmp_path / "evidence"),
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 2
    assert "PATCHOPS_UPLOADER_RECOVER_UPLOAD_VERIFY_STATUS: BLOCKED_UPLOAD_NOT_PASS_NO_SEND" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
    assert "CONVERSATION_TEXT_LOGGED: false" in result.stdout
