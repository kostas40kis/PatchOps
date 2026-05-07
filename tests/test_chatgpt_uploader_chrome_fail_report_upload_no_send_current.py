from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.chrome_report_uploader import (
    ACTION_UPLOAD_OPERATOR_REPORT,
    BLOCKED_CHROME_REPORT_TARGET_NOT_READY,
    BLOCKED_CHROME_REPORT_UPLOAD_CONFIRMATION_MISMATCH,
    BLOCKED_CHROME_REPORT_UPLOAD_CONFIRMATION_REQUIRED,
    BLOCKED_CHROME_REPORT_UPLOAD_MESSAGE_MISMATCH,
    BLOCKED_CHROME_REPORT_UPLOAD_NOT_VERIFIED,
    BLOCKED_OPERATOR_REPORT_HASH_MISMATCH,
    BLOCKED_OPERATOR_REPORT_MISSING,
    BLOCKED_SEND_RISK,
    CONFIRM_CHROME_FAIL_REPORT_UPLOAD_NO_SEND,
    PASS_CHROME_FAIL_REPORT_ATTACHMENT_READY_NO_SEND,
    read_report_values_from_gate,
    run_chrome_fail_report_upload_no_send,
    sha256_file,
    write_upload_evidence,
)


def make_report(tmp_path: Path, content: str = "operator report\n") -> Path:
    report = tmp_path / "operator_report.txt"
    report.write_text(content, encoding="utf-8")
    return report


def ready_values(report: Path) -> dict[str, object]:
    return {
        "patch_name": "demo_patch",
        "patch_result": "FAIL",
        "selected_action": ACTION_UPLOAD_OPERATOR_REPORT,
        "browser_lane": "chrome",
        "operator_report_path": str(report),
        "expected_operator_report_sha256": sha256_file(report),
        "live_browser": True,
        "confirmation_text": CONFIRM_CHROME_FAIL_REPORT_UPLOAD_NO_SEND,
        "stop_before_send": True,
        "provider": "fake-ready",
    }


def run_ready(report: Path, **overrides: object):
    values = ready_values(report)
    values.update(overrides)
    return run_chrome_fail_report_upload_no_send(**values)  # type: ignore[arg-type]


def test_fake_ready_upload_no_send_passes_and_never_submits(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)

    assert result.ok is True
    assert result.result_label == PASS_CHROME_FAIL_REPORT_ATTACHMENT_READY_NO_SEND
    assert result.patch_name == "demo_patch"
    assert result.patch_result == "FAIL"
    assert result.selected_action == ACTION_UPLOAD_OPERATOR_REPORT
    assert result.browser_lane == "chrome"
    assert result.chrome_target_ready is True
    assert result.chrome_target_focused is True
    assert result.upload_trigger_attempted is True
    assert result.file_picker_used is True
    assert result.file_path_written is True
    assert result.attachment_ready is True
    assert result.upload_verified is True
    assert result.operator_report_uploaded is True
    assert result.chatgpt_submit_performed is False
    assert result.status_message_posted is False
    assert result.send_button_pressed is False
    assert result.raw_conversation_text_available is False
    assert result.selenium_used is False
    assert result.webdriver_used is False
    assert result.browser_dom_automation_used is False
    assert result.cloudflare_bypass_attempted is False
    assert result.captcha_bypass_attempted is False
    assert result.safety.file_upload_attempted is True
    assert result.safety.conversation_text_logged is False
    assert result.safety.random_page_click_performed is False


