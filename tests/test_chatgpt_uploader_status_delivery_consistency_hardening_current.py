from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.status_delivery_consistency import (
    ACTION_POST_STATUS_MESSAGE,
    ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD,
    ACTION_UPLOAD_OPERATOR_REPORT,
    BLOCKED_STATUS_DELIVERY_HASH_MISMATCH,
    BLOCKED_STATUS_DELIVERY_IDEMPOTENCY_CONFLICT,
    BLOCKED_STATUS_DELIVERY_SCHEMA_INVALID,
    BLOCKED_STATUS_DELIVERY_UNBOUNDED_RETRY,
    BLOCKED_STATUS_DELIVERY_UNBOUNDED_TIMEOUT,
    BLOCKED_STATUS_DELIVERY_UNSAFE_FLAGS,
    PASS_STATUS_DELIVERY_CONSISTENCY_HARDENED,
    expected_pass_status_message,
    run_status_delivery_consistency_doctor,
    sha256_file,
    sha256_text,
    write_consistency_evidence,
)


def make_report(tmp_path: Path, content: str = "operator report\n") -> Path:
    report = tmp_path / "operator_report.txt"
    report.write_text(content, encoding="utf-8")
    return report


def ledger(tmp_path: Path) -> Path:
    return tmp_path / "ledger.jsonl"


