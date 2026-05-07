from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.chrome_operator_report_attach_no_send import (
    ACTION_UPLOAD_OPERATOR_REPORT,
    BLOCKED_ATTACHMENT_NOT_VERIFIED,
    BLOCKED_CHROME_AMBIGUOUS_TARGET,
    BLOCKED_CHROME_ATTACH_BROWSER_MISMATCH,
    BLOCKED_CHROME_ATTACH_CONFIG_MISSING,
    BLOCKED_CHROME_ATTACH_CONFIRMATION_MISMATCH,
    BLOCKED_CHROME_ATTACH_CONFIRMATION_REQUIRED,
    BLOCKED_CHROME_ATTACH_URL_INVALID,
    BLOCKED_CHROME_ATTACHMENT_CONTROL_NOT_FOUND,
    BLOCKED_CHROME_FILE_PICKER_NOT_READY,
    BLOCKED_CHROME_TARGET_NOT_READY,
    BLOCKED_OPERATOR_REPORT_HASH_MISMATCH,
    BLOCKED_OPERATOR_REPORT_MISSING,
    BLOCKED_SEND_RISK,
    CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND,
    PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND,
    run_chrome_operator_report_attach_no_send,
    sha256_file,
    sha256_text,
    write_evidence,
)

TARGET_URL = "https://chatgpt.com/g/g-p-69fb24e234b08191b691f750f5405732-patchops/c/69fc5f46-6e88-83eb-82b8-58a779a43ddd"


def make_report(tmp_path: Path, content: str = "operator report\n") -> Path:
    report = tmp_path / "operator_report.txt"
    report.write_text(content, encoding="utf-8")
    return report


def ready_config() -> dict[str, object]:
    return {
        "status_chat": {
            "enabled": True,
            "browser_lane": "chrome",
            "target_url": TARGET_URL,
            "target_url_sha256": sha256_text(TARGET_URL),
        }
    }


def run_ready(report: Path, **overrides: object):
    values = {
        "config_payload": ready_config(),
        "provider": "fake-ready",
        "live_browser": True,
        "stop_before_send": True,
        "confirmation_text": CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND,
        "operator_report_path": str(report),
        "expected_operator_report_sha256": sha256_file(report),
    }
    values.update(overrides)
    return run_chrome_operator_report_attach_no_send(**values)  # type: ignore[arg-type]


def test_fake_ready_attaches_report_no_send(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)

    assert result.ok is True
    assert result.result_label == PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND
    assert result.patch_result == "FAIL"
    assert result.selected_action == ACTION_UPLOAD_OPERATOR_REPORT
    assert result.browser_lane == "chrome"
    assert result.status_chat_configured is True
    assert result.status_chat_url_hash_or_redacted == f"sha256:{sha256_text(TARGET_URL)}"
    assert result.operator_report_path == str(report)
    assert result.operator_report_sha256 == sha256_file(report)
    assert result.computed_operator_report_sha256 == sha256_file(report)
    assert result.operator_report_size_bytes == report.stat().st_size
    assert result.chrome_target_ready is True
    assert result.chrome_target_focused is True
    assert result.attachment_control_found is True
    assert result.attachment_trigger_attempted is True
    assert result.file_picker_used is True
    assert result.file_picker_opened is True
    assert result.file_path_written is True
    assert result.attachment_ready is True
    assert result.attachment_verified is True
    assert result.file_upload_attempted is True
    assert result.operator_report_uploaded is False
    assert result.chatgpt_submit_performed is False
    assert result.status_message_posted is False
    assert result.send_button_pressed is False
    assert result.raw_conversation_text_available is False
    assert result.selenium_used is False
    assert result.webdriver_used is False
    assert result.browser_dom_automation_used is False
    assert result.cloudflare_bypass_attempted is False
    assert result.captcha_bypass_attempted is False
    assert result.safety.conversation_text_logged is False
    assert result.safety.random_page_click_performed is False


def test_missing_config_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_chrome_operator_report_attach_no_send(config_payload={}, provider="fake-ready", live_browser=True, stop_before_send=True, confirmation_text=CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND, operator_report_path=str(report), expected_operator_report_sha256=sha256_file(report))

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONFIG_MISSING
    assert result.file_upload_attempted is False


