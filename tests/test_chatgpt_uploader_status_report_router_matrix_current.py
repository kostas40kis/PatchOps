from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.status_report_router import (
    ACTION_POST_STATUS_MESSAGE,
    ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD,
    ACTION_UPLOAD_OPERATOR_REPORT,
    BLOCKED_UPLOADER_STATUS_ROUTER_BROWSER_UNSUPPORTED,
    BLOCKED_UPLOADER_STATUS_ROUTER_PATCH_NAME_REQUIRED,
    BLOCKED_UPLOADER_STATUS_ROUTER_REPORT_HASH_MISMATCH,
    BLOCKED_UPLOADER_STATUS_ROUTER_REPORT_REQUIRED,
    BLOCKED_UPLOADER_STATUS_ROUTER_RESULT_UNSUPPORTED,
    BLOCKED_UPLOADER_STATUS_ROUTER_STATUS_TARGET_INVALID,
    PASS_UPLOADER_STATUS_ROUTER_MATRIX_VALIDATED,
    expected_pass_status_message,
    route_status_report_path,
    route_status_report_payload,
    sha256_file,
    write_router_evidence,
)


def make_report(tmp_path: Path, content: str = "operator report\n") -> Path:
    report = tmp_path / "operator_report.txt"
    report.write_text(content, encoding="utf-8")
    return report


def test_pass_with_status_chat_routes_to_status_message_chrome() -> None:
    decision = route_status_report_payload(
        {
            "patch_name": "demo_patch",
            "patch_result": "PASS",
            "status_chat_configured": True,
            "status_chat_url": "https://chatgpt.com/c/example",
            "browser_lane": "chrome",
        }
    )

    assert decision.ok is True
    assert decision.result_label == PASS_UPLOADER_STATUS_ROUTER_MATRIX_VALIDATED
    assert decision.selected_action == ACTION_POST_STATUS_MESSAGE
    assert decision.browser_lane == "chrome"
    assert decision.pass_status_message == "demo_patch has passed"
    assert decision.required_next_gate == "chrome_status_message_send_gate"
    assert decision.operator_report_path is None
    assert decision.operator_report_sha256 is None
    assert decision.status_chat_url_hash_or_redacted is not None
    assert "example" not in decision.status_chat_url_hash_or_redacted
    assert decision.browser_action_performed is False
    assert decision.chatgpt_submit_performed is False
    assert decision.operator_report_uploaded is False
    assert decision.status_message_posted is False
    assert decision.send_button_pressed is False
    assert decision.raw_conversation_text_available is False
    assert decision.selenium_used is False
    assert decision.webdriver_used is False
    assert decision.browser_dom_automation_used is False
    assert decision.cloudflare_bypass_attempted is False
    assert decision.captcha_bypass_attempted is False


def test_pass_with_status_chat_routes_to_status_message_edge() -> None:
    decision = route_status_report_payload(
        {
            "patch_name": "demo_patch",
            "patch_result": "PASSED",
            "status_chat_configured": True,
            "status_chat_url_hash_or_redacted": "sha256:abc",
            "browser_lane": "edge",
        }
    )

    assert decision.ok is True
    assert decision.selected_action == ACTION_POST_STATUS_MESSAGE
    assert decision.browser_lane == "edge"
    assert decision.required_next_gate == "edge_status_message_send_gate"


def test_pass_without_status_chat_records_locally_no_upload() -> None:
    decision = route_status_report_payload(
        {
            "patch_name": "demo_patch",
            "patch_result": "PASS",
            "status_chat_configured": False,
        }
    )

    assert decision.ok is True
    assert decision.selected_action == ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD
    assert decision.required_next_gate == "none"
    assert decision.pass_status_message == "demo_patch has passed"
    assert decision.operator_report_path is None
    assert decision.operator_report_uploaded is False


