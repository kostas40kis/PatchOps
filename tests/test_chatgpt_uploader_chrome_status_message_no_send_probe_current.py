from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.chrome_status_reporter import (
    ACTION_POST_STATUS_MESSAGE,
    BLOCKED_CHROME_STATUS_TARGET_NOT_READY,
    BLOCKED_SEND_RISK,
    BLOCKED_STATUS_MESSAGE_MISMATCH,
    CONFIRM_CHROME_STATUS_MESSAGE_NO_SEND,
    PASS_CHROME_STATUS_MESSAGE_COMPOSER_READY_NO_SEND,
    expected_pass_status_message,
    read_expected_message_from_gate,
    run_chrome_status_message_no_send_probe,
    write_probe_evidence,
)


def run_ready(**overrides: object):
    values = {
        "patch_name": "u3_c29_chrome_status_message_no_send_probe",
        "selected_action": ACTION_POST_STATUS_MESSAGE,
        "browser_lane": "chrome",
        "pass_status_message": "u3_c29_chrome_status_message_no_send_probe has passed",
        "live_browser": True,
        "confirmation_text": CONFIRM_CHROME_STATUS_MESSAGE_NO_SEND,
        "stop_before_send": True,
        "provider": "fake-ready",
    }
    values.update(overrides)
    return run_chrome_status_message_no_send_probe(**values)  # type: ignore[arg-type]


def test_fake_ready_no_send_probe_passes_and_never_submits() -> None:
    result = run_ready()

    assert result.ok is True
    assert result.result_label == PASS_CHROME_STATUS_MESSAGE_COMPOSER_READY_NO_SEND
    assert result.chrome_target_ready is True
    assert result.chrome_target_focused is True
    assert result.composer_focus_attempted is True
    assert result.composer_text_placed is True
    assert result.composer_text_verified is True
    assert result.send_risk_detected is False
    assert result.browser_action_performed is True
    assert result.chatgpt_submit_performed is False
    assert result.operator_report_uploaded is False
    assert result.status_message_posted is False
    assert result.send_button_pressed is False
    assert result.raw_conversation_text_available is False
    assert result.selenium_used is False
    assert result.webdriver_used is False
    assert result.browser_dom_automation_used is False
    assert result.cloudflare_bypass_attempted is False
    assert result.captcha_bypass_attempted is False
    assert result.safety.file_upload_attempted is False
    assert result.safety.conversation_text_logged is False
    assert result.safety.random_page_click_performed is False


def test_live_browser_flag_is_required() -> None:
    result = run_ready(live_browser=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.send_risk_detected is True
    assert result.browser_action_performed is False


def test_confirmation_text_is_required() -> None:
    result = run_ready(confirmation_text="WRONG")

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.confirmation_matched is False
    assert result.browser_action_performed is False


def test_stop_before_send_is_required() -> None:
    result = run_ready(stop_before_send=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.send_risk_detected is True
    assert result.chatgpt_submit_performed is False
    assert result.send_button_pressed is False


def test_selected_action_must_be_post_status_message() -> None:
    result = run_ready(selected_action="upload_operator_report")

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_MESSAGE_MISMATCH
    assert result.browser_action_performed is False


def test_browser_lane_must_be_chrome() -> None:
    result = run_ready(browser_lane="edge")

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_MESSAGE_MISMATCH
    assert result.browser_action_performed is False


def test_exact_status_message_is_required() -> None:
    result = run_ready(pass_status_message="wrong message")

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_MESSAGE_MISMATCH
    assert result.composer_text_placed is False


def test_target_not_ready_blocks() -> None:
    result = run_ready(provider="fake-no-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_STATUS_TARGET_NOT_READY
    assert result.chrome_target_ready is False
    assert result.composer_focus_attempted is False
    assert result.chatgpt_submit_performed is False


def test_ambiguous_target_blocks_as_not_ready() -> None:
    result = run_ready(provider="fake-ambiguous-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_STATUS_TARGET_NOT_READY
    assert result.matching_target_count == 2
    assert result.send_button_pressed is False


def test_send_risk_blocks_before_text_placement() -> None:
    result = run_ready(provider="fake-send-risk")

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.composer_focus_attempted is True
    assert result.composer_text_placed is False
    assert result.send_risk_detected is True
    assert result.chatgpt_submit_performed is False
    assert result.status_message_posted is False


def test_message_mismatch_blocks_after_safe_attempt() -> None:
    result = run_ready(provider="fake-mismatch")

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_MESSAGE_MISMATCH
    assert result.composer_text_placed is True
    assert result.composer_text_verified is False
    assert result.chatgpt_submit_performed is False
    assert result.send_button_pressed is False


def test_expected_pass_status_message_shape() -> None:
    assert expected_pass_status_message("abc") == "abc has passed"


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


def test_missing_gate_payload_falls_back_to_c29_message(tmp_path: Path) -> None:
    patch_name, selected_action, browser_lane, message = read_expected_message_from_gate(tmp_path / "missing.json")

    assert patch_name == "u3_c29_chrome_status_message_no_send_probe"
    assert selected_action == ACTION_POST_STATUS_MESSAGE
    assert browser_lane == "chrome"
    assert message == "u3_c29_chrome_status_message_no_send_probe has passed"


def test_write_probe_evidence_redacts_title_and_records_no_send(tmp_path: Path) -> None:
    result = run_ready()
    json_path = tmp_path / "probe.json"
    txt_path = tmp_path / "probe.txt"

    write_probe_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    assert json_path.exists()
    assert txt_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_CHROME_STATUS_MESSAGE_COMPOSER_READY_NO_SEND
    assert payload["pass_status_message"] == "u3_c29_chrome_status_message_no_send_probe has passed"
    assert payload["selected_target_title_hash"] is not None
    assert "Google Chrome" not in json_path.read_text(encoding="utf-8")
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
    assert "result_label: PASS_CHROME_STATUS_MESSAGE_COMPOSER_READY_NO_SEND" in text
    assert "chatgpt_submit_performed: false" in text
    assert "send_button_pressed: false" in text
    assert "browser_dom_automation_used: false" in text