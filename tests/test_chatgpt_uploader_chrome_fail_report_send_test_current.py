from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.chrome_fail_report_send_test import (
    BLOCKED_CHROME_FAIL_REPORT_SEND_ATTACH_FAILED,
    BLOCKED_CHROME_FAIL_REPORT_SEND_BUTTON_NOT_READY,
    BLOCKED_CHROME_FAIL_REPORT_SEND_CONFIRMATION_MISMATCH,
    BLOCKED_CHROME_FAIL_REPORT_SEND_CONFIRMATION_REQUIRED,
    BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_INVALID,
    BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_MISSING,
    BLOCKED_CHROME_FAIL_REPORT_SEND_HASH_MISMATCH,
    BLOCKED_CHROME_FAIL_REPORT_SEND_LIVE_BROWSER_REQUIRED,
    CONFIRM_CHROME_FAIL_REPORT_SEND,
    FAIL_CHROME_FAIL_REPORT_SEND_NOT_PROVEN,
    PASS_CHROME_FAIL_REPORT_SENT,
    run_chrome_fail_report_send_test,
    sha256_file,
    write_evidence,
)
from patchops.chatgpt_uploader.chrome_operator_report_attach_no_send import sha256_text

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


def ready_gate(report: Path) -> dict[str, object]:
    return {
        "ok": True,
        "result_label": "PASS_CHROME_FAIL_REPORT_SEND_GATE_READY",
        "gate_ready": True,
        "selected_action": "upload_operator_report",
        "browser_lane": "chrome",
        "real_send_confirmation_required_for_next_patch": CONFIRM_CHROME_FAIL_REPORT_SEND,
        "real_send_confirmation_accepted_by_this_patch": False,
        "browser_action_performed": False,
        "send_button_pressed": False,
        "operator_report_path": str(report),
        "operator_report_sha256": sha256_file(report),
        "delivery_gate_sha256": "gatehash",
    }


def run_ready(report: Path, **overrides: object):
    values = {
        "config_payload": ready_config(),
        "config_path": report.parent / "uploader_status_target_config.json",
        "send_gate_path": report.parent / "latest_chrome_fail_report_send_gate_ready.json",
        "provider": "fake-ready",
        "live_browser": True,
        "confirmation_text": CONFIRM_CHROME_FAIL_REPORT_SEND,
        "operator_report_path": None,
        "expected_operator_report_sha256": None,
    }
    if "send_gate_payload" in overrides:
        values["send_gate_payload"] = overrides.pop("send_gate_payload")
    else:
        values["send_gate_payload"] = ready_gate(report)
    values.update(overrides)
    return run_chrome_fail_report_send_test(**values)  # type: ignore[arg-type]

def test_fake_ready_attaches_and_sends(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)

    assert result.ok is True
    assert result.result_label == PASS_CHROME_FAIL_REPORT_SENT
    assert result.selected_action == "upload_operator_report"
    assert result.browser_lane == "chrome"
    assert result.live_browser is True
    assert result.send_confirmation_matched is True
    assert result.send_gate_ready is True
    assert result.operator_report_path == str(report)
    assert result.operator_report_sha256 == sha256_file(report)
    assert result.computed_operator_report_sha256 == sha256_file(report)
    assert result.operator_report_hash_verified_on_disk is True
    assert result.attachment_result_label == "PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND"
    assert result.attachment_verified is True
    assert result.attachment_ready is True
    assert result.file_upload_attempted is True
    assert result.file_picker_used is True
    assert result.file_path_written is True
    assert result.chrome_target_focused is True
    assert result.send_button_ready is True
    assert result.send_button_candidate_count == 1
    assert result.send_button_pressed is True
    assert result.chatgpt_submit_performed is True
    assert result.operator_report_uploaded is True
    assert result.status_message_posted is False
    assert result.browser_action_performed is True
    assert result.raw_conversation_text_available is False
    assert result.selenium_used is False
    assert result.webdriver_used is False
    assert result.browser_dom_automation_used is False
    assert result.cloudflare_bypass_attempted is False
    assert result.captcha_bypass_attempted is False
    assert result.safety.conversation_text_logged is False
    assert result.safety.random_page_click_performed is False


