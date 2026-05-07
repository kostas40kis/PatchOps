from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_submit_adapter import (
    BLOCKED_FORBIDDEN_SUBMIT_BACKEND,
    BLOCKED_SEND_GATE_NOT_READY,
    BLOCKED_SUBMIT_ACTION_NOT_IMPLEMENTED,
    BLOCKED_SUBMIT_CONFIRMATION_MISSING,
    LIVE_CONFIRM_TEXT,
    PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION,
    PASS_CHROME_SUBMIT_READY_NO_ACTION,
    evaluate_chrome_submit_adapter,
    write_chrome_submit_adapter_decision,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _ready_gate() -> dict[str, object]:
    return {
        "ok": True,
        "result": "PASS_SEND_READY_NO_SUBMIT",
        "expected_browser": "chrome",
        "attachment_confirmed": True,
        "file_upload_attempted": True,
        "send_allowed": False,
        "send_button_pressed": False,
        "chatgpt_submit_performed": False,
        "raw_conversation_text_logged": False,
        "conversation_text_logged": False,
        "safety_flags": {
            "selenium_used": False,
            "webdriver_used": False,
            "browser_dom_automation_used": False,
            "send_allowed": False,
            "send_button_pressed": False,
            "chatgpt_submit_performed": False,
            "attachment_confirmed": True,
            "file_upload_attempted": True,
        },
    }


def test_submit_adapter_ready_no_action_from_send_gate() -> None:
    decision = evaluate_chrome_submit_adapter(send_gate_decision=_ready_gate())

    assert decision.ok is True
    assert decision.result == PASS_CHROME_SUBMIT_READY_NO_ACTION
    assert decision.expected_browser == "chrome"
    assert decision.send_gate_ready is True
    assert decision.attachment_confirmed is True
    assert decision.submit_backend == "dry_run_no_action"
    assert decision.submit_backend_allowed is True
    assert decision.submit_action_allowed is False
    assert decision.send_button_pressed is False
    assert decision.submit_action_performed is False
    assert decision.chatgpt_submit_performed is False
    assert decision.raw_conversation_text_logged is False
    assert decision.conversation_text_logged is False
    assert decision.safety_flags["attachment_confirmed"] is True
    assert decision.safety_flags["file_upload_attempted"] is True
    assert decision.safety_flags["send_allowed"] is False
    assert decision.safety_flags["send_button_pressed"] is False
    assert decision.safety_flags["chatgpt_submit_performed"] is False
    assert decision.safety_flags["selenium_used"] is False
    assert decision.safety_flags["webdriver_used"] is False
    assert decision.safety_flags["browser_dom_automation_used"] is False


def test_submit_adapter_blocks_when_send_gate_not_ready() -> None:
    gate = _ready_gate()
    gate["result"] = "BLOCKED_ATTACHMENT_NOT_CONFIRMED"
    gate["ok"] = False
    gate["attachment_confirmed"] = False
    decision = evaluate_chrome_submit_adapter(send_gate_decision=gate)

    assert decision.ok is False
    assert decision.result == BLOCKED_SEND_GATE_NOT_READY
    assert decision.send_gate_ready is False
    assert decision.send_button_pressed is False
    assert decision.chatgpt_submit_performed is False


def test_submit_adapter_blocks_forbidden_backends() -> None:
    for backend in ["selenium", "webdriver", "dom_click", "random_click", "auto_submit", "hidden_browser"]:
        decision = evaluate_chrome_submit_adapter(send_gate_decision=_ready_gate(), submit_backend=backend)
        assert decision.ok is False
        assert decision.result == BLOCKED_FORBIDDEN_SUBMIT_BACKEND
        assert decision.submit_backend_allowed is False
        assert decision.chatgpt_submit_performed is False


def test_submit_adapter_live_dry_run_requires_confirmation() -> None:
    decision = evaluate_chrome_submit_adapter(
        send_gate_decision=_ready_gate(),
        live_browser=True,
        confirm_live_browser_text="wrong",
    )

    assert decision.ok is False
    assert decision.result == BLOCKED_SUBMIT_CONFIRMATION_MISSING
    assert LIVE_CONFIRM_TEXT in decision.reason
    assert decision.live_browser_used is False
    assert decision.chatgpt_submit_performed is False


def test_submit_adapter_live_dry_run_with_confirmation_still_no_action() -> None:
    decision = evaluate_chrome_submit_adapter(
        send_gate_decision=_ready_gate(),
        live_browser=True,
        confirm_live_browser_text=LIVE_CONFIRM_TEXT,
    )

    assert decision.ok is True
    assert decision.result == PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION
    assert decision.live_browser_used is True
    assert decision.submit_confirmation_present is True
    assert decision.send_button_pressed is False
    assert decision.submit_action_performed is False
    assert decision.chatgpt_submit_performed is False


def test_submit_adapter_blocks_allow_submit_action() -> None:
    decision = evaluate_chrome_submit_adapter(
        send_gate_decision=_ready_gate(),
        allow_submit_action=True,
    )

    assert decision.ok is False
    assert decision.result == BLOCKED_SUBMIT_ACTION_NOT_IMPLEMENTED
    assert decision.submit_action_allowed is False
    assert decision.send_button_pressed is False
    assert decision.chatgpt_submit_performed is False


def test_write_submit_adapter_decision_roundtrip(tmp_path: Path) -> None:
    decision = evaluate_chrome_submit_adapter(send_gate_decision=_ready_gate())
    output = write_chrome_submit_adapter_decision(decision, tmp_path / "submit" / "decision.json")

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["result"] == PASS_CHROME_SUBMIT_READY_NO_ACTION
    assert payload["send_gate_ready"] is True
    assert payload["send_button_pressed"] is False
    assert payload["submit_action_performed"] is False
    assert payload["chatgpt_submit_performed"] is False


def test_submit_adapter_script_with_gate_file(tmp_path: Path) -> None:
    gate_path = tmp_path / "send_gate.json"
    gate_path.write_text(json.dumps(_ready_gate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    decision_path = tmp_path / "submit_decision.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_submit_adapter_no_action.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--send-gate-decision",
            str(gate_path),
            "--decision-path",
            str(decision_path),
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
    assert payload["result"] == PASS_CHROME_SUBMIT_READY_NO_ACTION
    assert payload["send_gate_ready"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert payload["send_button_pressed"] is False

    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    assert decision["result"] == PASS_CHROME_SUBMIT_READY_NO_ACTION


def test_submit_adapter_script_blocks_allow_submit(tmp_path: Path) -> None:
    gate_path = tmp_path / "send_gate.json"
    gate_path.write_text(json.dumps(_ready_gate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_submit_adapter_no_action.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--send-gate-decision",
            str(gate_path),
            "--allow-submit-action",
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
    assert payload["result"] == BLOCKED_SUBMIT_ACTION_NOT_IMPLEMENTED
    assert payload["chatgpt_submit_performed"] is False


def test_chrome_submit_adapter_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_submit_adapter_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_submit_adapter.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_submit_adapter_no_action.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text