def test_confirmation_is_required_before_live_action(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, confirmation_text=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_REPORT_UPLOAD_CONFIRMATION_REQUIRED
    assert result.upload_trigger_attempted is False
    assert result.operator_report_uploaded is False
    assert result.chatgpt_submit_performed is False


def test_confirmation_mismatch_blocks_before_live_action(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, confirmation_text="WRONG")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_REPORT_UPLOAD_CONFIRMATION_MISMATCH
    assert result.confirmation_matched is False
    assert result.upload_trigger_attempted is False
    assert result.operator_report_uploaded is False


def test_live_browser_flag_is_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, live_browser=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.upload_trigger_attempted is False
    assert result.chatgpt_submit_performed is False


def test_stop_before_send_is_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, stop_before_send=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.send_risk_detected is True
    assert result.upload_trigger_attempted is False


def test_selected_action_must_be_upload_operator_report(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, selected_action="post_status_message")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_REPORT_UPLOAD_MESSAGE_MISMATCH
    assert result.upload_trigger_attempted is False


def test_browser_lane_must_be_chrome(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, browser_lane="edge")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_REPORT_UPLOAD_MESSAGE_MISMATCH
    assert result.upload_trigger_attempted is False


def test_operator_report_path_is_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, operator_report_path=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_OPERATOR_REPORT_MISSING
    assert result.upload_trigger_attempted is False


def test_operator_report_file_must_exist(tmp_path: Path) -> None:
    missing = tmp_path / "missing_report.txt"
    result = run_chrome_fail_report_upload_no_send(
        patch_name="demo_patch",
        patch_result="FAIL",
        selected_action=ACTION_UPLOAD_OPERATOR_REPORT,
        browser_lane="chrome",
        operator_report_path=str(missing),
        expected_operator_report_sha256=None,
        live_browser=True,
        confirmation_text=CONFIRM_CHROME_FAIL_REPORT_UPLOAD_NO_SEND,
        stop_before_send=True,
        provider="fake-ready",
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_OPERATOR_REPORT_MISSING
    assert result.operator_report_uploaded is False


def test_operator_report_hash_mismatch_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, expected_operator_report_sha256="wrong-hash")

    assert result.ok is False
    assert result.result_label == BLOCKED_OPERATOR_REPORT_HASH_MISMATCH
    assert result.operator_report_sha256 == sha256_file(report)
    assert result.upload_trigger_attempted is False


def test_target_not_ready_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-no-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_REPORT_TARGET_NOT_READY
    assert result.upload_trigger_attempted is False
    assert result.operator_report_uploaded is False


def test_ambiguous_target_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-ambiguous-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_REPORT_TARGET_NOT_READY
    assert result.matching_target_count == 2
    assert result.upload_trigger_attempted is False


def test_picker_failure_blocks_upload_verified(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-picker-fails")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_REPORT_UPLOAD_NOT_VERIFIED
    assert result.upload_trigger_attempted is True
    assert result.file_picker_used is True
    assert result.file_path_written is False
    assert result.operator_report_uploaded is False
    assert result.chatgpt_submit_performed is False


def test_upload_not_verified_blocks_outer_pass(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-upload-not-verified")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_REPORT_UPLOAD_NOT_VERIFIED
    assert result.attachment_ready is True
    assert result.upload_verified is False
    assert result.operator_report_uploaded is False
    assert result.chatgpt_submit_performed is False


def test_send_risk_blocks_upload(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-send-risk")

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.send_risk_detected is True
    assert result.operator_report_uploaded is False
    assert result.chatgpt_submit_performed is False
    assert result.send_button_pressed is False


def test_gate_payload_supplies_report_values(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    path = tmp_path / "gate.json"
    path.write_text(
        json.dumps(
            {
                "patch_name": "demo_patch",
                "patch_result": "FAIL",
                "selected_action": ACTION_UPLOAD_OPERATOR_REPORT,
                "browser_lane": "chrome",
                "operator_report_path": str(report),
                "operator_report_sha256": sha256_file(report),
            }
        ),
        encoding="utf-8",
    )

    patch_name, patch_result, selected_action, browser_lane, report_path, report_hash = read_report_values_from_gate(path)

    assert patch_name == "demo_patch"
    assert patch_result == "FAIL"
    assert selected_action == ACTION_UPLOAD_OPERATOR_REPORT
    assert browser_lane == "chrome"
    assert report_path == str(report)
    assert report_hash == sha256_file(report)


def test_write_upload_evidence_redacts_title_and_records_no_send(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)
    json_path = tmp_path / "upload.json"
    txt_path = tmp_path / "upload.txt"

    write_upload_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    assert json_path.exists()
    assert txt_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_CHROME_FAIL_REPORT_ATTACHMENT_READY_NO_SEND
    assert payload["operator_report_sha256"] == sha256_file(report)
    assert payload["selected_target_title_hash"] is not None
    assert "Google Chrome" not in json_path.read_text(encoding="utf-8")
    assert payload["operator_report_uploaded"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert payload["status_message_posted"] is False
    assert payload["send_button_pressed"] is False
    assert payload["raw_conversation_text_available"] is False
    assert payload["selenium_used"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
    assert payload["cloudflare_bypass_attempted"] is False
    assert payload["captcha_bypass_attempted"] is False

    text = txt_path.read_text(encoding="utf-8")
    assert "result_label: PASS_CHROME_FAIL_REPORT_ATTACHMENT_READY_NO_SEND" in text
    assert "chatgpt_submit_performed: false" in text
    assert "send_button_pressed: false" in text
    assert "browser_dom_automation_used: false" in text