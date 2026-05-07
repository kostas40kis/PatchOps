from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.chrome_fail_report_send_gate_rehearsal import (
    BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_ATTACHMENT_MISSING,
    BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_CONFIRMATION_MISMATCH,
    BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_CONFIRMATION_REQUIRED,
    BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_INVALID,
    BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_MISSING,
    BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH,
    BLOCKED_SEND_RISK,
    CONFIRM_CHROME_FAIL_REPORT_SEND,
    CONFIRM_CHROME_FAIL_REPORT_SEND_GATE_REHEARSAL,
    PASS_CHROME_FAIL_REPORT_SEND_GATE_READY,
    run_chrome_fail_report_send_gate_rehearsal,
    sha256_file,
    write_evidence,
)


def make_report(tmp_path: Path, content: str = "operator report\n") -> Path:
    report = tmp_path / "operator_report.txt"
    report.write_text(content, encoding="utf-8")
    return report


def passing_evidence(report: Path) -> dict[str, object]:
    return {
        "ok": True,
        "result_label": "PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT",
        "selected_action": "upload_operator_report",
        "browser_lane": "chrome",
        "patch_result": "FAIL",
        "runs_requested": 3,
        "runs_completed": 3,
        "runs_passed": 3,
        "consecutive_passes": 3,
        "attachment_verified_all_runs": True,
        "attachment_ready_all_runs": True,
        "file_upload_attempted_all_runs": True,
        "file_picker_used_all_runs": True,
        "file_path_written_all_runs": True,
        "operator_report_uploaded_any_run": False,
        "chatgpt_submit_performed_any_run": False,
        "status_message_posted_any_run": False,
        "send_button_pressed_any_run": False,
        "raw_conversation_text_available_any_run": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
        "cloudflare_bypass_attempted": False,
        "captcha_bypass_attempted": False,
        "base_operator_report_path": str(report),
        "base_operator_report_sha256": sha256_file(report),
    }


def run_ready(report: Path, **overrides: object):
    values = {
        "consistency_evidence_path": report.parent / "latest_chrome_operator_report_attach_consistency.json",
        "rehearsal_confirmation_text": CONFIRM_CHROME_FAIL_REPORT_SEND_GATE_REHEARSAL,
        "real_send_confirmation_text": None,
        "operator_report_path": None,
        "expected_operator_report_sha256": None,
    }
    if "consistency_evidence_payload" in overrides:
        values["consistency_evidence_payload"] = overrides.pop("consistency_evidence_payload")
    else:
        values["consistency_evidence_payload"] = passing_evidence(report)
    values.update(overrides)
    return run_chrome_fail_report_send_gate_rehearsal(**values)  # type: ignore[arg-type]

def test_send_gate_ready_from_consistency_evidence(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)

    assert result.ok is True
    assert result.result_label == PASS_CHROME_FAIL_REPORT_SEND_GATE_READY
    assert result.patch_result == "FAIL"
    assert result.selected_action == "upload_operator_report"
    assert result.browser_lane == "chrome"
    assert result.consistency_ok is True
    assert result.consistency_result_label == "PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT"
    assert result.consistency_runs_completed == 3
    assert result.consistency_runs_passed == 3
    assert result.consistency_consecutive_passes == 3
    assert result.attachment_verified_from_prior_evidence is True
    assert result.attachment_verified_all_runs is True
    assert result.file_upload_attempted_all_runs is True
    assert result.file_picker_used_all_runs is True
    assert result.file_path_written_all_runs is True
    assert result.send_gate_confirmation_required is True
    assert result.send_gate_rehearsal_confirmation_matched is True
    assert result.real_send_confirmation_required_for_next_patch == CONFIRM_CHROME_FAIL_REPORT_SEND
    assert result.real_send_confirmation_present is False
    assert result.real_send_confirmation_accepted_by_this_patch is False
    assert result.operator_report_path == str(report)
    assert result.operator_report_sha256 == sha256_file(report)
    assert result.computed_operator_report_sha256 == sha256_file(report)
    assert result.operator_report_hash_carried_forward is True
    assert result.operator_report_hash_verified_on_disk is True
    assert result.gate_ready is True
    assert result.delivery_gate_sha256 is not None
    assert result.browser_action_performed is False
    assert result.file_upload_attempted is False
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


def test_rehearsal_confirmation_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, rehearsal_confirmation_text=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_CONFIRMATION_REQUIRED
    assert result.browser_action_performed is False
    assert result.send_button_pressed is False


