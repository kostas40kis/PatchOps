from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.chrome_operator_report_attach_consistency import (
    BLOCKED_CHROME_ATTACH_CONSISTENCY_CONFIRMATION_MISMATCH,
    BLOCKED_CHROME_ATTACH_CONSISTENCY_CONFIRMATION_REQUIRED,
    BLOCKED_CHROME_ATTACH_CONSISTENCY_EVIDENCE_MISSING,
    BLOCKED_CHROME_ATTACH_CONSISTENCY_FLAKY,
    BLOCKED_CHROME_ATTACH_CONSISTENCY_INSUFFICIENT_RUNS,
    BLOCKED_CHROME_ATTACH_CONSISTENCY_LIVE_BROWSER_REQUIRED,
    BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_HASH_MISMATCH,
    BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_MISSING,
    BLOCKED_CHROME_ATTACH_CONSISTENCY_SEND_RISK,
    BLOCKED_CHROME_ATTACH_CONSISTENCY_STOP_BEFORE_SEND_REQUIRED,
    CONFIRM_CHROME_ATTACH_CONSISTENCY,
    MIN_RUNS_REQUIRED,
    PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT,
    run_chrome_operator_report_attach_consistency,
    sha256_file,
    write_consistency_evidence,
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


def run_ready(report: Path, **overrides: object):
    values = {
        "config_payload": ready_config(),
        "provider": "fake-ready",
        "live_browser": True,
        "stop_before_send": True,
        "confirmation_text": CONFIRM_CHROME_ATTACH_CONSISTENCY,
        "operator_report_path": str(report),
        "expected_operator_report_sha256": sha256_file(report),
        "runs": MIN_RUNS_REQUIRED,
        "run_evidence_dir": report.parent / "evidence",
        "work_dir": report.parent / "work",
        "use_fresh_copies": True,
        "inter_run_delay_seconds": 0,
    }
    values.update(overrides)
    return run_chrome_operator_report_attach_consistency(**values)  # type: ignore[arg-type]


def test_three_consecutive_fake_ready_runs_pass(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)

    assert result.ok is True
    assert result.result_label == PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT
    assert result.selected_action == "upload_operator_report"
    assert result.browser_lane == "chrome"
    assert result.patch_result == "FAIL"
    assert result.runs_requested == 3
    assert result.runs_completed == 3
    assert result.runs_passed == 3
    assert result.consecutive_passes == 3
    assert result.attachment_verified_all_runs is True
    assert result.attachment_ready_all_runs is True
    assert result.file_upload_attempted_all_runs is True
    assert result.file_picker_used_all_runs is True
    assert result.file_path_written_all_runs is True
    assert result.operator_report_uploaded_any_run is False
    assert result.chatgpt_submit_performed_any_run is False
    assert result.status_message_posted_any_run is False
    assert result.send_button_pressed_any_run is False
    assert result.raw_conversation_text_available_any_run is False
    assert result.selenium_used is False
    assert result.webdriver_used is False
    assert result.browser_dom_automation_used is False
    assert result.cloudflare_bypass_attempted is False
    assert result.captcha_bypass_attempted is False
    assert result.browser_action_performed is True
    assert result.file_upload_attempted is True
    assert result.operator_report_uploaded is False
    assert result.chatgpt_submit_performed is False
    assert result.status_message_posted is False
    assert result.send_button_pressed is False
    assert result.raw_conversation_text_available is False
    assert len(result.run_results) == 3
    assert all(Path(run.evidence_json_path).exists() for run in result.run_results)
    assert all(Path(run.evidence_txt_path).exists() for run in result.run_results)
    assert len({run.operator_report_path for run in result.run_results}) == 3


def test_can_run_without_fresh_copies(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, use_fresh_copies=False)

    assert result.ok is True
    assert result.use_fresh_copies is False
    assert len({run.operator_report_path for run in result.run_results}) == 1
    assert result.base_operator_report_sha256 == sha256_file(report)


def test_live_browser_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, live_browser=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONSISTENCY_LIVE_BROWSER_REQUIRED
    assert result.runs_completed == 0
    assert result.file_upload_attempted is False


def test_stop_before_send_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, stop_before_send=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONSISTENCY_STOP_BEFORE_SEND_REQUIRED
    assert result.runs_completed == 0
    assert result.send_button_pressed is False


def test_confirmation_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, confirmation_text=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONSISTENCY_CONFIRMATION_REQUIRED
    assert result.runs_completed == 0


def test_confirmation_must_match(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, confirmation_text="WRONG")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONSISTENCY_CONFIRMATION_MISMATCH
    assert result.runs_completed == 0


def test_requires_at_least_three_runs(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, runs=2)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONSISTENCY_INSUFFICIENT_RUNS
    assert result.runs_completed == 0


def test_requires_existing_operator_report(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    result = run_chrome_operator_report_attach_consistency(
        config_payload=ready_config(),
        provider="fake-ready",
        live_browser=True,
        stop_before_send=True,
        confirmation_text=CONFIRM_CHROME_ATTACH_CONSISTENCY,
        operator_report_path=str(missing),
        expected_operator_report_sha256=None,
        runs=3,
        run_evidence_dir=tmp_path / "evidence",
        work_dir=tmp_path / "work",
        use_fresh_copies=True,
        inter_run_delay_seconds=0,
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_MISSING
    assert result.runs_completed == 0


def test_report_hash_must_match(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, expected_operator_report_sha256="wrong")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_HASH_MISMATCH
    assert result.base_operator_report_sha256 == sha256_file(report)
    assert result.runs_completed == 0


def test_flaky_child_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-attachment-not-verified")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONSISTENCY_FLAKY
    assert result.runs_completed == 1
    assert result.runs_passed == 0
    assert result.attachment_verified_all_runs is False
    assert "run 1 failed" in result.issues[0]


def test_send_risk_blocks_immediately(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-send-risk")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONSISTENCY_SEND_RISK
    assert result.runs_completed == 1
    assert result.send_button_pressed_any_run is False
    assert result.operator_report_uploaded_any_run is False
    assert result.chatgpt_submit_performed_any_run is False
    assert result.send_button_pressed is False
    assert result.operator_report_uploaded is False
    assert result.chatgpt_submit_performed is False


def test_child_target_failure_is_flaky_not_pass(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-no-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_ATTACH_CONSISTENCY_FLAKY
    assert result.runs_completed == 1
    assert result.runs_passed == 0


def test_write_consistency_evidence(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)
    json_path = tmp_path / "consistency.json"
    txt_path = tmp_path / "consistency.txt"

    write_consistency_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT
    assert payload["runs_requested"] == 3
    assert payload["runs_passed"] == 3
    assert payload["consecutive_passes"] == 3
    assert payload["attachment_verified_all_runs"] is True
    assert payload["file_upload_attempted_all_runs"] is True
    assert payload["operator_report_uploaded_any_run"] is False
    assert payload["chatgpt_submit_performed_any_run"] is False
    assert payload["status_message_posted_any_run"] is False
    assert payload["send_button_pressed_any_run"] is False
    assert payload["raw_conversation_text_available_any_run"] is False
    assert payload["selenium_used"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
    assert payload["cloudflare_bypass_attempted"] is False
    assert payload["captcha_bypass_attempted"] is False
    assert payload["browser_action_performed"] is True
    assert payload["file_upload_attempted"] is True
    assert payload["operator_report_uploaded"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["status_message_posted"] is False
    assert payload["send_button_pressed"] is False
    assert payload["raw_conversation_text_available"] is False
    assert len(payload["run_results"]) == 3

    raw_json = json_path.read_text(encoding="utf-8")
    assert TARGET_URL not in raw_json
    text = txt_path.read_text(encoding="utf-8")
    assert "result_label: PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT" in text
    assert "runs_passed: 3" in text
    assert "send_button_pressed_any_run: false" in text
    assert "browser_dom_automation_used: false" in text


def test_evidence_missing_label_constant_is_exported() -> None:
    assert BLOCKED_CHROME_ATTACH_CONSISTENCY_EVIDENCE_MISSING == "BLOCKED_CHROME_ATTACH_CONSISTENCY_EVIDENCE_MISSING"