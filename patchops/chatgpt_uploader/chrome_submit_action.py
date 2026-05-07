from __future__ import annotations

import ctypes
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

try:
    from patchops.chatgpt_uploader.chrome_submit_adapter import (
        PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION,
        PASS_CHROME_SUBMIT_READY_NO_ACTION,
    )
except Exception:  # pragma: no cover
    PASS_CHROME_SUBMIT_READY_NO_ACTION = "PASS_CHROME_SUBMIT_READY_NO_ACTION"
    PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION = "PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION"

PASS_CHROME_SUBMIT_ACTION_PERFORMED = "PASS_CHROME_SUBMIT_ACTION_PERFORMED"
PASS_CHROME_SUBMIT_ACTION_MOCKED = "PASS_CHROME_SUBMIT_ACTION_MOCKED"
BLOCKED_SUBMIT_ADAPTER_NOT_READY = "BLOCKED_SUBMIT_ADAPTER_NOT_READY"
BLOCKED_LIVE_SUBMIT_CONFIRMATION_MISSING = "BLOCKED_LIVE_SUBMIT_CONFIRMATION_MISSING"
BLOCKED_SUBMIT_HWND_MISSING = "BLOCKED_SUBMIT_HWND_MISSING"
BLOCKED_SUBMIT_BACKEND_UNSUPPORTED = "BLOCKED_SUBMIT_BACKEND_UNSUPPORTED"
FAIL_SUBMIT_KEYPRESS_FAILED = "FAIL_SUBMIT_KEYPRESS_FAILED"

EXPECTED_BROWSER = "chrome"
LIVE_CONFIRM_TEXT = "PATCHOPS_CONFIRM_CHROME_SUBMIT_ACTION"
SUBMIT_BACKEND_ENTER = "enter_once"
SUBMIT_BACKEND_CTRL_ENTER = "ctrl_enter_once"
SUPPORTED_BACKENDS = {SUBMIT_BACKEND_ENTER, SUBMIT_BACKEND_CTRL_ENTER}

SAFETY_FLAGS = {
    "selenium_used": False,
    "webdriver_used": False,
    "browser_dom_automation_used": False,
    "cloudflare_bypass_attempted": False,
    "captcha_bypass_attempted": False,
    "conversation_text_logged": False,
    "raw_conversation_text_logged": False,
    "random_page_click_performed": False,
    "file_upload_attempted": True,
    "attachment_confirmed": True,
    "send_allowed": True,
    "send_button_pressed": False,
    "submit_action_performed": False,
    "chatgpt_submit_performed": False,
    "live_browser_used": False,
}


@dataclass(frozen=True)
class ChromeSubmitActionEvidence:
    ok: bool
    result: str
    expected_browser: str
    live_browser_used: bool
    submit_adapter_result: str | None
    submit_adapter_ready: bool
    attachment_confirmed: bool
    submit_backend: str
    submit_confirmation_present: bool
    target_hwnd: int | None
    keypress_attempted: bool
    send_button_pressed: bool
    submit_action_performed: bool
    chatgpt_submit_performed: bool
    raw_conversation_text_logged: bool
    conversation_text_logged: bool
    safety_flags: dict[str, bool]
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _payload(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "to_payload"):
        payload = value.to_payload()
        if isinstance(payload, dict):
            return dict(payload)
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def _safety(*, live_browser_used: bool, submit_performed: bool, send_button_pressed: bool) -> dict[str, bool]:
    safety = dict(SAFETY_FLAGS)
    safety["live_browser_used"] = bool(live_browser_used)
    safety["submit_action_performed"] = bool(submit_performed)
    safety["chatgpt_submit_performed"] = bool(submit_performed)
    safety["send_button_pressed"] = bool(send_button_pressed)
    return safety


def _blocked(
    *,
    result: str,
    adapter_payload: Mapping[str, Any],
    submit_backend: str,
    reason: str,
    live_browser_used: bool = False,
    target_hwnd: int | None = None,
) -> ChromeSubmitActionEvidence:
    return ChromeSubmitActionEvidence(
        ok=False,
        result=result,
        expected_browser=EXPECTED_BROWSER,
        live_browser_used=bool(live_browser_used),
        submit_adapter_result=adapter_payload.get("result"),
        submit_adapter_ready=False,
        attachment_confirmed=bool(adapter_payload.get("attachment_confirmed", False)),
        submit_backend=submit_backend,
        submit_confirmation_present=False,
        target_hwnd=target_hwnd,
        keypress_attempted=False,
        send_button_pressed=False,
        submit_action_performed=False,
        chatgpt_submit_performed=False,
        raw_conversation_text_logged=False,
        conversation_text_logged=False,
        safety_flags=_safety(live_browser_used=live_browser_used, submit_performed=False, send_button_pressed=False),
        reason=reason,
    )


def adapter_is_submit_ready(adapter_payload: Mapping[str, Any]) -> bool:
    return (
        bool(adapter_payload.get("ok", False))
        and adapter_payload.get("result") in {PASS_CHROME_SUBMIT_READY_NO_ACTION, PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION}
        and bool(adapter_payload.get("send_gate_ready", False))
        and bool(adapter_payload.get("attachment_confirmed", False))
        and not bool(adapter_payload.get("chatgpt_submit_performed", False))
        and not bool(adapter_payload.get("send_button_pressed", False))
    )


def _press_key(vk: int) -> None:
    user32 = ctypes.windll.user32
    user32.keybd_event(int(vk), 0, 0, 0)
    user32.keybd_event(int(vk), 0, 0x0002, 0)


def _press_ctrl_enter() -> None:
    user32 = ctypes.windll.user32
    VK_CONTROL = 0x11
    VK_RETURN = 0x0D
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_RETURN, 0, 0, 0)
    user32.keybd_event(VK_RETURN, 0, 0x0002, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_CONTROL, 0, 0x0002, 0)