def test_rehearsal_confirmation_must_match(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, rehearsal_confirmation_text="WRONG")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_CONFIRMATION_MISMATCH
    assert result.gate_ready is False


def test_real_send_confirmation_is_refused_by_rehearsal(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, real_send_confirmation_text=CONFIRM_CHROME_FAIL_REPORT_SEND)

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.real_send_confirmation_present is True
    assert result.real_send_confirmation_accepted_by_this_patch is False
    assert result.send_button_pressed is False
    assert result.chatgpt_submit_performed is False


def test_consistency_evidence_is_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_chrome_fail_report_send_gate_rehearsal(
        consistency_evidence_payload=None,
        consistency_evidence_path=tmp_path / "missing.json",
        rehearsal_confirmation_text=CONFIRM_CHROME_FAIL_REPORT_SEND_GATE_REHEARSAL,
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_MISSING


def test_consistency_evidence_must_be_passed(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    evidence = passing_evidence(report)
    evidence["ok"] = False

    result = run_ready(report, consistency_evidence_payload=evidence)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_INVALID


def test_consistency_label_must_match(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    evidence = passing_evidence(report)
    evidence["result_label"] = "BLOCKED_CHROME_ATTACH_CONSISTENCY_FLAKY"

    result = run_ready(report, consistency_evidence_payload=evidence)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_INVALID


def test_browser_lane_must_be_chrome(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    evidence = passing_evidence(report)
    evidence["browser_lane"] = "edge"

    result = run_ready(report, consistency_evidence_payload=evidence)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_INVALID


def test_attachment_evidence_is_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    evidence = passing_evidence(report)
    evidence["attachment_verified_all_runs"] = False

    result = run_ready(report, consistency_evidence_payload=evidence)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_ATTACHMENT_MISSING


def test_forbidden_prior_send_or_submit_flags_block(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    evidence = passing_evidence(report)
    evidence["send_button_pressed_any_run"] = True

    result = run_ready(report, consistency_evidence_payload=evidence)

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.send_button_pressed is False
    assert result.chatgpt_submit_performed is False


def test_operator_report_hash_must_be_carried(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    evidence = passing_evidence(report)
    evidence["base_operator_report_sha256"] = ""

    result = run_ready(report, consistency_evidence_payload=evidence)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH
    assert result.operator_report_hash_carried_forward is False


def test_supplied_hash_must_match_evidence_hash(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, expected_operator_report_sha256="wrong")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH


def test_operator_report_file_must_still_exist(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    evidence = passing_evidence(report)
    report.unlink()

    result = run_ready(report, consistency_evidence_payload=evidence)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH
    assert result.operator_report_hash_carried_forward is True
    assert result.operator_report_hash_verified_on_disk is False


def test_computed_hash_must_match_carried_hash(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    evidence = passing_evidence(report)
    report.write_text("changed\n", encoding="utf-8")

    result = run_ready(report, consistency_evidence_payload=evidence)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH
    assert result.computed_operator_report_sha256 == sha256_file(report)
    assert result.operator_report_hash_verified_on_disk is False


def test_explicit_report_path_override_can_pass(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    evidence = passing_evidence(report)
    other = tmp_path / "operator_report_copy.txt"
    other.write_text(report.read_text(encoding="utf-8"), encoding="utf-8")

    result = run_ready(report, consistency_evidence_payload=evidence, operator_report_path=str(other), expected_operator_report_sha256=sha256_file(other))

    assert result.ok is True
    assert result.result_label == PASS_CHROME_FAIL_REPORT_SEND_GATE_READY
    assert result.operator_report_path == str(other)
    assert result.operator_report_sha256 == sha256_file(other)


def test_write_gate_evidence_has_no_browser_action(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)
    json_path = tmp_path / "send_gate.json"
    txt_path = tmp_path / "send_gate.txt"

    write_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_CHROME_FAIL_REPORT_SEND_GATE_READY
    assert payload["gate_ready"] is True
    assert payload["real_send_confirmation_required_for_next_patch"] == CONFIRM_CHROME_FAIL_REPORT_SEND
    assert payload["real_send_confirmation_accepted_by_this_patch"] is False
    assert payload["browser_action_performed"] is False
    assert payload["file_upload_attempted"] is False
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
    assert "result_label: PASS_CHROME_FAIL_REPORT_SEND_GATE_READY" in text
    assert "gate_ready: true" in text
    assert "send_button_pressed: false" in text
    assert "browser_dom_automation_used: false" in text