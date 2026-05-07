from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_picker_path_entry import (
    BLOCKED_CANONICAL_REPORT_MISSING,
    BLOCKED_PATH_ENTRY_CONFIRMATION_MISSING,
    BLOCKED_PATH_NOT_CANONICAL_REPORT,
    BLOCKED_PICKER_NOT_READY,
    LIVE_CONFIRM_TEXT,
    PASS_PICKER_PATH_ENTRY_PLAN_READY,
    PASS_PICKER_PATH_WRITTEN_NO_OPEN,
    build_picker_path_entry_plan,
    hash_path,
    run_picker_path_entry,
    validate_canonical_report_path,
    write_picker_path_entry_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _report(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "PatchOps operator report\n=======================\nfinal result      : PASS\nSafety flags\n------------\n",
        encoding="utf-8",
    )
    return path


def test_validate_canonical_report_path_accepts_patchops_report(tmp_path: Path) -> None:
    report = _report(tmp_path / "patchops_report.txt")
    evidence = validate_canonical_report_path(report)

    assert evidence.ok is True
    assert evidence.result == "PASS_CANONICAL_REPORT_PATH_VALIDATED"
    assert evidence.exists is True
    assert evidence.is_file is True
    assert evidence.suffix == ".txt"
    assert evidence.basename == "patchops_report.txt"
    assert evidence.path_hash == hash_path(report)
    assert evidence.marker_detected is True


def test_validate_canonical_report_path_blocks_missing() -> None:
    evidence = validate_canonical_report_path("missing_report.txt")

    assert evidence.ok is False
    assert evidence.result == BLOCKED_CANONICAL_REPORT_MISSING
    assert evidence.exists is False


def test_validate_canonical_report_path_blocks_non_report_text(tmp_path: Path) -> None:
    path = tmp_path / "not_report.txt"
    path.write_text("hello world", encoding="utf-8")

    evidence = validate_canonical_report_path(path)

    assert evidence.ok is False
    assert evidence.result == BLOCKED_PATH_NOT_CANONICAL_REPORT
    assert evidence.marker_detected is False


def test_picker_path_entry_plan_stops_before_open_upload_send(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    plan = build_picker_path_entry_plan(report)

    assert plan.ok is True
    assert plan.result == PASS_PICKER_PATH_ENTRY_PLAN_READY
    assert plan.max_attempts == 1
    assert plan.allow_path_write is True
    assert plan.allow_open_press is False
    assert plan.allow_enter_press is False
    assert plan.allow_upload_claim is False
    assert plan.allow_send is False
    assert plan.sequence[-1] == "stop_before_open"


def test_path_entry_blocks_when_picker_not_ready(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence = run_picker_path_entry(canonical_report_path=report, picker_ready=False)

    assert evidence.ok is False
    assert evidence.result == BLOCKED_PICKER_NOT_READY
    assert evidence.file_path_written is False
    assert evidence.open_button_pressed is False
    assert evidence.enter_pressed is False
    assert evidence.file_upload_attempted is False
    assert evidence.chatgpt_submit_performed is False


def test_path_entry_local_plan_ready_without_mock_write(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence = run_picker_path_entry(canonical_report_path=report, picker_ready=True)

    assert evidence.ok is True
    assert evidence.result == PASS_PICKER_PATH_ENTRY_PLAN_READY
    assert evidence.file_path_written is False
    assert evidence.path_hash_written is None
    assert evidence.open_button_pressed is False
    assert evidence.file_selected is False
    assert evidence.file_upload_attempted is False
    assert evidence.chatgpt_submit_performed is False


def test_path_entry_mock_write_success_records_hash_only(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence = run_picker_path_entry(canonical_report_path=report, picker_ready=True, mock_write_success=True)

    assert evidence.ok is True
    assert evidence.result == PASS_PICKER_PATH_WRITTEN_NO_OPEN
    assert evidence.file_path_written is True
    assert evidence.path_hash_written == hash_path(report)
    assert evidence.basename_written == "operator.txt"
    assert str(report.resolve()) not in json.dumps(evidence.to_payload())
    assert evidence.open_button_pressed is False
    assert evidence.enter_pressed is False
    assert evidence.file_selected is False
    assert evidence.file_upload_attempted is False
    assert evidence.chatgpt_submit_performed is False
    assert evidence.raw_conversation_text_logged is False


def test_live_path_entry_requires_explicit_confirmation_and_allow_flag(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence = run_picker_path_entry(
        canonical_report_path=report,
        picker_ready=True,
        picker_hwnd=123,
        live_browser=True,
        confirm_live_browser_text="wrong",
        allow_picker_path_write=True,
    )

    assert evidence.ok is False
    assert evidence.result == BLOCKED_PATH_ENTRY_CONFIRMATION_MISSING
    assert LIVE_CONFIRM_TEXT in evidence.reason
    assert evidence.live_browser_used is False
    assert evidence.file_path_written is False


def test_write_picker_path_entry_evidence_roundtrip(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence = run_picker_path_entry(canonical_report_path=report, picker_ready=True, mock_write_success=True)
    output = write_picker_path_entry_evidence(evidence, tmp_path / "entry" / "evidence.json")

    payload_text = output.read_text(encoding="utf-8")
    payload = json.loads(payload_text)
    assert payload["result"] == PASS_PICKER_PATH_WRITTEN_NO_OPEN
    assert payload["file_path_written"] is True
    assert payload["open_button_pressed"] is False
    assert payload["enter_pressed"] is False
    assert payload["file_selected"] is False
    assert payload["file_upload_attempted"] is False
    assert str(report.resolve()) not in payload_text


def test_write_picker_path_script_mock_success(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    evidence_path = tmp_path / "path_entry.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_write_picker_path_live.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(report),
            "--picker-ready",
            "--mock-write-success",
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
    assert payload["result"] == PASS_PICKER_PATH_WRITTEN_NO_OPEN
    assert payload["file_path_written"] is True
    assert payload["open_button_pressed"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert str(report.resolve()) not in result.stdout

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["result"] == PASS_PICKER_PATH_WRITTEN_NO_OPEN


def test_write_picker_path_script_blocks_missing_report_zero_exit(tmp_path: Path) -> None:
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_write_picker_path_live.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(tmp_path / "missing.txt"),
            "--picker-ready",
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
    assert payload["result"] == BLOCKED_CANONICAL_REPORT_MISSING
    assert payload["file_path_written"] is False


def test_write_picker_path_script_live_without_confirmation_blocks(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator.txt")
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_write_picker_path_live.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(report),
            "--picker-ready",
            "--picker-hwnd",
            "123",
            "--live-browser",
            "--allow-picker-path-write",
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
    assert payload["result"] == BLOCKED_PATH_ENTRY_CONFIRMATION_MISSING
    assert payload["live_browser_used"] is False
    assert payload["file_path_written"] is False


def test_chrome_picker_path_entry_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_picker_path_entry_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_picker_path_entry.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_write_picker_path_live.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text