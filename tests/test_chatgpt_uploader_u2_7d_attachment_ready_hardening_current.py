from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _success_payload() -> dict:
    return {
        "status": "PASS",
        "result": "PASS_EXISTING_TARGET_UPLOAD_ATTACHED_NO_SEND",
        "existing_target_found": True,
        "existing_target_focused": True,
        "launch_skipped_existing_target": True,
        "normal_edge_launch_attempted": False,
        "canonical_trigger_attempted": True,
        "slash_sent": True,
        "browser_picker_opened": True,
        "file_path_written": True,
        "picker_enter_pressed": True,
        "file_upload_attempted": True,
        "attachment_verification_attempted": True,
        "attachment_visible": True,
        "attachment_ready": True,
        "upload_progress_resolved": True,
        "chatgpt_submit_performed": False,
        "conversation_text_logged": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
        "random_page_click_performed": False,
    }


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def test_u2_7d_classifier_accepts_attachment_ready_no_send_success() -> None:
    from patchops.chatgpt_uploader.attachment_ready_hardening import classify_attachment_ready_payload

    result = classify_attachment_ready_payload(_success_payload()).to_payload()

    assert result["status"] == "PASS"
    assert result["result"] == "PASS_ATTACHMENT_READY_NO_SEND_HARDENED"
    assert result["failure_layer"] == ""
    assert result["attachment_visible"] is True
    assert result["attachment_ready"] is True
    assert result["upload_progress_resolved"] is True
    assert result["chatgpt_submit_performed"] is False


def test_u2_7d_classifier_finds_first_missing_layer() -> None:
    from patchops.chatgpt_uploader.attachment_ready_hardening import classify_attachment_ready_payload

    payload = _success_payload()
    payload["browser_picker_opened"] = False
    payload["file_path_written"] = False
    result = classify_attachment_ready_payload(payload).to_payload()

    assert result["status"] == "PASS_OR_BLOCKED"
    assert result["failure_layer"] == "picker_not_opened"
    assert result["recommended_next_mode"] == "repair_picker_open_detection_or_focus"


def test_u2_7d_classifier_fails_forbidden_send() -> None:
    from patchops.chatgpt_uploader.attachment_ready_hardening import classify_attachment_ready_payload

    payload = _success_payload()
    payload["chatgpt_submit_performed"] = True
    result = classify_attachment_ready_payload(payload).to_payload()

    assert result["status"] == "FAIL_FORBIDDEN_SIDE_EFFECT"
    assert result["failure_layer"] == "chatgpt_submit_performed"


def test_u2_7d_script_simulated_success_writes_hardening_evidence(tmp_path: Path) -> None:
    source_payload = tmp_path / "source.json"
    report_path = tmp_path / "report.txt"
    evidence_dir = tmp_path / "evidence"

    source_payload.write_text(json.dumps(_success_payload(), indent=2), encoding="utf-8")
    report_path.write_text("report body\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_u2_7d_attachment_ready_hardening_gate.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(tmp_path / "target.json"),
            "--report-path",
            str(report_path),
            "--evidence-dir",
            str(evidence_dir),
            "--simulate-source-payload",
            str(source_payload),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_U2_7D_STATUS: PASS" in result.stdout
    assert "RESULT: PASS_ATTACHMENT_READY_NO_SEND_HARDENED" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["attachment_ready"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