def test_send_gate_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, send_gate_payload=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_MISSING
    assert result.send_button_pressed is False


def test_send_gate_must_be_valid(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    gate = ready_gate(report)
    gate["gate_ready"] = False

    result = run_ready(report, send_gate_payload=gate)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_INVALID
    assert result.browser_action_performed is False


def test_confirmation_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, confirmation_text=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_CONFIRMATION_REQUIRED
    assert result.send_button_pressed is False


def test_confirmation_must_match(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, confirmation_text="WRONG")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_CONFIRMATION_MISMATCH
    assert result.send_button_pressed is False


def test_live_browser_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, live_browser=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_LIVE_BROWSER_REQUIRED
    assert result.send_button_pressed is False


def test_operator_report_file_must_exist(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    gate = ready_gate(report)
    report.unlink()

    result = run_ready(report, send_gate_payload=gate)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_HASH_MISMATCH
    assert result.operator_report_hash_verified_on_disk is False
    assert result.send_button_pressed is False


def test_operator_report_hash_must_match(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    gate = ready_gate(report)
    report.write_text("changed\n", encoding="utf-8")

    result = run_ready(report, send_gate_payload=gate)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_HASH_MISMATCH
    assert result.computed_operator_report_sha256 == sha256_file(report)
    assert result.send_button_pressed is False


def test_explicit_report_hash_override_can_pass(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    other = tmp_path / "other_report.txt"
    other.write_text("other report\n", encoding="utf-8")

    result = run_ready(report, operator_report_path=str(other), expected_operator_report_sha256=sha256_file(other))

    assert result.ok is True
    assert result.result_label == PASS_CHROME_FAIL_REPORT_SENT
    assert result.operator_report_path == str(other)
    assert result.operator_report_sha256 == sha256_file(other)


def test_attach_failure_blocks_before_send(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    bad_config = ready_config()
    bad_config["status_chat"]["browser_lane"] = "edge"  # type: ignore[index]

    result = run_ready(report, config_payload=bad_config)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_ATTACH_FAILED
    assert result.send_button_pressed is False
    assert result.operator_report_uploaded is False


def test_send_button_missing_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-send-button-missing")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_BUTTON_NOT_READY
    assert result.attachment_verified is True
    assert result.send_button_pressed is False
    assert result.operator_report_uploaded is False


def test_send_not_proven_fails(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-send-not-proven")

    assert result.ok is False
    assert result.result_label == FAIL_CHROME_FAIL_REPORT_SEND_NOT_PROVEN
    assert result.send_button_ready is True
    assert result.send_button_pressed is True
    assert result.chatgpt_submit_performed is False
    assert result.operator_report_uploaded is False


def test_write_send_evidence(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)
    json_path = tmp_path / "sent.json"
    txt_path = tmp_path / "sent.txt"

    write_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_CHROME_FAIL_REPORT_SENT
    assert payload["send_gate_ready"] is True
    assert payload["attachment_verified"] is True
    assert payload["file_upload_attempted"] is True
    assert payload["send_button_pressed"] is True
    assert payload["chatgpt_submit_performed"] is True
    assert payload["operator_report_uploaded"] is True
    assert payload["status_message_posted"] is False
    assert payload["raw_conversation_text_available"] is False
    assert payload["selenium_used"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
    assert payload["cloudflare_bypass_attempted"] is False
    assert payload["captcha_bypass_attempted"] is False
    raw_json = json_path.read_text(encoding="utf-8")
    assert TARGET_URL not in raw_json
    assert "Google Chrome" not in raw_json

    text = txt_path.read_text(encoding="utf-8")
    assert "result_label: PASS_CHROME_FAIL_REPORT_SENT" in text
    assert "send_button_pressed: true" in text
    assert "operator_report_uploaded: true" in text
    assert "browser_dom_automation_used: false" in text