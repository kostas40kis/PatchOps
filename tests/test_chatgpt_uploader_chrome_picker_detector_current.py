from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_picker_trigger import (
    BLOCKED_AMBIGUOUS_PICKER,
    BLOCKED_LIVE_BROWSER_CONFIRMATION_MISSING,
    BLOCKED_PICKER_ERROR_MODAL,
    LIVE_CONFIRM_TEXT,
    PASS_NO_PICKER,
    PASS_ONE_PICKER_DETECTED,
    adapt_windows_picker_detection,
    build_picker_candidate,
    evaluate_chrome_picker_detection,
    run_chrome_picker_detector,
    write_chrome_picker_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_no_picker_is_safe_pass_without_side_effects() -> None:
    evidence = evaluate_chrome_picker_detection([])

    assert evidence.ok is True
    assert evidence.result == PASS_NO_PICKER
    assert evidence.picker_detected is False
    assert evidence.picker_count == 0
    assert evidence.error_modal_detected is False
    assert evidence.raw_conversation_text_logged is False
    assert evidence.file_path_written is False
    assert evidence.open_button_pressed is False
    assert evidence.file_upload_attempted is False
    assert evidence.chatgpt_submit_performed is False
    assert evidence.safety_flags["selenium_used"] is False
    assert evidence.safety_flags["webdriver_used"] is False
    assert evidence.safety_flags["browser_dom_automation_used"] is False


def test_one_picker_detected_records_chrome_owner_when_known() -> None:
    picker = build_picker_candidate(handle=22, owner_handle=10, expected_chrome_hwnd=10)
    evidence = evaluate_chrome_picker_detection([picker], expected_chrome_hwnd=10)

    assert evidence.ok is True
    assert evidence.result == PASS_ONE_PICKER_DETECTED
    assert evidence.picker_detected is True
    assert evidence.picker_count == 1
    assert evidence.picker_owned_by_expected_chrome_flow is True
    assert evidence.selected_picker is not None
    assert evidence.selected_picker["selected"] is True
    assert evidence.selected_picker["handle"] == 22


def test_one_picker_owner_unknown_is_not_false_claim() -> None:
    picker = build_picker_candidate(handle=22, owner_handle=None, expected_chrome_hwnd=10)
    evidence = evaluate_chrome_picker_detection([picker], expected_chrome_hwnd=10)

    assert evidence.result == PASS_ONE_PICKER_DETECTED
    assert evidence.picker_owned_by_expected_chrome_flow is None


def test_multiple_pickers_block_ambiguous() -> None:
    evidence = evaluate_chrome_picker_detection([
        build_picker_candidate(handle=1),
        build_picker_candidate(handle=2),
    ])

    assert evidence.ok is False
    assert evidence.result == BLOCKED_AMBIGUOUS_PICKER
    assert evidence.ambiguous is True
    assert evidence.selected_picker is None
    assert all(candidate.selected is False for candidate in evidence.picker_candidates)


def test_error_modal_blocks_before_picker_selection() -> None:
    picker = build_picker_candidate(handle=1)
    error = build_picker_candidate(handle=99, title_sha256="error-title")
    evidence = evaluate_chrome_picker_detection([picker], error_modal_candidates=[error])

    assert evidence.ok is False
    assert evidence.result == BLOCKED_PICKER_ERROR_MODAL
    assert evidence.error_modal_detected is True
    assert evidence.error_modal_count == 1
    assert evidence.selected_picker is None


def test_adapts_existing_windows_picker_detection_payload() -> None:
    payload = {
        "status": "PASS_PICKER_DETECTED",
        "picker_detected": True,
        "picker_count": 1,
        "ambiguous": False,
        "error_modal_detected": False,
        "error_modal_count": 0,
        "selected_picker": {
            "handle": 501,
            "owner_handle": 100,
            "class_name": "#32770",
            "title_sha256": "abc",
            "title_length": 4,
            "visible": True,
            "enabled": True,
            "child_class_counts": {"Edit": 1, "Button": 1},
        },
        "picker_candidates": [],
        "error_modal_candidates": [],
        "observed_window_count": 3,
        "reason": "single_file_picker_candidate_detected",
    }

    evidence = adapt_windows_picker_detection(payload, expected_chrome_hwnd=100)

    assert evidence.result == PASS_ONE_PICKER_DETECTED
    assert evidence.picker_count == 1
    assert evidence.selected_picker is not None
    assert evidence.selected_picker["handle"] == 501
    assert evidence.picker_owned_by_expected_chrome_flow is True
    assert evidence.observed_window_count == 3


def test_adapts_windows_error_modal_to_blocked_label() -> None:
    payload = {
        "status": "PASS_ERROR_MODAL_DETECTED",
        "picker_detected": False,
        "picker_count": 0,
        "ambiguous": False,
        "error_modal_detected": True,
        "error_modal_count": 1,
        "selected_picker": None,
        "picker_candidates": [],
        "error_modal_candidates": [
            {
                "handle": 77,
                "owner_handle": 100,
                "class_name": "#32770",
                "title_sha256": "err",
                "title_length": 12,
                "visible": True,
                "enabled": True,
                "child_class_counts": {"Button": 1},
            }
        ],
        "observed_window_count": 4,
    }

    evidence = adapt_windows_picker_detection(payload, expected_chrome_hwnd=100)
    assert evidence.result == BLOCKED_PICKER_ERROR_MODAL
    assert evidence.error_modal_detected is True
    assert evidence.error_modal_count == 1


def test_live_mode_requires_explicit_confirmation() -> None:
    evidence = run_chrome_picker_detector(live_browser=True, confirm_live_browser_text="wrong")

    assert evidence.ok is False
    assert evidence.result == BLOCKED_LIVE_BROWSER_CONFIRMATION_MISSING
    assert evidence.live_browser_used is False
    assert LIVE_CONFIRM_TEXT in evidence.reason
    assert evidence.file_path_written is False
    assert evidence.chatgpt_submit_performed is False


def test_write_chrome_picker_evidence_roundtrip(tmp_path: Path) -> None:
    evidence = evaluate_chrome_picker_detection([build_picker_candidate(handle=11)])
    output = write_chrome_picker_evidence(evidence, tmp_path / "picker" / "evidence.json")

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["result"] == PASS_ONE_PICKER_DETECTED
    assert payload["expected_browser"] == "chrome"
    assert payload["file_path_written"] is False
    assert payload["open_button_pressed"] is False
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["raw_conversation_text_logged"] is False


def test_detect_picker_script_mock_one_picker(tmp_path: Path) -> None:
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_detect_picker_live.py"
    evidence_path = tmp_path / "picker.json"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--expected-chrome-hwnd",
            "100",
            "--mock-picker",
            "501|100|true|true|abc",
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
    assert payload["result"] == PASS_ONE_PICKER_DETECTED
    assert payload["picker_owned_by_expected_chrome_flow"] is True
    assert payload["file_path_written"] is False
    assert payload["chatgpt_submit_performed"] is False

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["result"] == PASS_ONE_PICKER_DETECTED
    assert evidence["open_button_pressed"] is False


def test_detect_picker_script_mock_ambiguous_zero_exit_blocked_label() -> None:
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_detect_picker_live.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--mock-picker",
            "1||true|true|a",
            "--mock-picker",
            "2||true|true|b",
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
    assert payload["result"] == BLOCKED_AMBIGUOUS_PICKER
    assert payload["ambiguous"] is True
    assert payload["file_path_written"] is False


def test_detect_picker_script_live_without_confirmation_blocks() -> None:
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_detect_picker_live.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--live-browser",
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
    assert payload["result"] == BLOCKED_LIVE_BROWSER_CONFIRMATION_MISSING
    assert payload["live_browser_used"] is False
    assert LIVE_CONFIRM_TEXT in payload["reason"]


def test_chrome_picker_detector_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_picker_detector_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_picker_trigger.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_detect_picker_live.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]

    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text