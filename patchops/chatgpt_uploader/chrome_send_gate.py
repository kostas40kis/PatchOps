from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from patchops.chatgpt_uploader.chrome_attachment_verifier import PASS_ATTACHMENT_CONFIRMED_NO_SEND
from patchops.chatgpt_uploader.chrome_picker_path_entry import validate_canonical_report_path

PASS_SEND_READY_NO_SUBMIT = "PASS_SEND_READY_NO_SUBMIT"
BLOCKED_ATTACHMENT_NOT_CONFIRMED = "BLOCKED_ATTACHMENT_NOT_CONFIRMED"
BLOCKED_SEND_CONFIRMATION_MISSING = "BLOCKED_SEND_CONFIRMATION_MISSING"
BLOCKED_SEND_ACTION_NOT_IMPLEMENTED = "BLOCKED_SEND_ACTION_NOT_IMPLEMENTED"
BLOCKED_SEND_POLICY_NO_SUBMIT = "BLOCKED_SEND_POLICY_NO_SUBMIT"

EXPECTED_BROWSER = "chrome"
LIVE_CONFIRM_TEXT = "PATCHOPS_CONFIRM_SEND_GATE_NO_SUBMIT"

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
    "chatgpt_submit_performed": False,
    "live_browser_used": False,
}


@dataclass(frozen=True)
class SendGateDecision:
    ok: bool
    result: str
    expected_browser: str
    canonical_report: dict[str, Any]
    attachment_evidence_result: str | None
    attachment_confirmed: bool
    expected_basename: str | None
    expected_basename_sha256: str | None
    submit_action_allowed: bool
    send_button_pressed: bool
    chatgpt_submit_performed: bool
    raw_conversation_text_logged: bool
    conversation_text_logged: bool
    live_browser_used: bool
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
        result = value.to_payload()
        if isinstance(result, dict):
            return dict(result)
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def _basename_hash(value: str | None) -> str | None:
    if not value:
        return None
    import hashlib
    return hashlib.sha256(str(Path(value).name).encode("utf-8")).hexdigest()


def _blocked_decision(
    *,
    result: str,
    canonical_report: dict[str, Any],
    attachment_payload: Mapping[str, Any] | None = None,
    reason: str,
    live_browser_used: bool = False,
) -> SendGateDecision:
    payload = dict(attachment_payload or {})
    safety = dict(SAFETY_FLAGS)
    safety["live_browser_used"] = bool(live_browser_used)
    safety["attachment_confirmed"] = bool(payload.get("attachment_confirmed", False))
    safety["file_upload_attempted"] = bool(payload.get("file_upload_attempted", payload.get("upload_attempted_before_verification", False)))
    return SendGateDecision(
        ok=False,
        result=result,
        expected_browser=EXPECTED_BROWSER,
        canonical_report=canonical_report,
        attachment_evidence_result=payload.get("result"),
        attachment_confirmed=bool(payload.get("attachment_confirmed", False)),
        expected_basename=payload.get("expected_basename") or canonical_report.get("basename"),
        expected_basename_sha256=payload.get("expected_basename_sha256") or _basename_hash(canonical_report.get("basename")),
        submit_action_allowed=False,
        send_button_pressed=False,
        chatgpt_submit_performed=False,
        raw_conversation_text_logged=False,
        conversation_text_logged=False,
        live_browser_used=bool(live_browser_used),
        safety_flags=safety,
        reason=reason,
    )


def evaluate_send_gate_no_submit(
    *,
    canonical_report_path: Path | str,
    attachment_evidence: Mapping[str, Any] | Any,
    live_browser: bool = False,
    confirm_live_browser_text: str | None = None,
    allow_submit: bool = False,
) -> SendGateDecision:
    report = validate_canonical_report_path(canonical_report_path)
    canonical_payload = report.to_payload()
    if not report.ok:
        return _blocked_decision(
            result=report.result,
            canonical_report=canonical_payload,
            attachment_payload=_payload(attachment_evidence),
            reason=report.reason,
            live_browser_used=False,
        )

    attachment_payload = _payload(attachment_evidence)
    attachment_result = attachment_payload.get("result")
    attachment_confirmed = bool(attachment_payload.get("attachment_confirmed", False))
    expected_basename = attachment_payload.get("expected_basename") or canonical_payload.get("basename")
    expected_hash = attachment_payload.get("expected_basename_sha256") or _basename_hash(expected_basename)
    canonical_hash = _basename_hash(canonical_payload.get("basename"))

    if attachment_result != PASS_ATTACHMENT_CONFIRMED_NO_SEND or not attachment_confirmed:
        return _blocked_decision(
            result=BLOCKED_ATTACHMENT_NOT_CONFIRMED,
            canonical_report=canonical_payload,
            attachment_payload=attachment_payload,
            reason="Attachment evidence must be PASS_ATTACHMENT_CONFIRMED_NO_SEND with attachment_confirmed=true before send readiness.",
            live_browser_used=False,
        )

    if expected_hash != canonical_hash:
        return _blocked_decision(
            result=BLOCKED_ATTACHMENT_NOT_CONFIRMED,
            canonical_report=canonical_payload,
            attachment_payload=attachment_payload,
            reason="Attachment evidence basename hash does not match the canonical report basename.",
            live_browser_used=False,
        )

    safety = dict(SAFETY_FLAGS)
    safety["attachment_confirmed"] = True
    safety["file_upload_attempted"] = bool(attachment_payload.get("file_upload_attempted", attachment_payload.get("upload_attempted_before_verification", True)))
    safety["live_browser_used"] = bool(live_browser)

    if live_browser and confirm_live_browser_text != LIVE_CONFIRM_TEXT:
        return _blocked_decision(
            result=BLOCKED_SEND_CONFIRMATION_MISSING,
            canonical_report=canonical_payload,
            attachment_payload=attachment_payload,
            reason=f"Live send gate requires --confirm-live-browser-text {LIVE_CONFIRM_TEXT}; submit remains blocked.",
            live_browser_used=False,
        )

    if allow_submit:
        return _blocked_decision(
            result=BLOCKED_SEND_ACTION_NOT_IMPLEMENTED,
            canonical_report=canonical_payload,
            attachment_payload=attachment_payload,
            reason="Submit action is intentionally not implemented in this patch; this patch only emits readiness evidence.",
            live_browser_used=bool(live_browser),
        )

    return SendGateDecision(
        ok=True,
        result=PASS_SEND_READY_NO_SUBMIT,
        expected_browser=EXPECTED_BROWSER,
        canonical_report=canonical_payload,
        attachment_evidence_result=str(attachment_result),
        attachment_confirmed=True,
        expected_basename=str(expected_basename),
        expected_basename_sha256=str(expected_hash),
        submit_action_allowed=False,
        send_button_pressed=False,
        chatgpt_submit_performed=False,
        raw_conversation_text_logged=False,
        conversation_text_logged=False,
        live_browser_used=bool(live_browser),
        safety_flags=safety,
        reason="Attachment is confirmed and send readiness is satisfied; actual submit remains blocked by policy in this patch.",
    )


def write_send_gate_decision(decision: SendGateDecision, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(decision.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path