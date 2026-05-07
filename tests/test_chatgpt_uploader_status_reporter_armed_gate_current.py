from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.status_reporter_armed_gate import (
    ACTION_POST_STATUS_MESSAGE,
    ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD,
    ACTION_UPLOAD_OPERATOR_REPORT,
    BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_MISMATCH,
    BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_REQUIRED,
    BLOCKED_UPLOADER_STATUS_REPORTER_UNSUPPORTED_BROWSER_LANE,
    CONFIRM_POST_STATUS_MESSAGE,
    CONFIRM_UPLOAD_OPERATOR_REPORT,
    PASS_UPLOADER_STATUS_REPORTER_ARMED_GATE_VALIDATED,
    build_status_reporter_armed_gate,
    run_from_paths,
)


def test_post_status_message_requires_confirmation() -> None:
    gate = build_status_reporter_armed_gate(
        {
            "patch_name": "demo_patch",
            "patch_result": "PASS",
            "selected_action": ACTION_POST_STATUS_MESSAGE,
            "browser_lane": "chrome",
            "status_chat_configured": True,
        }
    )

    assert gate.ok is False
    assert gate.result_label == BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_REQUIRED
    assert gate.required_next_gate == CONFIRM_POST_STATUS_MESSAGE
    assert gate.pass_status_message == "demo_patch has passed"
    assert gate.browser_action_performed is False
    assert gate.chatgpt_submit_performed is False
    assert gate.status_message_posted is False
    assert gate.operator_report_uploaded is False
    assert gate.raw_conversation_text_available is False
    assert gate.selenium_used is False
    assert gate.webdriver_used is False
    assert gate.browser_dom_automation_used is False


def test_post_status_message_confirmation_mismatch_blocks() -> None:
    gate = build_status_reporter_armed_gate(
        {
            "patch_name": "demo_patch",
            "patch_result": "PASS",
            "selected_action": ACTION_POST_STATUS_MESSAGE,
            "browser_lane": "chrome",
            "status_chat_configured": True,
        },
        confirmation_text="WRONG_TOKEN",
    )

    assert gate.ok is False
    assert gate.result_label == BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_MISMATCH
    assert gate.confirmation_required is True
    assert gate.confirmation_matched is False


def test_post_status_message_confirmation_passes() -> None:
    gate = build_status_reporter_armed_gate(
        {
            "patch_name": "demo_patch",
            "patch_result": "PASS",
            "selected_action": ACTION_POST_STATUS_MESSAGE,
            "browser_lane": "chrome",
            "status_chat_configured": True,
            "status_chat_url": "https://chatgpt.com/c/example",
        },
        confirmation_text=CONFIRM_POST_STATUS_MESSAGE,
    )

    assert gate.ok is True
    assert gate.result_label == PASS_UPLOADER_STATUS_REPORTER_ARMED_GATE_VALIDATED
    assert gate.required_next_gate == CONFIRM_POST_STATUS_MESSAGE
    assert gate.confirmation_matched is True
    assert gate.status_chat_url_hash_or_redacted is not None
    assert "chatgpt.com" in gate.status_chat_url_hash_or_redacted
    assert "example" not in gate.status_chat_url_hash_or_redacted


def test_upload_operator_report_requires_upload_confirmation_and_hashes_report(tmp_path: Path) -> None:
    report = tmp_path / "operator_report.txt"
    report.write_text("operator report\n", encoding="utf-8")

    gate = build_status_reporter_armed_gate(
        {
            "patch_name": "demo_patch",
            "patch_result": "FAIL",
            "selected_action": ACTION_UPLOAD_OPERATOR_REPORT,
            "browser_lane": "edge",
            "status_chat_configured": True,
            "operator_report_path": str(report),
        },
        confirmation_text=CONFIRM_UPLOAD_OPERATOR_REPORT,
    )

    assert gate.ok is True
    assert gate.result_label == PASS_UPLOADER_STATUS_REPORTER_ARMED_GATE_VALIDATED
    assert gate.required_next_gate == CONFIRM_UPLOAD_OPERATOR_REPORT
    assert gate.operator_report_path == str(report)
    assert gate.operator_report_sha256 is not None
    assert gate.pass_status_message is None
    assert gate.operator_report_uploaded is False
    assert gate.safety.file_upload_attempted is False