def test_fail_routes_to_upload_operator_report_with_hash(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    decision = route_status_report_payload(
        {
            "patch_name": "demo_patch",
            "patch_result": "FAIL",
            "operator_report_path": str(report),
            "operator_report_sha256": sha256_file(report),
            "status_chat_configured": True,
            "status_chat_url": "https://chatgpt.com/c/example",
            "browser_lane": "chrome",
        }
    )

    assert decision.ok is True
    assert decision.selected_action == ACTION_UPLOAD_OPERATOR_REPORT
    assert decision.browser_lane == "chrome"
    assert decision.required_next_gate == "chrome_operator_report_upload_gate"
    assert decision.operator_report_path == str(report)
    assert decision.operator_report_sha256 == sha256_file(report)
    assert decision.pass_status_message is None
    assert decision.chatgpt_submit_performed is False
    assert decision.operator_report_uploaded is False


def test_blocked_routes_to_upload_operator_report_default_chrome_when_no_status_chat(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    decision = route_status_report_payload(
        {
            "patch_name": "demo_patch",
            "patch_result": "BLOCKED",
            "operator_report_path": str(report),
            "status_chat_configured": False,
        }
    )

    assert decision.ok is True
    assert decision.selected_action == ACTION_UPLOAD_OPERATOR_REPORT
    assert decision.browser_lane == "chrome"
    assert decision.required_next_gate == "chrome_operator_report_upload_gate"
    assert decision.operator_report_sha256 == sha256_file(report)


def test_missing_patch_name_blocks() -> None:
    decision = route_status_report_payload({"patch_result": "PASS"})

    assert decision.ok is False
    assert decision.result_label == BLOCKED_UPLOADER_STATUS_ROUTER_PATCH_NAME_REQUIRED
    assert decision.selected_action is None


def test_unsupported_result_blocks() -> None:
    decision = route_status_report_payload({"patch_name": "demo_patch", "patch_result": "MAYBE"})

    assert decision.ok is False
    assert decision.result_label == BLOCKED_UPLOADER_STATUS_ROUTER_RESULT_UNSUPPORTED
    assert decision.selected_action is None


def test_status_chat_configured_requires_supported_browser_lane() -> None:
    decision = route_status_report_payload(
        {
            "patch_name": "demo_patch",
            "patch_result": "PASS",
            "status_chat_configured": True,
            "status_chat_url": "https://chatgpt.com/c/example",
            "browser_lane": "auto",
        }
    )

    assert decision.ok is False
    assert decision.result_label == BLOCKED_UPLOADER_STATUS_ROUTER_BROWSER_UNSUPPORTED
    assert decision.browser_lane == "auto"


def test_status_chat_configured_requires_url_or_hash() -> None:
    decision = route_status_report_payload(
        {
            "patch_name": "demo_patch",
            "patch_result": "PASS",
            "status_chat_configured": True,
            "browser_lane": "chrome",
        }
    )

    assert decision.ok is False
    assert decision.result_label == BLOCKED_UPLOADER_STATUS_ROUTER_STATUS_TARGET_INVALID
    assert decision.selected_action is None


def test_fail_requires_operator_report_path() -> None:
    decision = route_status_report_payload(
        {
            "patch_name": "demo_patch",
            "patch_result": "FAIL",
            "status_chat_configured": False,
        }
    )

    assert decision.ok is False
    assert decision.result_label == BLOCKED_UPLOADER_STATUS_ROUTER_REPORT_REQUIRED
    assert decision.selected_action == ACTION_UPLOAD_OPERATOR_REPORT


def test_fail_requires_operator_report_file_to_exist(tmp_path: Path) -> None:
    missing = tmp_path / "missing_report.txt"
    decision = route_status_report_payload(
        {
            "patch_name": "demo_patch",
            "patch_result": "FAIL",
            "operator_report_path": str(missing),
            "browser_lane": "chrome",
        }
    )

    assert decision.ok is False
    assert decision.result_label == BLOCKED_UPLOADER_STATUS_ROUTER_REPORT_REQUIRED
    assert decision.operator_report_path == str(missing)


def test_report_hash_mismatch_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    decision = route_status_report_payload(
        {
            "patch_name": "demo_patch",
            "patch_result": "FAIL",
            "operator_report_path": str(report),
            "operator_report_sha256": "wrong-hash",
            "browser_lane": "chrome",
        }
    )

    assert decision.ok is False
    assert decision.result_label == BLOCKED_UPLOADER_STATUS_ROUTER_REPORT_HASH_MISMATCH
    assert decision.operator_report_sha256 == sha256_file(report)


def test_nested_status_chat_payload_is_supported() -> None:
    decision = route_status_report_payload(
        {
            "policy": {
                "patch_name": "demo_patch",
                "patch_result": "PASS",
            },
            "status_chat": {
                "enabled": True,
                "browser_lane": "chrome",
                "target_url": "https://chatgpt.com/c/example",
            },
        }
    )

    assert decision.ok is True
    assert decision.selected_action == ACTION_POST_STATUS_MESSAGE
    assert decision.browser_lane == "chrome"


def test_route_status_report_path_and_write_evidence(tmp_path: Path) -> None:
    input_path = tmp_path / "input.json"
    policy_path = tmp_path / "policy.json"
    text_path = tmp_path / "policy.txt"
    input_path.write_text(
        json.dumps(
            {
                "patch_name": "demo_patch",
                "patch_result": "PASS",
                "status_chat_configured": False,
            }
        ),
        encoding="utf-8",
    )

    decision = route_status_report_path(input_path)
    write_router_evidence(decision, policy_output_path=policy_path, txt_output_path=text_path)

    assert decision.ok is True
    assert decision.source_input_path == str(input_path)
    assert policy_path.exists()
    assert text_path.exists()

    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_UPLOADER_STATUS_ROUTER_MATRIX_VALIDATED
    assert payload["selected_action"] == ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD
    assert payload["policy"]["selected_action"] == ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD
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

    text = text_path.read_text(encoding="utf-8")
    assert "result_label: PASS_UPLOADER_STATUS_ROUTER_MATRIX_VALIDATED" in text
    assert "selected_action: record_pass_locally_no_upload" in text
    assert "browser_dom_automation_used: false" in text


def test_expected_pass_status_message_shape() -> None:
    assert expected_pass_status_message("abc") == "abc has passed"