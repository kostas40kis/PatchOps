from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.chatgpt_uploader.chrome_attachment_verifier import (
    PASS_ATTACHMENT_CONFIRMED_NO_SEND,
    build_attachment_candidate,
    verify_attachment_no_send,
)
from patchops.chatgpt_uploader.chrome_send_gate import PASS_SEND_READY_NO_SUBMIT, evaluate_send_gate_no_submit
from patchops.chatgpt_uploader.chrome_submit_action import (
    PASS_CHROME_SUBMIT_ACTION_MOCKED,
    PASS_CHROME_SUBMIT_ACTION_PERFORMED,
    run_chrome_submit_action,
)
from patchops.chatgpt_uploader.chrome_submit_adapter import (
    PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION,
    PASS_CHROME_SUBMIT_READY_NO_ACTION,
    evaluate_chrome_submit_adapter,
)

PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT = "PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT"
PASS_CHROME_UPLOAD_FLOW_SUBMIT_MOCKED = "PASS_CHROME_UPLOAD_FLOW_SUBMIT_MOCKED"
PASS_CHROME_UPLOAD_FLOW_SUBMIT_PERFORMED = "PASS_CHROME_UPLOAD_FLOW_SUBMIT_PERFORMED"
BLOCKED_UPLOAD_FLOW_ATTACHMENT = "BLOCKED_UPLOAD_FLOW_ATTACHMENT"
BLOCKED_UPLOAD_FLOW_SEND_GATE = "BLOCKED_UPLOAD_FLOW_SEND_GATE"
BLOCKED_UPLOAD_FLOW_SUBMIT_ADAPTER = "BLOCKED_UPLOAD_FLOW_SUBMIT_ADAPTER"
BLOCKED_UPLOAD_FLOW_SUBMIT_ACTION = "BLOCKED_UPLOAD_FLOW_SUBMIT_ACTION"

EXPECTED_BROWSER = "chrome"

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
    "send_gate_ready": False,
    "submit_adapter_ready": False,
    "send_button_pressed": False,
    "submit_action_performed": False,
    "chatgpt_submit_performed": False,
    "live_browser_used": False,
    "orchestrator_used": True,
}


@dataclass(frozen=True)
class ChromeUploadFlowEvidence:
    ok: bool
    result: str
    expected_browser: str
    attachment_result: str | None
    send_gate_result: str | None
    submit_adapter_result: str | None
    submit_action_result: str | None
    upload_attempted_before_verification: bool
    attachment_confirmed: bool
    send_gate_ready: bool
    submit_adapter_ready: bool
    submit_action_requested: bool
    submit_action_performed: bool
    chatgpt_submit_performed: bool
    send_button_pressed: bool
    raw_conversation_text_logged: bool
    conversation_text_logged: bool
    live_browser_used: bool
    canonical_report_basename: str | None
    canonical_report_path_hash: str | None
    stage_payloads: dict[str, Any]
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


def _merge_safety(*payloads: Mapping[str, Any], live_browser_used: bool = False) -> dict[str, bool]:
    safety = dict(SAFETY_FLAGS)
    for payload in payloads:
        nested = payload.get("safety_flags")
        if isinstance(nested, dict):
            for key in safety:
                if key in nested:
                    safety[key] = bool(nested[key])
        for key in ("file_upload_attempted", "attachment_confirmed", "send_button_pressed", "submit_action_performed", "chatgpt_submit_performed"):
            if key in payload:
                safety[key] = bool(payload[key])
    safety["send_gate_ready"] = any(payload.get("result") == PASS_SEND_READY_NO_SUBMIT and bool(payload.get("ok", False)) for payload in payloads)
    safety["submit_adapter_ready"] = any(
        payload.get("result") in {PASS_CHROME_SUBMIT_READY_NO_ACTION, PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION} and bool(payload.get("ok", False))
        for payload in payloads
    )
    safety["live_browser_used"] = bool(live_browser_used or any(bool(payload.get("live_browser_used", False)) for payload in payloads))
    safety["orchestrator_used"] = True
    safety["selenium_used"] = False
    safety["webdriver_used"] = False
    safety["browser_dom_automation_used"] = False
    safety["conversation_text_logged"] = False
    safety["raw_conversation_text_logged"] = False
    return safety


def _flow(
    *,
    ok: bool,
    result: str,
    attachment: Mapping[str, Any],
    send_gate: Mapping[str, Any] | None = None,
    submit_adapter: Mapping[str, Any] | None = None,
    submit_action: Mapping[str, Any] | None = None,
    submit_action_requested: bool = False,
    reason: str,
) -> ChromeUploadFlowEvidence:
    send_gate_payload = dict(send_gate or {})
    submit_adapter_payload = dict(submit_adapter or {})
    submit_action_payload = dict(submit_action or {})
    safety = _merge_safety(
        attachment,
        send_gate_payload,
        submit_adapter_payload,
        submit_action_payload,
    )
    canonical = attachment.get("canonical_report") if isinstance(attachment.get("canonical_report"), dict) else {}
    return ChromeUploadFlowEvidence(
        ok=bool(ok),
        result=result,
        expected_browser=EXPECTED_BROWSER,
        attachment_result=attachment.get("result"),
        send_gate_result=send_gate_payload.get("result"),
        submit_adapter_result=submit_adapter_payload.get("result"),
        submit_action_result=submit_action_payload.get("result"),
        upload_attempted_before_verification=bool(attachment.get("upload_attempted_before_verification", attachment.get("file_upload_attempted", False))),
        attachment_confirmed=bool(attachment.get("attachment_confirmed", False)),
        send_gate_ready=send_gate_payload.get("result") == PASS_SEND_READY_NO_SUBMIT and bool(send_gate_payload.get("ok", False)),
        submit_adapter_ready=submit_adapter_payload.get("result") in {PASS_CHROME_SUBMIT_READY_NO_ACTION, PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION} and bool(submit_adapter_payload.get("ok", False)),
        submit_action_requested=bool(submit_action_requested),
        submit_action_performed=bool(submit_action_payload.get("submit_action_performed", False)),
        chatgpt_submit_performed=bool(submit_action_payload.get("chatgpt_submit_performed", False)),
        send_button_pressed=bool(submit_action_payload.get("send_button_pressed", False)),
        raw_conversation_text_logged=False,
        conversation_text_logged=False,
        live_browser_used=bool(safety.get("live_browser_used", False)),
        canonical_report_basename=canonical.get("basename") or attachment.get("expected_basename"),
        canonical_report_path_hash=canonical.get("path_hash"),
        stage_payloads={
            "attachment": dict(attachment),
            "send_gate": send_gate_payload,
            "submit_adapter": submit_adapter_payload,
            "submit_action": submit_action_payload,
        },
        safety_flags=safety,
        reason=reason,
    )