def test_record_pass_locally_requires_no_live_confirmation() -> None:
    gate = build_status_reporter_armed_gate(
        {
            "patch_name": "demo_patch",
            "patch_result": "PASS",
            "selected_action": ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD,
            "status_chat_configured": False,
        }
    )

    assert gate.ok is True
    assert gate.result_label == PASS_UPLOADER_STATUS_REPORTER_ARMED_GATE_VALIDATED
    assert gate.required_next_gate == "none"
    assert gate.confirmation_required is False
    assert gate.confirmation_matched is True
    assert gate.pass_status_message is None
    assert gate.browser_action_performed is False
    assert gate.chatgpt_submit_performed is False


def test_unsupported_browser_lane_blocks_before_confirmation() -> None:
    gate = build_status_reporter_armed_gate(
        {
            "patch_name": "demo_patch",
            "patch_result": "PASS",
            "selected_action": ACTION_POST_STATUS_MESSAGE,
            "browser_lane": "auto",
            "status_chat_configured": True,
        },
        confirmation_text=CONFIRM_POST_STATUS_MESSAGE,
    )

    assert gate.ok is False
    assert gate.result_label == BLOCKED_UPLOADER_STATUS_REPORTER_UNSUPPORTED_BROWSER_LANE
    assert gate.browser_lane == "auto"


def test_run_from_paths_writes_handoff_evidence(tmp_path: Path) -> None:
    policy = tmp_path / "latest_uploader_status_report_policy.json"
    json_out = tmp_path / "latest_uploader_status_reporter_armed_gate.json"
    txt_out = tmp_path / "latest_uploader_status_reporter_armed_gate.txt"

    policy.write_text(
        json.dumps(
            {
                "patch_name": "demo_patch",
                "patch_result": "PASS",
                "selected_action": ACTION_POST_STATUS_MESSAGE,
                "browser_lane": "chrome",
                "status_chat_configured": True,
            }
        ),
        encoding="utf-8",
    )

    gate = run_from_paths(
        policy_path=policy,
        json_output_path=json_out,
        txt_output_path=txt_out,
        confirmation_text=CONFIRM_POST_STATUS_MESSAGE,
    )

    assert gate.ok is True
    assert json_out.exists()
    assert txt_out.exists()

    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_UPLOADER_STATUS_REPORTER_ARMED_GATE_VALIDATED
    assert payload["patch_name"] == "demo_patch"
    assert payload["selected_action"] == ACTION_POST_STATUS_MESSAGE
    assert payload["browser_lane"] == "chrome"
    assert payload["pass_status_message"] == "demo_patch has passed"
    assert payload["browser_action_performed"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["operator_report_uploaded"] is False
    assert payload["status_message_posted"] is False
    assert payload["send_button_pressed"] is False
    assert payload["raw_conversation_text_available"] is False
    assert payload["selenium_used"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
    assert payload["cloudflare_bypass_attempted"] is False
    assert payload["captcha_bypass_attempted"] is False

    text = txt_out.read_text(encoding="utf-8")
    assert "result_label: PASS_UPLOADER_STATUS_REPORTER_ARMED_GATE_VALIDATED" in text
    assert "chatgpt_submit_performed: false" in text
    assert "browser_dom_automation_used: false" in text


def test_nested_policy_shape_is_supported() -> None:
    gate = build_status_reporter_armed_gate(
        {
            "status_report_policy": {
                "patch_name": "nested_patch",
                "patch_result": "PASS",
                "selected_action": ACTION_POST_STATUS_MESSAGE,
                "browser_lane": "chrome",
                "status_chat_configured": True,
            }
        },
        confirmation_text=CONFIRM_POST_STATUS_MESSAGE,
    )

    assert gate.ok is True
    assert gate.patch_name == "nested_patch"
    assert gate.pass_status_message == "nested_patch has passed"