def test_post_status_message_pass_hardens_and_appends_ledger(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {
            "patch_name": "demo_patch",
            "patch_result": "PASS",
            "selected_action": ACTION_POST_STATUS_MESSAGE,
            "browser_lane": "chrome",
            "status_chat_configured": True,
            "pass_status_message": "demo_patch has passed",
        },
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is True
    assert result.result_label == PASS_STATUS_DELIVERY_CONSISTENCY_HARDENED
    assert result.pass_status_message_sha256 == sha256_text("demo_patch has passed")
    assert result.exact_message_sha256 == sha256_text("demo_patch has passed")
    assert result.selected_action_sha256 == sha256_text(ACTION_POST_STATUS_MESSAGE)
    assert result.idempotency_key is not None
    assert result.normalized_delivery_sha256 is not None
    assert result.retry_count == 1
    assert result.timeout_seconds == 30
    assert result.ledger_appended is True
    assert result.ledger_duplicate_seen is False
    assert Path(result.ledger_path).exists()
    assert result.browser_action_performed is False
    assert result.chatgpt_submit_performed is False
    assert result.operator_report_uploaded is False
    assert result.status_message_posted is False
    assert result.send_button_pressed is False
    assert result.file_upload_attempted is False
    assert result.raw_conversation_text_available is False
    assert result.selenium_used is False
    assert result.webdriver_used is False
    assert result.browser_dom_automation_used is False
    assert result.cloudflare_bypass_attempted is False
    assert result.captcha_bypass_attempted is False


def test_record_pass_locally_hardens_without_browser_action(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {
            "patch_name": "demo_patch",
            "patch_result": "PASS",
            "selected_action": ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD,
            "status_chat_configured": False,
            "pass_status_message": "demo_patch has passed",
        },
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is True
    assert result.selected_action == ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD
    assert result.browser_lane is None
    assert result.operator_report_path is None
    assert result.operator_report_uploaded is False
    assert result.status_message_posted is False


def test_upload_operator_report_hardens_and_computes_hash(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_status_delivery_consistency_doctor(
        {
            "patch_name": "demo_patch",
            "patch_result": "FAIL",
            "selected_action": ACTION_UPLOAD_OPERATOR_REPORT,
            "browser_lane": "edge",
            "operator_report_path": str(report),
        },
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is True
    assert result.operator_report_sha256 == sha256_file(report)
    assert result.computed_operator_report_sha256 == sha256_file(report)
    assert result.pass_status_message is None
    assert result.exact_message_sha256 is None
    assert result.selected_action_sha256 == sha256_text(ACTION_UPLOAD_OPERATOR_REPORT)
    assert result.ledger_appended is True


def test_missing_patch_name_blocks_schema(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {"selected_action": ACTION_POST_STATUS_MESSAGE, "browser_lane": "chrome", "pass_status_message": "x has passed"},
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_DELIVERY_SCHEMA_INVALID
    assert result.ledger_appended is False


def test_unknown_selected_action_blocks_schema(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {"patch_name": "demo", "selected_action": "unknown", "browser_lane": "chrome"},
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_DELIVERY_SCHEMA_INVALID


def test_browser_action_requires_named_lane(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {"patch_name": "demo", "selected_action": ACTION_POST_STATUS_MESSAGE, "browser_lane": "auto", "pass_status_message": "demo has passed"},
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_DELIVERY_SCHEMA_INVALID


def test_pass_message_must_be_exact(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {"patch_name": "demo", "selected_action": ACTION_POST_STATUS_MESSAGE, "browser_lane": "edge", "pass_status_message": "wrong"},
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_DELIVERY_SCHEMA_INVALID


def test_upload_requires_operator_report_path(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {"patch_name": "demo", "selected_action": ACTION_UPLOAD_OPERATOR_REPORT, "browser_lane": "edge"},
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_DELIVERY_SCHEMA_INVALID


def test_report_hash_mismatch_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_status_delivery_consistency_doctor(
        {
            "patch_name": "demo",
            "selected_action": ACTION_UPLOAD_OPERATOR_REPORT,
            "browser_lane": "edge",
            "operator_report_path": str(report),
            "operator_report_sha256": "wrong-hash",
        },
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_DELIVERY_HASH_MISMATCH
    assert result.computed_operator_report_sha256 == sha256_file(report)


def test_exact_message_hash_mismatch_blocks(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {
            "patch_name": "demo",
            "selected_action": ACTION_POST_STATUS_MESSAGE,
            "browser_lane": "chrome",
            "pass_status_message": "demo has passed",
            "exact_message_sha256": "wrong",
        },
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_DELIVERY_HASH_MISMATCH


def test_selected_action_hash_mismatch_blocks(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {
            "patch_name": "demo",
            "selected_action": ACTION_POST_STATUS_MESSAGE,
            "browser_lane": "chrome",
            "pass_status_message": "demo has passed",
            "selected_action_sha256": "wrong",
        },
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_DELIVERY_HASH_MISMATCH


def test_retry_count_is_bounded(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {"patch_name": "demo", "selected_action": ACTION_POST_STATUS_MESSAGE, "browser_lane": "chrome", "pass_status_message": "demo has passed", "retry_count": 99},
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_DELIVERY_UNBOUNDED_RETRY


def test_timeout_is_bounded(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {"patch_name": "demo", "selected_action": ACTION_POST_STATUS_MESSAGE, "browser_lane": "chrome", "pass_status_message": "demo has passed", "timeout_seconds": 999},
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_DELIVERY_UNBOUNDED_TIMEOUT


def test_unsafe_flags_block(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {
            "patch_name": "demo",
            "selected_action": ACTION_POST_STATUS_MESSAGE,
            "browser_lane": "chrome",
            "pass_status_message": "demo has passed",
            "safety": {"selenium_used": True},
        },
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_DELIVERY_UNSAFE_FLAGS
    assert "selenium_used" in result.issues[0]


def test_duplicate_idempotency_same_payload_is_allowed_without_append(tmp_path: Path) -> None:
    ledger_path = ledger(tmp_path)
    payload = {"patch_name": "demo", "selected_action": ACTION_POST_STATUS_MESSAGE, "browser_lane": "chrome", "pass_status_message": "demo has passed"}

    first = run_status_delivery_consistency_doctor(payload, ledger_path=ledger_path)
    second = run_status_delivery_consistency_doctor(payload, ledger_path=ledger_path)

    assert first.ok is True
    assert first.ledger_appended is True
    assert second.ok is True
    assert second.ledger_duplicate_seen is True
    assert second.ledger_appended is False
    assert len(ledger_path.read_text(encoding="utf-8").splitlines()) == 1


def test_idempotency_conflict_blocks_if_ledger_key_has_different_hash(tmp_path: Path) -> None:
    ledger_path = ledger(tmp_path)
    first = run_status_delivery_consistency_doctor(
        {"patch_name": "demo", "selected_action": ACTION_POST_STATUS_MESSAGE, "browser_lane": "chrome", "pass_status_message": "demo has passed"},
        ledger_path=ledger_path,
    )
    assert first.ok is True
    ledger_path.write_text(
        json.dumps({"idempotency_key": first.idempotency_key, "normalized_delivery_sha256": "different"}) + "\n",
        encoding="utf-8",
    )

    second = run_status_delivery_consistency_doctor(
        {"patch_name": "demo", "selected_action": ACTION_POST_STATUS_MESSAGE, "browser_lane": "chrome", "pass_status_message": "demo has passed"},
        ledger_path=ledger_path,
    )

    assert second.ok is False
    assert second.result_label == BLOCKED_STATUS_DELIVERY_IDEMPOTENCY_CONFLICT


def test_supplied_idempotency_key_must_match(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {
            "patch_name": "demo",
            "selected_action": ACTION_POST_STATUS_MESSAGE,
            "browser_lane": "chrome",
            "pass_status_message": "demo has passed",
            "idempotency_key": "wrong",
        },
        ledger_path=ledger(tmp_path),
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_STATUS_DELIVERY_HASH_MISMATCH


def test_write_consistency_evidence(tmp_path: Path) -> None:
    result = run_status_delivery_consistency_doctor(
        {"patch_name": "demo", "selected_action": ACTION_POST_STATUS_MESSAGE, "browser_lane": "edge", "pass_status_message": "demo has passed"},
        ledger_path=ledger(tmp_path),
    )
    json_path = tmp_path / "consistency.json"
    txt_path = tmp_path / "consistency.txt"

    write_consistency_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_STATUS_DELIVERY_CONSISTENCY_HARDENED
    assert payload["idempotency_key"] is not None
    assert payload["normalized_delivery_sha256"] is not None
    assert payload["browser_action_performed"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["operator_report_uploaded"] is False
    assert payload["status_message_posted"] is False
    assert payload["send_button_pressed"] is False
    assert payload["file_upload_attempted"] is False
    assert payload["raw_conversation_text_available"] is False
    assert payload["selenium_used"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
    assert payload["cloudflare_bypass_attempted"] is False
    assert payload["captcha_bypass_attempted"] is False

    text = txt_path.read_text(encoding="utf-8")
    assert "result_label: PASS_STATUS_DELIVERY_CONSISTENCY_HARDENED" in text
    assert "browser_dom_automation_used: false" in text


def test_expected_pass_status_message_shape() -> None:
    assert expected_pass_status_message("abc") == "abc has passed"