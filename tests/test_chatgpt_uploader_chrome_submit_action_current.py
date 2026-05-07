from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_submit_action import (
    BLOCKED_LIVE_SUBMIT_CONFIRMATION_MISSING,
    BLOCKED_SUBMIT_ADAPTER_NOT_READY,
    BLOCKED_SUBMIT_BACKEND_UNSUPPORTED,
    BLOCKED_SUBMIT_HWND_MISSING,
    LIVE_CONFIRM_TEXT,
    PASS_CHROME_SUBMIT_ACTION_MOCKED,
    adapter_is_submit_ready,
    run_chrome_submit_action,
    write_chrome_submit_action_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _adapter_ready() -> dict[str, object]:
    return {
        "ok": True,
        "result": "PASS_CHROME_SUBMIT_READY_NO_ACTION",
        "expected_browser": "chrome",
        "send_gate_ready": True,
        "attachment_confirmed": True,
        "submit_backend": "dry_run_no_action",
        "send_button_pressed": False,
        "chatgpt_submit_performed": False,
        "raw_conversation_text_logged": False,
        "conversation_text_logged": False,
        "safety_flags": {
            "selenium_used": False,
            "webdriver_used": False,
            "browser_dom_automation_used": False,
            "attachment_confirmed": True,
            "file_upload_attempted": True,
            "send_allowed": False,
            "send_button_pressed": False,
            "chatgpt_submit_performed": False,
        },
    }


def test_adapter_is_submit_ready_contract() -> None:
    assert adapter_is_submit_ready(_adapter_ready()) is True
    bad = _adapter_ready()
    bad["attachment_confirmed"] = False
    assert adapter_is_submit_ready(bad) is False


def test_submit_action_blocks_when_adapter_not_ready() -> None:
    decision = run_chrome_submit_action(submit_adapter_decision={"ok": False, "result": "BLOCKED_SEND_GATE_NOT_READY"})

    assert decision.ok is False
    assert decision.result == BLOCKED_SUBMIT_ADAPTER_NOT_READY
    assert decision.submit_adapter_ready is False
    assert decision.keypress_attempted is False
    assert decision.submit_action_performed is False
    assert decision.chatgpt_submit_performed is False
    assert decision.send_button_pressed is False


def test_submit_action_blocks_unsupported_backend() -> None:
    decision = run_chrome_submit_action(submit_adapter_decision=_adapter_ready(), submit_backend="dom_click")

    assert decision.ok is False
    assert decision.result == BLOCKED_SUBMIT_BACKEND_UNSUPPORTED
    assert decision.submit_action_performed is False
    assert decision.chatgpt_submit_performed is False


def test_submit_action_mock_success_records_submit_without_live_ui() -> None:
    decision = run_chrome_submit_action(
        submit_adapter_decision=_adapter_ready(),
        submit_backend="ctrl_enter_once",
        mock_submit_success=True,
    )

    assert decision.ok is True
    assert decision.result == PASS_CHROME_SUBMIT_ACTION_MOCKED
    assert decision.live_browser_used is False
    assert decision.submit_adapter_ready is True
    assert decision.attachment_confirmed is True
    assert decision.keypress_attempted is True
    assert decision.submit_action_performed is True
    assert decision.chatgpt_submit_performed is True
    assert decision.send_button_pressed is False
    assert decision.raw_conversation_text_logged is False
    assert decision.conversation_text_logged is False
    assert decision.safety_flags["submit_action_performed"] is True
    assert decision.safety_flags["chatgpt_submit_performed"] is True
    assert decision.safety_flags["send_button_pressed"] is False
    assert decision.safety_flags["selenium_used"] is False
    assert decision.safety_flags["webdriver_used"] is False
    assert decision.safety_flags["browser_dom_automation_used"] is False


def test_live_submit_requires_confirmation_and_allow_flag() -> None:
    decision = run_chrome_submit_action(
        submit_adapter_decision=_adapter_ready(),
        live_browser=True,
        target_hwnd=123,
        allow_submit_action=True,
        confirm_live_browser_text="wrong",
    )

    assert decision.ok is False
    assert decision.result == BLOCKED_LIVE_SUBMIT_CONFIRMATION_MISSING
    assert LIVE_CONFIRM_TEXT in decision.reason
    assert decision.live_browser_used is False
    assert decision.keypress_attempted is False
    assert decision.chatgpt_submit_performed is False


def test_live_submit_requires_target_hwnd() -> None:
    decision = run_chrome_submit_action(
        submit_adapter_decision=_adapter_ready(),
        live_browser=True,
        allow_submit_action=True,
        confirm_live_browser_text=LIVE_CONFIRM_TEXT,
    )

    assert decision.ok is False
    assert decision.result == BLOCKED_SUBMIT_HWND_MISSING
    assert decision.chatgpt_submit_performed is False


def test_write_submit_action_evidence_roundtrip(tmp_path: Path) -> None:
    evidence = run_chrome_submit_action(submit_adapter_decision=_adapter_ready(), mock_submit_success=True)
    output = write_chrome_submit_action_evidence(evidence, tmp_path / "submit" / "action.json")

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["result"] == PASS_CHROME_SUBMIT_ACTION_MOCKED
    assert payload["submit_action_performed"] is True
    assert payload["chatgpt_submit_performed"] is True
    assert payload["send_button_pressed"] is False


def test_submit_action_script_mock_success(tmp_path: Path) -> None:
    adapter_path = tmp_path / "adapter.json"
    adapter_path.write_text(json.dumps(_adapter_ready(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    evidence_path = tmp_path / "submit_action.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_submit_action_gated.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--submit-adapter-decision",
            str(adapter_path),
            "--mock-submit-success",
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
    assert payload["result"] == PASS_CHROME_SUBMIT_ACTION_MOCKED
    assert payload["submit_action_performed"] is True
    assert payload["chatgpt_submit_performed"] is True
    assert payload["send_button_pressed"] is False

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["result"] == PASS_CHROME_SUBMIT_ACTION_MOCKED


def test_submit_action_script_blocks_without_adapter_ready(tmp_path: Path) -> None:
    adapter_path = tmp_path / "adapter.json"
    adapter_path.write_text(json.dumps({"ok": False, "result": "BLOCKED_SEND_GATE_NOT_READY"}, indent=2) + "\n", encoding="utf-8")
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_submit_action_gated.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--submit-adapter-decision",
            str(adapter_path),
            "--mock-submit-success",
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
    assert payload["result"] == BLOCKED_SUBMIT_ADAPTER_NOT_READY
    assert payload["chatgpt_submit_performed"] is False


def test_chrome_submit_action_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_submit_action_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_submit_action.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_submit_action_gated.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text