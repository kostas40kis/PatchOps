from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_focus_guard import (
    BLOCKED_CHROME_NOT_RUNNING,
    BLOCKED_CHROME_TARGET_AMBIGUOUS,
    BLOCKED_CHROME_TARGET_NOT_READY,
    BLOCKED_LOGIN_OR_CHALLENGE,
    PASS_CHROME_TARGET_READY,
    LIVE_CONFIRM_TEXT,
    build_candidate,
    evaluate_chrome_preflight_candidates,
    redact_title,
    run_chrome_preflight,
    title_indicates_login_or_challenge,
    write_chrome_preflight_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_URL = "https://chatgpt.com/g/g-p-demo/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


def _candidate(
    title: str = "ChatGPT - Google Chrome",
    *,
    process_name: str = "chrome.exe",
    visible: bool = True,
    minimized: bool = False,
    hwnd: int = 100,
):
    return build_candidate(
        hwnd=hwnd,
        process_id=1234,
        process_name=process_name,
        title=title,
        visible=visible,
        minimized=minimized,
        target_url=TARGET_URL,
    )


def test_single_visible_chrome_chatgpt_candidate_passes() -> None:
    evidence = evaluate_chrome_preflight_candidates([_candidate()], target_url=TARGET_URL)

    assert evidence.ok is True
    assert evidence.result == PASS_CHROME_TARGET_READY
    assert evidence.expected_browser == "chrome"
    assert evidence.candidate_count == 1
    assert evidence.selectable_count == 1
    assert evidence.selected_hwnd == 100
    assert evidence.target_url_hash
    assert evidence.redacted_target_display == "https://chatgpt.com/<redacted>"
    assert evidence.raw_conversation_text_logged is False
    assert evidence.file_upload_attempted is False
    assert evidence.chatgpt_submit_performed is False
    assert evidence.safety_flags["selenium_used"] is False
    assert evidence.safety_flags["webdriver_used"] is False
    assert evidence.safety_flags["browser_dom_automation_used"] is False
    assert evidence.safety_flags["window_focus_attempted"] is False
    assert evidence.candidates[0].selected is True


def test_no_chrome_candidates_blocks_not_running() -> None:
    evidence = evaluate_chrome_preflight_candidates([
        _candidate(process_name="msedge.exe", title="ChatGPT - Microsoft Edge")
    ], target_url=TARGET_URL)

    assert evidence.ok is False
    assert evidence.result == BLOCKED_CHROME_NOT_RUNNING
    assert evidence.selectable_count == 0
    assert evidence.selected_hwnd is None


def test_hidden_or_minimized_chrome_blocks_target_not_ready() -> None:
    evidence = evaluate_chrome_preflight_candidates([
        _candidate(visible=False, hwnd=1),
        _candidate(minimized=True, hwnd=2),
    ], target_url=TARGET_URL)

    assert evidence.ok is False
    assert evidence.result == BLOCKED_CHROME_TARGET_NOT_READY
    assert evidence.selectable_count == 0


def test_multiple_visible_chatgpt_candidates_block_ambiguous() -> None:
    evidence = evaluate_chrome_preflight_candidates([
        _candidate(hwnd=1),
        _candidate(title="ChatGPT shared tab - Google Chrome", hwnd=2),
    ], target_url=TARGET_URL)

    assert evidence.ok is False
    assert evidence.result == BLOCKED_CHROME_TARGET_AMBIGUOUS
    assert evidence.selectable_count == 2
    assert evidence.selected_hwnd is None


def test_login_or_challenge_candidate_blocks() -> None:
    evidence = evaluate_chrome_preflight_candidates([
        _candidate(title="Checking your browser before accessing ChatGPT - Google Chrome", hwnd=1)
    ], target_url=TARGET_URL)

    assert evidence.ok is False
    assert evidence.result == BLOCKED_LOGIN_OR_CHALLENGE
    assert evidence.raw_conversation_text_logged is False


def test_title_helpers_redact_and_detect_challenge() -> None:
    raw_title = "Private conversation name - ChatGPT - Google Chrome"
    assert redact_title(raw_title) == "ChatGPT - Google Chrome"
    assert "Private conversation" not in redact_title(raw_title)
    assert title_indicates_login_or_challenge("Verify you are human - Google Chrome") is True
    assert title_indicates_login_or_challenge("ChatGPT - Google Chrome") is False


def test_run_chrome_preflight_requires_live_confirmation() -> None:
    evidence = run_chrome_preflight(live_browser=True, confirm_live_browser_text="wrong", target_url=TARGET_URL)

    assert evidence.ok is False
    assert evidence.result == BLOCKED_CHROME_TARGET_NOT_READY
    assert evidence.live_browser_used is False
    assert evidence.error
    assert LIVE_CONFIRM_TEXT in evidence.error


def test_write_chrome_preflight_evidence_roundtrip(tmp_path: Path) -> None:
    evidence = evaluate_chrome_preflight_candidates([_candidate()], target_url=TARGET_URL)
    output = write_chrome_preflight_evidence(evidence, tmp_path / "evidence" / "preflight.json")

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["result"] == PASS_CHROME_TARGET_READY
    assert payload["expected_browser"] == "chrome"
    assert payload["raw_conversation_text_logged"] is False
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["safety_flags"]["window_focus_attempted"] is False
    assert TARGET_URL not in output.read_text(encoding="utf-8")


def test_preflight_script_local_candidate_passes(tmp_path: Path) -> None:
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_preflight.py"
    evidence_path = tmp_path / "preflight.json"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--target-url",
            TARGET_URL,
            "--candidate",
            "chrome.exe|ChatGPT - Google Chrome|true|false|501",
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
    assert payload["result"] == PASS_CHROME_TARGET_READY
    assert payload["ok"] is True
    assert payload["selected_hwnd"] == 501
    assert payload["raw_conversation_text_logged"] is False
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert TARGET_URL not in result.stdout

    evidence_payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence_payload["result"] == PASS_CHROME_TARGET_READY
    assert TARGET_URL not in evidence_path.read_text(encoding="utf-8")


def test_preflight_script_local_ambiguous_returns_blocked_zero_exit() -> None:
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_preflight.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--target-url",
            TARGET_URL,
            "--candidate",
            "chrome.exe|ChatGPT - Google Chrome|true|false|1",
            "--candidate",
            "chrome.exe|ChatGPT second - Google Chrome|true|false|2",
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
    assert payload["result"] == BLOCKED_CHROME_TARGET_AMBIGUOUS
    assert payload["ok"] is False
    assert payload["selectable_count"] == 2


def test_preflight_script_live_mode_without_confirmation_blocks() -> None:
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_preflight.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--live-browser",
            "--target-url",
            TARGET_URL,
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
    assert payload["result"] == BLOCKED_CHROME_TARGET_NOT_READY
    assert payload["live_browser_used"] is False
    assert LIVE_CONFIRM_TEXT in payload["error"]


def test_chrome_focus_guard_patch_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]

    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_focus_guard_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_focus_guard.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_preflight.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "pywinauto", "playwright"]

    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text