def _press_submit_once(*, target_hwnd: int, submit_backend: str) -> None:
    user32 = ctypes.windll.user32
    if not user32.SetForegroundWindow(int(target_hwnd)):
        raise RuntimeError("SetForegroundWindow failed")
    time.sleep(0.20)
    if submit_backend == SUBMIT_BACKEND_ENTER:
        _press_key(0x0D)
    elif submit_backend == SUBMIT_BACKEND_CTRL_ENTER:
        _press_ctrl_enter()
    else:
        raise RuntimeError(f"unsupported submit backend: {submit_backend}")


def run_chrome_submit_action(
    *,
    submit_adapter_decision: Mapping[str, Any] | Any,
    submit_backend: str = SUBMIT_BACKEND_CTRL_ENTER,
    live_browser: bool = False,
    confirm_live_browser_text: str | None = None,
    target_hwnd: int | None = None,
    allow_submit_action: bool = False,
    mock_submit_success: bool = False,
) -> ChromeSubmitActionEvidence:
    adapter_payload = _payload(submit_adapter_decision)
    backend = str(submit_backend or "").strip().lower()

    if backend not in SUPPORTED_BACKENDS:
        return _blocked(
            result=BLOCKED_SUBMIT_BACKEND_UNSUPPORTED,
            adapter_payload=adapter_payload,
            submit_backend=backend or "<missing>",
            reason="Submit backend must be enter_once or ctrl_enter_once.",
        )

    if not adapter_is_submit_ready(adapter_payload):
        return _blocked(
            result=BLOCKED_SUBMIT_ADAPTER_NOT_READY,
            adapter_payload=adapter_payload,
            submit_backend=backend,
            reason="Submit action requires a ready submit-adapter decision with send_gate_ready=true and attachment_confirmed=true.",
        )

    if live_browser:
        if confirm_live_browser_text != LIVE_CONFIRM_TEXT or not allow_submit_action:
            return _blocked(
                result=BLOCKED_LIVE_SUBMIT_CONFIRMATION_MISSING,
                adapter_payload=adapter_payload,
                submit_backend=backend,
                reason=f"Live submit requires --allow-submit-action and --confirm-live-browser-text {LIVE_CONFIRM_TEXT}.",
                live_browser_used=False,
                target_hwnd=target_hwnd,
            )
        if target_hwnd is None:
            return _blocked(
                result=BLOCKED_SUBMIT_HWND_MISSING,
                adapter_payload=adapter_payload,
                submit_backend=backend,
                reason="Live submit requires target_hwnd from Chrome preflight evidence.",
                live_browser_used=False,
                target_hwnd=None,
            )
        try:
            _press_submit_once(target_hwnd=int(target_hwnd), submit_backend=backend)
        except Exception as exc:
            return ChromeSubmitActionEvidence(
                ok=False,
                result=FAIL_SUBMIT_KEYPRESS_FAILED,
                expected_browser=EXPECTED_BROWSER,
                live_browser_used=True,
                submit_adapter_result=adapter_payload.get("result"),
                submit_adapter_ready=True,
                attachment_confirmed=True,
                submit_backend=backend,
                submit_confirmation_present=True,
                target_hwnd=target_hwnd,
                keypress_attempted=True,
                send_button_pressed=False,
                submit_action_performed=False,
                chatgpt_submit_performed=False,
                raw_conversation_text_logged=False,
                conversation_text_logged=False,
                safety_flags=_safety(live_browser_used=True, submit_performed=False, send_button_pressed=False),
                reason=f"Submit keypress failed: {exc}",
            )
        return ChromeSubmitActionEvidence(
            ok=True,
            result=PASS_CHROME_SUBMIT_ACTION_PERFORMED,
            expected_browser=EXPECTED_BROWSER,
            live_browser_used=True,
            submit_adapter_result=adapter_payload.get("result"),
            submit_adapter_ready=True,
            attachment_confirmed=True,
            submit_backend=backend,
            submit_confirmation_present=True,
            target_hwnd=target_hwnd,
            keypress_attempted=True,
            send_button_pressed=False,
            submit_action_performed=True,
            chatgpt_submit_performed=True,
            raw_conversation_text_logged=False,
            conversation_text_logged=False,
            safety_flags=_safety(live_browser_used=True, submit_performed=True, send_button_pressed=False),
            reason="Gated submit keypress was performed once; no DOM/WebDriver automation or conversation text logging was used.",
        )

    if mock_submit_success:
        return ChromeSubmitActionEvidence(
            ok=True,
            result=PASS_CHROME_SUBMIT_ACTION_MOCKED,
            expected_browser=EXPECTED_BROWSER,
            live_browser_used=False,
            submit_adapter_result=adapter_payload.get("result"),
            submit_adapter_ready=True,
            attachment_confirmed=True,
            submit_backend=backend,
            submit_confirmation_present=False,
            target_hwnd=target_hwnd,
            keypress_attempted=True,
            send_button_pressed=False,
            submit_action_performed=True,
            chatgpt_submit_performed=True,
            raw_conversation_text_logged=False,
            conversation_text_logged=False,
            safety_flags=_safety(live_browser_used=False, submit_performed=True, send_button_pressed=False),
            reason="Mock submit action succeeded; no live UI action was performed.",
        )

    return _blocked(
        result=BLOCKED_LIVE_SUBMIT_CONFIRMATION_MISSING,
        adapter_payload=adapter_payload,
        submit_backend=backend,
        reason="No live submit confirmation or mock submit success was provided.",
        live_browser_used=False,
        target_hwnd=target_hwnd,
    )


def write_chrome_submit_action_evidence(evidence: ChromeSubmitActionEvidence, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evidence.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path