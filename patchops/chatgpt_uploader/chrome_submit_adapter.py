from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

try:
    from patchops.chatgpt_uploader.chrome_send_gate import PASS_SEND_READY_NO_SUBMIT
except Exception:  # pragma: no cover
    PASS_SEND_READY_NO_SUBMIT = "PASS_SEND_READY_NO_SUBMIT"

PASS_CHROME_SUBMIT_READY_NO_ACTION = "PASS_CHROME_SUBMIT_READY_NO_ACTION"
PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION = "PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION"
BLOCKED_SEND_GATE_NOT_READY = "BLOCKED_SEND_GATE_NOT_READY"
BLOCKED_SUBMIT_CONFIRMATION_MISSING = "BLOCKED_SUBMIT_CONFIRMATION_MISSING"
BLOCKED_SUBMIT_ACTION_DISABLED = "BLOCKED_SUBMIT_ACTION_DISABLED"
BLOCKED_SUBMIT_ACTION_NOT_IMPLEMENTED = "BLOCKED_SUBMIT_ACTION_NOT_IMPLEMENTED"
BLOCKED_FORBIDDEN_SUBMIT_BACKEND = "BLOCKED_FORBIDDEN_SUBMIT_BACKEND"

EXPECTED_BROWSER = "chrome"
LIVE_CONFIRM_TEXT = "PATCHOPS_CONFIRM_CHROME_SUBMIT_NO_ACTION"
SAFE_DRY_RUN_BACKEND = "dry_run_no_action"

FORBIDDEN_SUBMIT_BACKENDS = {
    "selenium",
    "webdriver",
    "browser_dom_automation",
    "dom_click",
    "javascript_click",
    "random_click",
    "coordinate_click",
    "unbounded_retry",
    "auto_submit",
    "hidden_browser",
}

SAFETY_FLAGS = {
    "selenium_used": False,
    "webdriver_used": False,
    "browser_dom_automation_used": False,
    "cloudflare_bypass_attempted": False,
    "captcha_bypass_attempted": False,
    "conversation_text_logged": False,
    "raw_conversation_text_logged": False,
    "random_page_click_performed": False,
    "file_upload_attempted": False,
    "attachment_confirmed": False,
    "send_allowed": False,
    "send_button_pressed": False,
    "submit_action_performed": False,
    "chatgpt_submit_performed": False,
    "live_browser_used": False,
}


@dataclass(frozen=True)
class ChromeSubmitAdapterDecision:
    ok: bool
    result: str
    expected_browser: str
    live_browser_used: bool
    send_gate_result: str | None
    send_gate_ready: bool
    attachment_confirmed: bool
    submit_backend: str
    submit_backend_allowed: bool
    submit_confirmation_present: bool
    submit_action_allowed: bool
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


def _safety_from_gate(gate: Mapping[str, Any], *, live_browser_used: bool = False) -> dict[str, bool]:
    safety = dict(SAFETY_FLAGS)
    nested = gate.get("safety_flags")
    if isinstance(nested, dict):
        for key in safety:
            if key in nested:
                safety[key] = bool(nested[key])
    safety["live_browser_used"] = bool(live_browser_used)
    safety["attachment_confirmed"] = bool(gate.get("attachment_confirmed", safety["attachment_confirmed"]))
    safety["file_upload_attempted"] = bool(gate.get("file_upload_attempted", safety["file_upload_attempted"]))
    safety["send_allowed"] = False
    safety["send_button_pressed"] = False
    safety["submit_action_performed"] = False
    safety["chatgpt_submit_performed"] = False
    safety["conversation_text_logged"] = False
    safety["raw_conversation_text_logged"] = False
    return safety


def _decision(
    *,
    ok: bool,
    result: str,
    send_gate: Mapping[str, Any],
    submit_backend: str,
    submit_backend_allowed: bool,
    submit_confirmation_present: bool,
    submit_action_allowed: bool,
    live_browser_used: bool,
    reason: str,
) -> ChromeSubmitAdapterDecision:
    safety = _safety_from_gate(send_gate, live_browser_used=live_browser_used)
    return ChromeSubmitAdapterDecision(
        ok=bool(ok),
        result=result,
        expected_browser=EXPECTED_BROWSER,
        live_browser_used=bool(live_browser_used),
        send_gate_result=send_gate.get("result"),
        send_gate_ready=send_gate.get("result") == PASS_SEND_READY_NO_SUBMIT and bool(send_gate.get("ok", False)),
        attachment_confirmed=bool(send_gate.get("attachment_confirmed", False)),
        submit_backend=submit_backend,
        submit_backend_allowed=bool(submit_backend_allowed),
        submit_confirmation_present=bool(submit_confirmation_present),
        submit_action_allowed=bool(submit_action_allowed),
        send_button_pressed=False,
        submit_action_performed=False,
        chatgpt_submit_performed=False,
        raw_conversation_text_logged=False,
        conversation_text_logged=False,
        safety_flags=safety,
        reason=reason,
    )