def run_chrome_upload_flow(
    *,
    canonical_report_path: Path | str,
    upload_attempted_before_verification: bool = True,
    attachment_descriptors: Sequence[Mapping[str, Any] | Any] = (),
    submit_action_requested: bool = False,
    submit_backend: str = "ctrl_enter_once",
    live_browser: bool = False,
    submit_confirm_text: str | None = None,
    target_hwnd: int | None = None,
    allow_submit_action: bool = False,
    mock_submit_success: bool = False,
) -> ChromeUploadFlowEvidence:
    attachment = verify_attachment_no_send(
        canonical_report_path=canonical_report_path,
        upload_attempted_before_verification=upload_attempted_before_verification,
        attachment_descriptors=attachment_descriptors,
        live_browser=False,
    )
    attachment_payload = attachment.to_payload()
    if attachment.result != PASS_ATTACHMENT_CONFIRMED_NO_SEND or not attachment.attachment_confirmed:
        return _flow(
            ok=False,
            result=BLOCKED_UPLOAD_FLOW_ATTACHMENT,
            attachment=attachment_payload,
            submit_action_requested=submit_action_requested,
            reason="Upload flow blocked at attachment verification stage.",
        )

    send_gate = evaluate_send_gate_no_submit(canonical_report_path=canonical_report_path, attachment_evidence=attachment_payload)
    send_gate_payload = send_gate.to_payload()
    if send_gate.result != PASS_SEND_READY_NO_SUBMIT or not send_gate.ok:
        return _flow(
            ok=False,
            result=BLOCKED_UPLOAD_FLOW_SEND_GATE,
            attachment=attachment_payload,
            send_gate=send_gate_payload,
            submit_action_requested=submit_action_requested,
            reason="Upload flow blocked at send gate stage.",
        )

    adapter = evaluate_chrome_submit_adapter(send_gate_decision=send_gate_payload)
    adapter_payload = adapter.to_payload()
    if adapter.result not in {PASS_CHROME_SUBMIT_READY_NO_ACTION, PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION} or not adapter.ok:
        return _flow(
            ok=False,
            result=BLOCKED_UPLOAD_FLOW_SUBMIT_ADAPTER,
            attachment=attachment_payload,
            send_gate=send_gate_payload,
            submit_adapter=adapter_payload,
            submit_action_requested=submit_action_requested,
            reason="Upload flow blocked at submit adapter stage.",
        )

    if not submit_action_requested:
        return _flow(
            ok=True,
            result=PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT,
            attachment=attachment_payload,
            send_gate=send_gate_payload,
            submit_adapter=adapter_payload,
            submit_action_requested=False,
            reason="Upload flow is ready through submit adapter; submit action was not requested.",
        )

    submit = run_chrome_submit_action(
        submit_adapter_decision=adapter_payload,
        submit_backend=submit_backend,
        live_browser=live_browser,
        confirm_live_browser_text=submit_confirm_text,
        target_hwnd=target_hwnd,
        allow_submit_action=allow_submit_action,
        mock_submit_success=mock_submit_success,
    )
    submit_payload = submit.to_payload()
    if not submit.ok:
        return _flow(
            ok=False,
            result=BLOCKED_UPLOAD_FLOW_SUBMIT_ACTION,
            attachment=attachment_payload,
            send_gate=send_gate_payload,
            submit_adapter=adapter_payload,
            submit_action=submit_payload,
            submit_action_requested=True,
            reason="Upload flow blocked at submit action stage.",
        )

    final_result = PASS_CHROME_UPLOAD_FLOW_SUBMIT_PERFORMED if submit.result == PASS_CHROME_SUBMIT_ACTION_PERFORMED else PASS_CHROME_UPLOAD_FLOW_SUBMIT_MOCKED
    return _flow(
        ok=True,
        result=final_result,
        attachment=attachment_payload,
        send_gate=send_gate_payload,
        submit_adapter=adapter_payload,
        submit_action=submit_payload,
        submit_action_requested=True,
        reason="Upload flow completed through gated submit action evidence.",
    )


def build_attachment_descriptor(*, basename: str, visible: bool = True, stable: bool = True, remove_button_visible: bool = True, progress_visible: bool = False, error_visible: bool = False) -> dict[str, Any]:
    return build_attachment_candidate(
        basename=basename,
        visible=visible,
        stable=stable,
        remove_button_visible=remove_button_visible,
        progress_visible=progress_visible,
        error_visible=error_visible,
        source="orchestrator_descriptor",
    ).to_payload()


def write_chrome_upload_flow_evidence(evidence: ChromeUploadFlowEvidence, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evidence.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path