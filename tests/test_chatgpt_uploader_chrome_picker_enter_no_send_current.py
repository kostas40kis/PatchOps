from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_picker_enter_no_send import (
    BLOCKED_PATH_NOT_WRITTEN,
    BLOCKED_PICKER_ENTER_CONFIRMATION_MISSING,
    BLOCKED_PICKER_NOT_READY,
    FAIL_PATH_ENTER_FAILED,
    FAIL_PICKER_NOT_CLOSED_AFTER_ENTER,
    LIVE_CONFIRM_TEXT,
    PASS_CHROME_PICKER_ENTERED_NO_SEND,
    build_picker_enter_plan,
    run_picker_enter_no_send,
    write_picker_enter_no_send_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _report(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "PatchOps operator report\n=======================\nfinal result      : PASS\nSafety flags\n------------\n",
        encoding="utf-8",
    )
    return path


def test_picker_enter_plan_allows_one_enter_only_after_path_write(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    plan = build_picker_enter_plan(report)

    assert plan.ok is True
    assert plan.result == "PASS_PICKER_ENTER_PLAN_READY"
    assert plan.allow_enter_press is True
    assert plan.allow_open_button_press is False
    assert plan.allow_send is False
    assert plan.allow_attachment_claim is False
    assert plan.max_enter_presses == 1
    assert plan.sequence[-1] == "stop_before_send"


def test_picker_enter_blocks_when_picker_not_ready(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence = run_picker_enter_no_send(
        canonical_report_path=report,
        picker_ready=False,
        path_written_before_enter=True,
        mock_enter_success=True,
        mock_picker_closed_after_enter=True,
    )

    assert evidence.ok is False
    assert evidence.result == BLOCKED_PICKER_NOT_READY
    assert evidence.enter_pressed is False
    assert evidence.file_upload_attempted is False
    assert evidence.chatgpt_submit_performed is False


def test_picker_enter_blocks_when_path_was_not_written(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence = run_picker_enter_no_send(
        canonical_report_path=report,
        picker_ready=True,
        path_written_before_enter=False,
        mock_enter_success=True,
        mock_picker_closed_after_enter=True,
    )

    assert evidence.ok is False
    assert evidence.result == BLOCKED_PATH_NOT_WRITTEN
    assert evidence.enter_pressed is False
    assert evidence.file_upload_attempted is False


def test_picker_enter_mock_success_records_upload_attempt_but_no_send(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence = run_picker_enter_no_send(
        canonical_report_path=report,
        picker_ready=True,
        picker_hwnd=123,
        path_written_before_enter=True,
        mock_enter_success=True,
        mock_picker_closed_after_enter=True,
    )

    assert evidence.ok is True
    assert evidence.result == PASS_CHROME_PICKER_ENTERED_NO_SEND
    assert evidence.enter_pressed is True
    assert evidence.picker_closed_after_enter is True
    assert evidence.file_upload_attempted is True
    assert evidence.open_button_pressed is False
    assert evidence.chatgpt_submit_performed is False
    assert evidence.attachment_confirmed is False
    assert evidence.raw_conversation_text_logged is False
    assert evidence.safety_flags["selenium_used"] is False
    assert evidence.safety_flags["webdriver_used"] is False
    assert evidence.safety_flags["browser_dom_automation_used"] is False
    assert str(report.resolve()) not in json.dumps(evidence.to_payload())


def test_picker_enter_mock_not_closed_is_failure_no_send(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence = run_picker_enter_no_send(
        canonical_report_path=report,
        picker_ready=True,
        picker_hwnd=123,
        path_written_before_enter=True,
        mock_enter_success=True,
        mock_picker_closed_after_enter=False,
    )

    assert evidence.ok is False
    assert evidence.result == FAIL_PICKER_NOT_CLOSED_AFTER_ENTER
    assert evidence.enter_pressed is True
    assert evidence.file_upload_attempted is True
    assert evidence.chatgpt_submit_performed is False
    assert evidence.attachment_confirmed is False


def test_picker_enter_without_live_or_mock_is_failed_safely(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence = run_picker_enter_no_send(
        canonical_report_path=report,
        picker_ready=True,
        path_written_before_enter=True,
    )

    assert evidence.ok is False
    assert evidence.result == FAIL_PATH_ENTER_FAILED
    assert evidence.enter_pressed is False
    assert evidence.file_upload_attempted is False
    assert evidence.chatgpt_submit_performed is False


def test_live_picker_enter_requires_confirmation_and_allow_flag(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence = run_picker_enter_no_send(
        canonical_report_path=report,
        picker_ready=True,
        picker_hwnd=123,
        path_written_before_enter=True,
        live_browser=True,
        allow_picker_enter=True,
        confirm_live_browser_text="wrong",
    )

    assert evidence.ok is False
    assert evidence.result == BLOCKED_PICKER_ENTER_CONFIRMATION_MISSING
    assert LIVE_CONFIRM_TEXT in evidence.reason
    assert evidence.live_browser_used is False
    assert evidence.enter_pressed is False


def test_write_picker_enter_no_send_evidence_roundtrip(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence = run_picker_enter_no_send(
        canonical_report_path=report,
        picker_ready=True,
        path_written_before_enter=True,
        mock_enter_success=True,
        mock_picker_closed_after_enter=True,
    )
    output = write_picker_enter_no_send_evidence(evidence, tmp_path / "enter" / "evidence.json")

    payload_text = output.read_text(encoding="utf-8")
    payload = json.loads(payload_text)
    assert payload["result"] == PASS_CHROME_PICKER_ENTERED_NO_SEND
    assert payload["enter_pressed"] is True
    assert payload["file_upload_attempted"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert payload["attachment_confirmed"] is False
    assert str(report.resolve()) not in payload_text


def test_picker_enter_script_mock_success(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence_path = tmp_path / "enter.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_press_picker_enter_no_send.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(report),
            "--picker-ready",
            "--path-written-before-enter",
            "--mock-enter-success",
            "--mock-picker-closed-after-enter",
            "--evidence-path",
            str(evidence_path),
            "--json",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == PASS_CHROME_PICKER_ENTERED_NO_SEND
    assert payload["enter_pressed"] is True
    assert payload["file_upload_attempted"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert str(report.resolve()) not in result.stdout

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["result"] == PASS_CHROME_PICKER_ENTERED_NO_SEND


def test_picker_enter_script_blocks_without_path_written(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_press_picker_enter_no_send.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(report),
            "--picker-ready",
            "--mock-enter-success",
            "--mock-picker-closed-after-enter",
            "--json",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_PATH_NOT_WRITTEN
    assert payload["enter_pressed"] is False


def test_picker_enter_script_live_without_confirmation_blocks(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_press_picker_enter_no_send.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(report),
            "--picker-ready",
            "--picker-hwnd",
            "123",
            "--path-written-before-enter",
            "--live-browser",
            "--allow-picker-enter",
            "--json",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_PICKER_ENTER_CONFIRMATION_MISSING
    assert payload["live_browser_used"] is False
    assert payload["enter_pressed"] is False


def test_chrome_picker_enter_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_picker_enter_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_picker_enter_no_send.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_press_picker_enter_no_send.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text