def evaluate_chrome_submit_adapter(
    *,
    send_gate_decision: Mapping[str, Any] | Any,
    submit_backend: str = SAFE_DRY_RUN_BACKEND,
    live_browser: bool = False,
    confirm_live_browser_text: str | None = None,
    allow_submit_action: bool = False,
) -> ChromeSubmitAdapterDecision:
    gate = _payload(send_gate_decision)
    backend = str(submit_backend or "").strip().lower()

    if backend in FORBIDDEN_SUBMIT_BACKENDS:
        return _decision(
            ok=False,
            result=BLOCKED_FORBIDDEN_SUBMIT_BACKEND,
            send_gate=gate,
            submit_backend=backend,
            submit_backend_allowed=False,
            submit_confirmation_present=False,
            submit_action_allowed=False,
            live_browser_used=False,
            reason=f"Forbidden submit backend blocked: {backend}",
        )

    if backend != SAFE_DRY_RUN_BACKEND:
        return _decision(
            ok=False,
            result=BLOCKED_FORBIDDEN_SUBMIT_BACKEND,
            send_gate=gate,
            submit_backend=backend or "<missing>",
            submit_backend_allowed=False,
            submit_confirmation_present=False,
            submit_action_allowed=False,
            live_browser_used=False,
            reason="Only dry_run_no_action submit backend is allowed in this patch.",
        )

    gate_ready = gate.get("result") == PASS_SEND_READY_NO_SUBMIT and bool(gate.get("ok", False)) and bool(gate.get("attachment_confirmed", False))
    if not gate_ready:
        return _decision(
            ok=False,
            result=BLOCKED_SEND_GATE_NOT_READY,
            send_gate=gate,
            submit_backend=backend,
            submit_backend_allowed=True,
            submit_confirmation_present=False,
            submit_action_allowed=False,
            live_browser_used=False,
            reason="Submit adapter requires PASS_SEND_READY_NO_SUBMIT with attachment_confirmed=true.",
        )

    if live_browser and confirm_live_browser_text != LIVE_CONFIRM_TEXT:
        return _decision(
            ok=False,
            result=BLOCKED_SUBMIT_CONFIRMATION_MISSING,
            send_gate=gate,
            submit_backend=backend,
            submit_backend_allowed=True,
            submit_confirmation_present=False,
            submit_action_allowed=False,
            live_browser_used=False,
            reason=f"Live submit adapter requires --confirm-live-browser-text {LIVE_CONFIRM_TEXT}; no submit action is performed.",
        )

    if allow_submit_action:
        return _decision(
            ok=False,
            result=BLOCKED_SUBMIT_ACTION_NOT_IMPLEMENTED,
            send_gate=gate,
            submit_backend=backend,
            submit_backend_allowed=True,
            submit_confirmation_present=confirm_live_browser_text == LIVE_CONFIRM_TEXT,
            submit_action_allowed=False,
            live_browser_used=bool(live_browser),
            reason="Actual ChatGPT submit action is intentionally not implemented in this patch.",
        )

    result = PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION if live_browser else PASS_CHROME_SUBMIT_READY_NO_ACTION
    return _decision(
        ok=True,
        result=result,
        send_gate=gate,
        submit_backend=backend,
        submit_backend_allowed=True,
        submit_confirmation_present=confirm_live_browser_text == LIVE_CONFIRM_TEXT if live_browser else False,
        submit_action_allowed=False,
        live_browser_used=bool(live_browser),
        reason="Submit adapter boundary is ready; dry-run evidence emitted and ChatGPT submit remains blocked.",
    )


def write_chrome_submit_adapter_decision(decision: ChromeSubmitAdapterDecision, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(decision.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path