def test_browser_lane_must_be_chrome(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    payload = ready_config()
    payload["status_chat"]["browser_lane"] = "edge"  # type: ignore[index]

    result = run_chrome_operator_report_attach_no_send(config_payload=payload, provider="fake-ready", live_browser=True, stop_before_send=True, confirmation_text=CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND, operator_report_path=str(report), expected_operator_report_sha256=sha256_file(report))

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_BROWSER_MISMATCH


def test_target_url_must_be_valid(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    payload = ready_config()
    payload["status_chat"]["target_url"] = "https://example.com/nope"  # type: ignore[index]
    payload["status_chat"]["target_url_sha256"] = sha256_text("https://example.com/nope")  # type: ignore[index]

    result = run_chrome_operator_report_attach_no_send(config_payload=payload, provider="fake-ready", live_browser=True, stop_before_send=True, confirmation_text=CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND, operator_report_path=str(report), expected_operator_report_sha256=sha256_file(report))

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_URL_INVALID


def test_target_hash_must_match(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    payload = ready_config()
    payload["status_chat"]["target_url_sha256"] = "wrong"  # type: ignore[index]

    result = run_chrome_operator_report_attach_no_send(config_payload=payload, provider="fake-ready", live_browser=True, stop_before_send=True, confirmation_text=CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND, operator_report_path=str(report), expected_operator_report_sha256=sha256_file(report))

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_URL_INVALID


def test_confirmation_is_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, confirmation_text=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONFIRMATION_REQUIRED
    assert result.attachment_trigger_attempted is False


def test_confirmation_must_match(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, confirmation_text="WRONG")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONFIRMATION_MISMATCH
    assert result.attachment_trigger_attempted is False


def test_live_browser_flag_is_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, live_browser=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.attachment_trigger_attempted is False
    assert result.file_upload_attempted is False


def test_stop_before_send_is_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, stop_before_send=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.attachment_trigger_attempted is False
    assert result.send_button_pressed is False


def test_operator_report_path_is_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, operator_report_path=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_OPERATOR_REPORT_MISSING
    assert result.file_upload_attempted is False


def test_operator_report_file_must_exist(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    result = run_chrome_operator_report_attach_no_send(config_payload=ready_config(), provider="fake-ready", live_browser=True, stop_before_send=True, confirmation_text=CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND, operator_report_path=str(missing), expected_operator_report_sha256=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_OPERATOR_REPORT_MISSING
    assert result.file_upload_attempted is False


def test_operator_report_hash_mismatch_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, expected_operator_report_sha256="wrong")

    assert result.ok is False
    assert result.result_label == BLOCKED_OPERATOR_REPORT_HASH_MISMATCH
    assert result.computed_operator_report_sha256 == sha256_file(report)
    assert result.file_upload_attempted is False


def test_no_target_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-no-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_TARGET_NOT_READY
    assert result.attachment_trigger_attempted is False


def test_ambiguous_target_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-ambiguous-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_AMBIGUOUS_TARGET
    assert result.matching_target_count == 2
    assert result.attachment_trigger_attempted is False


def test_attachment_control_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-no-attachment-control")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACHMENT_CONTROL_NOT_FOUND
    assert result.attachment_candidate_count == 0
    assert result.attachment_trigger_attempted is False


def test_file_picker_must_open(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-no-dialog")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FILE_PICKER_NOT_READY
    assert result.attachment_trigger_attempted is True
    assert result.file_picker_opened is False
    assert result.file_upload_attempted is True
    assert result.operator_report_uploaded is False


def test_path_write_must_succeed(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-path-write-fails")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FILE_PICKER_NOT_READY
    assert result.file_picker_opened is True
    assert result.file_path_written is False
    assert result.operator_report_uploaded is False


def test_attachment_ready_must_be_detected(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-attachment-not-ready")

    assert result.ok is False
    assert result.result_label == BLOCKED_ATTACHMENT_NOT_VERIFIED
    assert result.file_path_written is True
    assert result.attachment_ready is False
    assert result.attachment_verified is False
    assert result.operator_report_uploaded is False
    assert result.chatgpt_submit_performed is False


def test_attachment_must_be_verified(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-attachment-not-verified")

    assert result.ok is False
    assert result.result_label == BLOCKED_ATTACHMENT_NOT_VERIFIED
    assert result.attachment_ready is True
    assert result.attachment_verified is False
    assert result.operator_report_uploaded is False
    assert result.chatgpt_submit_performed is False


def test_send_risk_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-send-risk")

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.send_risk_detected is True
    assert result.operator_report_uploaded is False
    assert result.chatgpt_submit_performed is False
    assert result.send_button_pressed is False


def test_write_evidence_redacts_url_and_title_but_keeps_report_hash(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)
    json_path = tmp_path / "attach.json"
    txt_path = tmp_path / "attach.txt"

    write_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    raw_json = json_path.read_text(encoding="utf-8")
    assert payload["result_label"] == PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND
    assert payload["status_chat_url_hash_or_redacted"] == f"sha256:{sha256_text(TARGET_URL)}"
    assert TARGET_URL not in raw_json
    assert "Google Chrome" not in raw_json
    assert payload["selected_target_title_hash"] is not None
    assert payload["operator_report_sha256"] == sha256_file(report)
    assert payload["computed_operator_report_sha256"] == sha256_file(report)
    assert payload["file_upload_attempted"] is True
    assert payload["operator_report_uploaded"] is False
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
    assert "result_label: PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND" in text
    assert TARGET_URL not in text
    assert "file_upload_attempted: true" in text
    assert "operator_report_uploaded: false" in text
    assert "send_button_pressed: false" in text
    assert "browser_dom_automation_used: false" in text