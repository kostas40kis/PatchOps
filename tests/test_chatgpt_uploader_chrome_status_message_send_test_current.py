from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.chrome_status_reporter import (
    ACTION_POST_STATUS_MESSAGE,
    BLOCKED_CHROME_STATUS_SEND_CONFIRMATION_MISMATCH,
    BLOCKED_CHROME_STATUS_SEND_CONFIRMATION_REQUIRED,
    BLOCKED_CHROME_STATUS_SEND_NOT_VERIFIED,
    BLOCKED_CHROME_STATUS_TARGET_NOT_READY,
    BLOCKED_SEND_RISK,
    BLOCKED_STATUS_MESSAGE_MISMATCH,
    CONFIRM_CHROME_STATUS_MESSAGE_NO_SEND,
    CONFIRM_CHROME_STATUS_MESSAGE_SEND,
    PASS_CHROME_STATUS_MESSAGE_COMPOSER_READY_NO_SEND,
    PASS_CHROME_STATUS_MESSAGE_SENT,
    expected_pass_status_message,
    read_expected_message_from_gate,
    run_chrome_status_message_no_send_probe,
    run_chrome_status_message_send_test,
    write_send_evidence,
)


def ready_values() -> dict[str, object]:
    return {
        "patch_name": "u3_c30_chrome_status_message_send_test",
        "selected_action": ACTION_POST_STATUS_MESSAGE,
        "browser_lane": "chrome",
        "pass_status_message": "u3_c30_chrome_status_message_send_test has passed",
        "live_browser": True,
        "no_send_confirmation_text": CONFIRM_CHROME_STATUS_MESSAGE_NO_SEND,
        "send_confirmation_text": CONFIRM_CHROME_STATUS_MESSAGE_SEND,
        "provider": "fake-ready",
    }


def run_send_ready(**overrides: object):
    values = ready_values()
    values.update(overrides)
    return run_chrome_status_message_send_test(**values)  # type: ignore[arg-type]


def test_no_send_probe_still_passes_and_never_submits() -> None:
    result = run_chrome_status_message_no_send_probe(
        patch_name="u3_c30_chrome_status_message_send_test",
        selected_action=ACTION_POST_STATUS_MESSAGE,
        browser_lane="chrome",
        pass_status_message="u3_c30_chrome_status_message_send_test has passed",
        live_browser=True,
        confirmation_text=CONFIRM_CHROME_STATUS_MESSAGE_NO_SEND,
        stop_before_send=True,
        provider="fake-ready",
    )

    assert result.ok is True
    assert result.result_label == PASS_CHROME_STATUS_MESSAGE_COMPOSER_READY_NO_SEND
    assert result.chatgpt_submit_performed is False
    assert result.status_message_posted is False
    assert result.send_button_pressed is False
    assert result.operator_report_uploaded is False
    assert result.selenium_used is False
    assert result.webdriver_used is False
    assert result.browser_dom_automation_used is False


