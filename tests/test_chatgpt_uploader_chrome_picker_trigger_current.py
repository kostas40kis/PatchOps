from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_picker_trigger import (
    BLOCKED_CHROME_TARGET_NOT_READY,
    BLOCKED_LIVE_BROWSER_CONFIRMATION_MISSING,
    BLOCKED_UNSAFE_TRIGGER,
    FAIL_CHROME_PICKER_NOT_OPENED,
    FORBIDDEN_TRIGGER_BACKENDS,
    LIVE_CONFIRM_TEXT,
    PASS_CHROME_PICKER_OPENED_NO_UPLOAD,
    PASS_ONE_PICKER_DETECTED,
    SAFE_TRIGGER_NAME,
    build_picker_candidate,
    evaluate_chrome_picker_detection,
    run_chrome_picker_trigger,
    validate_trigger_backend,
    write_chrome_picker_trigger_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _one_picker(expected_chrome_hwnd: int = 100):
    picker = build_picker_candidate(handle=501, owner_handle=expected_chrome_hwnd, expected_chrome_hwnd=expected_chrome_hwnd)
    return evaluate_chrome_picker_detection([picker], expected_chrome_hwnd=expected_chrome_hwnd)


def test_safe_trigger_policy_is_single_attempt_no_write_no_send() -> None:
    plan = validate_trigger_backend(SAFE_TRIGGER_NAME)

    assert plan.ok is True
    assert plan.trigger_name == SAFE_TRIGGER_NAME
    assert plan.sequence == (
        "focus_chrome_target",
        "safe_composer_focus_once",
        "slash_once",
        "enter_once",
        "detect_picker",
        "stop",
    )
    assert plan.max_attempts == 1
    assert plan.allow_path_write is False
    assert plan.allow_open_press is False
    assert plan.allow_send is False
    assert plan.forbidden_backend_detected is None


def test_unsafe_trigger_backends_are_blocked() -> None:
    expected = {
        "ctrl_u",
        "tab_ladder",
        "random_click_ladder",
        "unbounded_retries",
        "unknown_keyboard_shortcut",
        "dom_query",
        "selenium",
        "webdriver",
        "browser_dom_automation",
        "plus_menu_crawling",
        "multi_picker_blind_selection",
    }
    assert expected.issubset(FORBIDDEN_TRIGGER_BACKENDS)

    for backend in expected:
        plan = validate_trigger_backend(backend)
        assert plan.ok is False
        assert plan.result == BLOCKED_UNSAFE_TRIGGER
        assert plan.forbidden_backend_detected == backend
        assert plan.allow_path_write is False
        assert plan.allow_open_press is False
        assert plan.allow_send is False


def test_trigger_blocks_when_preflight_not_ready() -> None:
    evidence = run_chrome_picker_trigger(preflight_ready=False, post_trigger_picker_evidence=_one_picker())

    assert evidence.ok is False
    assert evidence.result == BLOCKED_CHROME_TARGET_NOT_READY
    assert evidence.safe_click_performed is False
    assert evidence.slash_trigger_attempted is False
    assert evidence.enter_pressed_for_picker_command is False
    assert evidence.file_path_written is False
    assert evidence.open_button_pressed is False
    assert evidence.file_upload_attempted is False
    assert evidence.chatgpt_submit_performed is False


def test_trigger_blocks_unsafe_backend_before_any_action() -> None:
    evidence = run_chrome_picker_trigger(trigger_backend="ctrl_u", preflight_ready=True, post_trigger_picker_evidence=_one_picker())

    assert evidence.ok is False
    assert evidence.result == BLOCKED_UNSAFE_TRIGGER
    assert evidence.trigger_plan["forbidden_backend_detected"] == "ctrl_u"
    assert evidence.safe_click_performed is False
    assert evidence.slash_trigger_attempted is False
    assert evidence.enter_pressed_for_picker_command is False


def test_local_trigger_passes_when_post_trigger_picker_detected() -> None:
    evidence = run_chrome_picker_trigger(
        preflight_ready=True,
        expected_chrome_hwnd=100,
        post_trigger_picker_evidence=_one_picker(100),
    )

    assert evidence.ok is True
    assert evidence.result == PASS_CHROME_PICKER_OPENED_NO_UPLOAD
    assert evidence.picker_detected_after_trigger is True
    assert evidence.picker_result_after_trigger == PASS_ONE_PICKER_DETECTED
    assert evidence.file_path_written is False
    assert evidence.open_button_pressed is False
    assert evidence.file_upload_attempted is False
    assert evidence.chatgpt_submit_performed is False
    assert evidence.raw_conversation_text_logged is False
    assert evidence.safety_flags["selenium_used"] is False
    assert evidence.safety_flags["webdriver_used"] is False
    assert evidence.safety_flags["browser_dom_automation_used"] is False


def test_local_trigger_fails_when_no_picker_detected_after_trigger() -> None:
    evidence = run_chrome_picker_trigger(preflight_ready=True, expected_chrome_hwnd=100)

    assert evidence.ok is False
    assert evidence.result == FAIL_CHROME_PICKER_NOT_OPENED
    assert evidence.picker_detected_after_trigger is False
    assert evidence.file_path_written is False
    assert evidence.open_button_pressed is False
    assert evidence.file_upload_attempted is False
    assert evidence.chatgpt_submit_performed is False


def test_live_trigger_requires_explicit_confirmation() -> None:
    evidence = run_chrome_picker_trigger(
        preflight_ready=True,
        expected_chrome_hwnd=100,
        live_browser=True,
        confirm_live_browser_text="wrong",
    )

    assert evidence.ok is False
    assert evidence.result == BLOCKED_LIVE_BROWSER_CONFIRMATION_MISSING
    assert LIVE_CONFIRM_TEXT in evidence.reason
    assert evidence.live_browser_used is False
    assert evidence.file_path_written is False
    assert evidence.file_upload_attempted is False


def test_write_trigger_evidence_roundtrip(tmp_path: Path) -> None:
    evidence = run_chrome_picker_trigger(preflight_ready=True, expected_chrome_hwnd=100, post_trigger_picker_evidence=_one_picker(100))
    output = write_chrome_picker_trigger_evidence(evidence, tmp_path / "trigger" / "evidence.json")

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["result"] == PASS_CHROME_PICKER_OPENED_NO_UPLOAD
    assert payload["file_path_written"] is False
    assert payload["open_button_pressed"] is False
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False


def test_open_picker_script_mock_success(tmp_path: Path) -> None:
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_open_picker_live.py"
    evidence_path = tmp_path / "open_picker.json"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--preflight-ready",
            "--expected-chrome-hwnd",
            "100",
            "--mock-picker-after-trigger",
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
    assert payload["result"] == PASS_CHROME_PICKER_OPENED_NO_UPLOAD
    assert payload["ok"] is True
    assert payload["file_path_written"] is False
    assert payload["open_button_pressed"] is False
    assert payload["chatgpt_submit_performed"] is False

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["result"] == PASS_CHROME_PICKER_OPENED_NO_UPLOAD


def test_open_picker_script_blocks_unsafe_backend_zero_exit() -> None:
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_open_picker_live.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--preflight-ready",
            "--trigger-backend",
            "ctrl_u",
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
    assert payload["result"] == BLOCKED_UNSAFE_TRIGGER
    assert payload["trigger_plan"]["forbidden_backend_detected"] == "ctrl_u"


def test_open_picker_script_live_without_confirmation_blocks() -> None:
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_open_picker_live.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--preflight-ready",
            "--expected-chrome-hwnd",
            "100",
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
    assert LIVE_CONFIRM_TEXT in payload["reason"]
    assert payload["live_browser_used"] is False


def test_chrome_picker_trigger_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_picker_trigger_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_picker_trigger.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_open_picker_live.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text