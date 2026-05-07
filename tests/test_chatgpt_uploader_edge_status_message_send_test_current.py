from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.edge_status_reporter import (
    ACTION_POST_STATUS_MESSAGE,
    BLOCKED_EDGE_EXACT_MESSAGE_CONFIRMATION_MISMATCH,
    BLOCKED_EDGE_EXACT_MESSAGE_CONFIRMATION_MISSING,
    BLOCKED_EDGE_SEND_RISK,
    BLOCKED_EDGE_STATUS_MESSAGE_MISMATCH,
    BLOCKED_EDGE_STATUS_SEND_CONFIRMATION_MISMATCH,
    BLOCKED_EDGE_STATUS_SEND_CONFIRMATION_REQUIRED,
    BLOCKED_EDGE_STATUS_TARGET_NOT_READY,
    CONFIRM_EDGE_STATUS_MESSAGE_SEND,
    FAIL_EDGE_STATUS_MESSAGE_SEND_NOT_PROVEN,
    PASS_EDGE_STATUS_MESSAGE_SENT,
    expected_pass_status_message,
    read_expected_message_from_gate,
    run_edge_status_message_send_test,
    write_send_evidence,
)


def ready_values() -> dict[str, object]:
    return {
        "patch_name": "u3_c34_edge_status_message_send_test",
        "selected_action": ACTION_POST_STATUS_MESSAGE,
        "browser_lane": "edge",
        "pass_status_message": "u3_c34_edge_status_message_send_test has passed",
        "live_browser": True,
        "send_confirmation_text": CONFIRM_EDGE_STATUS_MESSAGE_SEND,
        "exact_message_confirmation": "u3_c34_edge_status_message_send_test has passed",
        "provider": "fake-ready",
    }


def run_ready(**overrides: object):
    values = ready_values()
    values.update(overrides)
    return run_edge_status_message_send_test(**values)  # type: ignore[arg-type]


def test_edge_send_ready_passes_with_explicit_confirmations() -> None:
    result = run_ready()

    assert result.ok is True
    assert result.result_label == PASS_EDGE_STATUS_MESSAGE_SENT
    assert result.edge_target_ready is True
    assert result.edge_target_focused is True
    assert result.composer_focus_attempted is True
    assert result.composer_text_placed is True
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


def test_live_browser_flag_is_required() -> None:
    result = run_ready(live_browser=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_SEND_RISK
    assert result.send_attempted is False
    assert result.chatgpt_submit_performed is False


def test_send_confirmation_is_required() -> None:
    result = run_ready(send_confirmation_text=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_SEND_CONFIRMATION_REQUIRED
    assert result.send_attempted is False


def test_send_confirmation_mismatch_blocks() -> None:
    result = run_ready(send_confirmation_text="WRONG")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_SEND_CONFIRMATION_MISMATCH
    assert result.send_confirmation_matched is False
    assert result.send_attempted is False


def test_exact_message_confirmation_is_required() -> None:
    result = run_ready(exact_message_confirmation=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_EXACT_MESSAGE_CONFIRMATION_MISSING
    assert result.send_attempted is False


def test_exact_message_confirmation_must_match() -> None:
    result = run_ready(exact_message_confirmation="wrong message")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_EXACT_MESSAGE_CONFIRMATION_MISMATCH
    assert result.exact_message_confirmation_matched is False
    assert result.send_attempted is False


def test_selected_action_must_be_post_status_message() -> None:
    result = run_ready(selected_action="upload_operator_report")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_MESSAGE_MISMATCH
    assert result.send_attempted is False


def test_browser_lane_must_be_edge() -> None:
    result = run_ready(browser_lane="chrome")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_MESSAGE_MISMATCH
    assert result.send_attempted is False


def test_pass_status_message_must_be_exact() -> None:
    result = run_ready(pass_status_message="wrong message")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_MESSAGE_MISMATCH
    assert result.send_attempted is False


def test_no_target_blocks_send() -> None:
    result = run_ready(provider="fake-no-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_TARGET_NOT_READY
    assert result.send_attempted is False
    assert result.chatgpt_submit_performed is False


def test_ambiguous_target_blocks_send() -> None:
    result = run_ready(provider="fake-ambiguous-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_TARGET_NOT_READY
    assert result.matching_target_count == 2
    assert result.send_attempted is False


def test_no_composer_blocks_send() -> None:
    result = run_ready(provider="fake-no-composer")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_TARGET_NOT_READY
    assert result.edge_target_focused is True
    assert result.composer_candidate_count == 0
    assert result.send_attempted is False


def test_message_mismatch_blocks_before_send() -> None:
    result = run_ready(provider="fake-mismatch")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_MESSAGE_MISMATCH
    assert result.composer_text_verified_before_send is False
    assert result.send_attempted is False
    assert result.chatgpt_submit_performed is False


def test_send_risk_blocks_before_send() -> None:
    result = run_ready(provider="fake-send-risk")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_SEND_RISK
    assert result.send_attempted is False
    assert result.status_message_posted is False


def test_send_verification_failure_blocks_outer_pass() -> None:
    result = run_ready(provider="fake-send-fails")

    assert result.ok is False
    assert result.result_label == FAIL_EDGE_STATUS_MESSAGE_SEND_NOT_PROVEN
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
                "browser_lane": "edge",
                "pass_status_message": "demo_patch has passed",
            }
        ),
        encoding="utf-8",
    )

    patch_name, selected_action, browser_lane, message = read_expected_message_from_gate(path)

    assert patch_name == "demo_patch"
    assert selected_action == ACTION_POST_STATUS_MESSAGE
    assert browser_lane == "edge"
    assert message == "demo_patch has passed"


def test_write_send_evidence_records_sent_and_redacts_title(tmp_path: Path) -> None:
    result = run_ready()
    json_path = tmp_path / "send.json"
    txt_path = tmp_path / "send.txt"

    write_send_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    assert json_path.exists()
    assert txt_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_EDGE_STATUS_MESSAGE_SENT
    assert payload["pass_status_message"] == "u3_c34_edge_status_message_send_test has passed"
    assert payload["selected_target_title_hash"] is not None
    assert "Microsoft Edge" not in json_path.read_text(encoding="utf-8")
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
    assert "result_label: PASS_EDGE_STATUS_MESSAGE_SENT" in text
    assert "chatgpt_submit_performed: true" in text
    assert "status_message_posted: true" in text
    assert "browser_dom_automation_used: false" in text