def test_no_send_live_browser_gate_takes_priority_over_message_mismatch() -> None:
    result = run_chrome_status_message_no_send_probe(
        patch_name="u3_c30_chrome_status_message_send_test",
        selected_action=ACTION_POST_STATUS_MESSAGE,
        browser_lane="chrome",
        pass_status_message="wrong message",
        live_browser=False,
        confirmation_text=CONFIRM_CHROME_STATUS_MESSAGE_NO_SEND,
        stop_before_send=True,
        provider="fake-ready",
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.send_risk_detected is True
    assert result.composer_text_placed is False


def test_send_ready_passes_with_explicit_confirmations() -> None:
    result = run_send_ready()

    assert result.ok is True
    assert result.result_label == PASS_CHROME_STATUS_MESSAGE_SENT
    assert result.no_send_probe_required is True
    assert result.no_send_probe_ok is True
    assert result.chrome_target_ready is True
    assert result.chrome_target_focused is True
    assert result.composer_text_verified_before_send is True
    assert result.send_attempted is True
    assert result.send_verified is True
    assert result.chatgpt_submit_performed is True
    assert result.status_message_posted is True
    assert result.send_button_pressed is True
    assert result.browser_action_performed is True
    assert result.operator_report_uploaded is False
    assert result.raw_conversation_text_available is False
    assert result.selenium_used is False
    assert result.webdriver_used is False
    assert result.browser_dom_automation_used is False
    assert result.cloudflare_bypass_attempted is False
    assert result.captcha_bypass_attempted is False
    assert result.safety.file_upload_attempted is False
    assert result.safety.conversation_text_logged is False
    assert result.safety.random_page_click_performed is False


def test_send_requires_live_browser_flag() -> None:
    result = run_send_ready(live_browser=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.send_attempted is False
    assert result.chatgpt_submit_performed is False
    assert result.status_message_posted is False


def test_send_live_browser_gate_takes_priority_over_message_mismatch() -> None:
    result = run_send_ready(live_browser=False, pass_status_message="wrong message")

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.send_attempted is False
    assert result.chatgpt_submit_performed is False


def test_send_confirmation_is_required() -> None:
    result = run_send_ready(send_confirmation_text=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_STATUS_SEND_CONFIRMATION_REQUIRED
    assert result.send_attempted is False
    assert result.chatgpt_submit_performed is False


def test_send_confirmation_mismatch_blocks() -> None:
    result = run_send_ready(send_confirmation_text="WRONG")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_STATUS_SEND_CONFIRMATION_MISMATCH
    assert result.send_confirmation_matched is False
    assert result.send_attempted is False


def test_no_send_confirmation_must_pass_before_send() -> None:
    result = run_send_ready(no_send_confirmation_text="WRONG")

    assert result.ok is False
    assert result.no_send_probe_ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.send_attempted is False
    assert result.chatgpt_submit_performed is False


def test_selected_action_must_be_post_status_message_for_send() -> None:
    result = run_send_ready(selected_action="upload_operator_report")

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_MESSAGE_MISMATCH
    assert result.send_attempted is False


def test_browser_lane_must_be_chrome_for_send() -> None:
    result = run_send_ready(browser_lane="edge")

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_MESSAGE_MISMATCH
    assert result.send_attempted is False


def test_exact_status_message_is_required_for_send() -> None:
    result = run_send_ready(pass_status_message="wrong message")

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_MESSAGE_MISMATCH
    assert result.send_attempted is False


def test_target_not_ready_blocks_send() -> None:
    result = run_send_ready(provider="fake-no-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_STATUS_TARGET_NOT_READY
    assert result.send_attempted is False
    assert result.chatgpt_submit_performed is False


def test_message_mismatch_blocks_before_send() -> None:
    result = run_send_ready(provider="fake-mismatch")

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_MESSAGE_MISMATCH
    assert result.composer_text_verified_before_send is False
    assert result.send_attempted is False
    assert result.chatgpt_submit_performed is False


def test_send_risk_blocks_before_send() -> None:
    result = run_send_ready(provider="fake-send-risk")

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.send_attempted is False
    assert result.status_message_posted is False


def test_send_verification_failure_blocks_outer_pass() -> None:
    result = run_send_ready(provider="fake-send-fails")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_STATUS_SEND_NOT_VERIFIED
    assert result.send_attempted is True
    assert result.send_verified is False
    assert result.chatgpt_submit_performed is False
    assert result.status_message_posted is False


def test_expected_pass_status_message_shape() -> None:
    assert expected_pass_status_message("demo") == "demo has passed"


def test_gate_payload_supplies_expected_message(tmp_path: Path) -> None:
    path = tmp_path / "gate.json"
    path.write_text(
        json.dumps(
            {
                "patch_name": "demo_patch",
                "selected_action": ACTION_POST_STATUS_MESSAGE,
                "browser_lane": "chrome",
                "pass_status_message": "demo_patch has passed",
            }
        ),
        encoding="utf-8",
    )

    patch_name, selected_action, browser_lane, message = read_expected_message_from_gate(path)

    assert patch_name == "demo_patch"
    assert selected_action == ACTION_POST_STATUS_MESSAGE
    assert browser_lane == "chrome"
    assert message == "demo_patch has passed"


def test_write_send_evidence_records_sent_and_redacts_title(tmp_path: Path) -> None:
    result = run_send_ready()
    json_path = tmp_path / "send.json"
    txt_path = tmp_path / "send.txt"

    write_send_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    assert json_path.exists()
    assert txt_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_CHROME_STATUS_MESSAGE_SENT
    assert payload["pass_status_message"] == "u3_c30_chrome_status_message_send_test has passed"
    assert payload["selected_target_title_hash"] is not None
    assert "Google Chrome" not in json_path.read_text(encoding="utf-8")
    assert payload["chatgpt_submit_performed"] is True
    assert payload["status_message_posted"] is True
    assert payload["operator_report_uploaded"] is False
    assert payload["raw_conversation_text_available"] is False
    assert payload["selenium_used"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
    assert payload["cloudflare_bypass_attempted"] is False
    assert payload["captcha_bypass_attempted"] is False

    text = txt_path.read_text(encoding="utf-8")
    assert "result_label: PASS_CHROME_STATUS_MESSAGE_SENT" in text
    assert "chatgpt_submit_performed: true" in text
    assert "status_message_posted: true" in text
    assert "browser_dom_automation_used: false" in text