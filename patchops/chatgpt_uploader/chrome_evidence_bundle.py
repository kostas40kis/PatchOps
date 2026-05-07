from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

PASS_EVIDENCE_BUNDLE_VALIDATED = "PASS_EVIDENCE_BUNDLE_VALIDATED"
PASS_EVIDENCE_BUNDLE_SUMMARY_WRITTEN = "PASS_EVIDENCE_BUNDLE_SUMMARY_WRITTEN"
BLOCKED_EVIDENCE_BUNDLE_INVALID_JSON = "BLOCKED_EVIDENCE_BUNDLE_INVALID_JSON"
BLOCKED_EVIDENCE_BUNDLE_MISSING = "BLOCKED_EVIDENCE_BUNDLE_MISSING"
BLOCKED_EVIDENCE_BUNDLE_UNSAFE = "BLOCKED_EVIDENCE_BUNDLE_UNSAFE"
BLOCKED_EVIDENCE_BUNDLE_UNRECOGNIZED_RESULT = "BLOCKED_EVIDENCE_BUNDLE_UNRECOGNIZED_RESULT"

EXPECTED_BROWSER = "chrome"
ACCEPTED_FLOW_RESULTS = {
    "PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT",
    "PASS_CHROME_UPLOAD_FLOW_SUBMIT_MOCKED",
    "PASS_CHROME_UPLOAD_FLOW_SUBMIT_PERFORMED",
    "BLOCKED_UPLOAD_FLOW_ATTACHMENT",
    "BLOCKED_UPLOAD_FLOW_SEND_GATE",
    "BLOCKED_UPLOAD_FLOW_SUBMIT_ADAPTER",
    "BLOCKED_UPLOAD_FLOW_SUBMIT_ACTION",
}
FORBIDDEN_TRUE_FLAGS = {
    "selenium_used",
    "webdriver_used",
    "browser_dom_automation_used",
    "cloudflare_bypass_attempted",
    "captcha_bypass_attempted",
    "conversation_text_logged",
    "raw_conversation_text_logged",
    "random_page_click_performed",
}


@dataclass(frozen=True)
class ChromeEvidenceBundle:
    ok: bool
    result: str
    expected_browser: str
    flow_result: str | None
    flow_ok: bool
    evidence_path_hash: str | None
    evidence_basename: str | None
    canonical_report_basename: str | None
    canonical_report_path_hash: str | None
    attachment_confirmed: bool
    send_gate_ready: bool
    submit_adapter_ready: bool
    submit_action_requested: bool
    submit_action_performed: bool
    chatgpt_submit_performed: bool
    live_browser_used: bool
    forbidden_true_flags: list[str]
    raw_conversation_text_logged: bool
    conversation_text_logged: bool
    summary_lines: list[str]
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _bool_from_payload(payload: Mapping[str, Any], key: str) -> bool:
    if key in payload:
        return bool(payload[key])
    safety = payload.get("safety_flags")
    if isinstance(safety, dict) and key in safety:
        return bool(safety[key])
    return False


def _forbidden_true_flags(payload: Mapping[str, Any]) -> list[str]:
    found: list[str] = []
    safety = payload.get("safety_flags") if isinstance(payload.get("safety_flags"), dict) else {}
    for key in sorted(FORBIDDEN_TRUE_FLAGS):
        if bool(payload.get(key, False)) or bool(safety.get(key, False)):
            found.append(key)
    return found


def _summary_lines(payload: Mapping[str, Any], *, evidence_basename: str | None, evidence_path_hash: str | None) -> list[str]:
    lines = [
        "Chrome upload flow evidence summary",
        "====================================",
        f"evidence_file        : {evidence_basename or ''}",
        f"evidence_sha256      : {evidence_path_hash or ''}",
        f"flow_result          : {payload.get('result') or ''}",
        f"flow_ok              : {str(bool(payload.get('ok', False))).lower()}",
        f"canonical_report     : {payload.get('canonical_report_basename') or ''}",
        f"canonical_report_hash: {payload.get('canonical_report_path_hash') or ''}",
        f"attachment_confirmed : {str(bool(payload.get('attachment_confirmed', False))).lower()}",
        f"send_gate_ready      : {str(bool(payload.get('send_gate_ready', False))).lower()}",
        f"submit_adapter_ready : {str(bool(payload.get('submit_adapter_ready', False))).lower()}",
        f"submit_requested     : {str(bool(payload.get('submit_action_requested', False))).lower()}",
        f"submit_performed     : {str(bool(payload.get('submit_action_performed', False))).lower()}",
        f"chatgpt_submitted    : {str(bool(payload.get('chatgpt_submit_performed', False))).lower()}",
        f"live_browser_used    : {str(bool(payload.get('live_browser_used', False))).lower()}",
        "",
        "Safety invariants",
        "-----------------",
        "selenium_used:false",
        "webdriver_used:false",
        "browser_dom_automation_used:false",
        "cloudflare_bypass_attempted:false",
        "captcha_bypass_attempted:false",
        "conversation_text_logged:false",
        "raw_conversation_text_logged:false",
        "random_page_click_performed:false",
    ]
    return lines


def validate_flow_evidence_payload(payload: Mapping[str, Any], *, evidence_basename: str | None = None, evidence_path_hash: str | None = None) -> ChromeEvidenceBundle:
    flow_result = payload.get("result")
    forbidden = _forbidden_true_flags(payload)
    lines = _summary_lines(payload, evidence_basename=evidence_basename, evidence_path_hash=evidence_path_hash)

    if flow_result not in ACCEPTED_FLOW_RESULTS:
        return ChromeEvidenceBundle(
            ok=False,
            result=BLOCKED_EVIDENCE_BUNDLE_UNRECOGNIZED_RESULT,
            expected_browser=EXPECTED_BROWSER,
            flow_result=str(flow_result) if flow_result is not None else None,
            flow_ok=bool(payload.get("ok", False)),
            evidence_path_hash=evidence_path_hash,
            evidence_basename=evidence_basename,
            canonical_report_basename=payload.get("canonical_report_basename"),
            canonical_report_path_hash=payload.get("canonical_report_path_hash"),
            attachment_confirmed=bool(payload.get("attachment_confirmed", False)),
            send_gate_ready=bool(payload.get("send_gate_ready", False)),
            submit_adapter_ready=bool(payload.get("submit_adapter_ready", False)),
            submit_action_requested=bool(payload.get("submit_action_requested", False)),
            submit_action_performed=bool(payload.get("submit_action_performed", False)),
            chatgpt_submit_performed=bool(payload.get("chatgpt_submit_performed", False)),
            live_browser_used=bool(payload.get("live_browser_used", False)),
            forbidden_true_flags=forbidden,
            raw_conversation_text_logged=_bool_from_payload(payload, "raw_conversation_text_logged"),
            conversation_text_logged=_bool_from_payload(payload, "conversation_text_logged"),
            summary_lines=lines,
            reason="Flow evidence result label is not recognized.",
        )

    if forbidden:
        return ChromeEvidenceBundle(
            ok=False,
            result=BLOCKED_EVIDENCE_BUNDLE_UNSAFE,
            expected_browser=EXPECTED_BROWSER,
            flow_result=str(flow_result),
            flow_ok=bool(payload.get("ok", False)),
            evidence_path_hash=evidence_path_hash,
            evidence_basename=evidence_basename,
            canonical_report_basename=payload.get("canonical_report_basename"),
            canonical_report_path_hash=payload.get("canonical_report_path_hash"),
            attachment_confirmed=bool(payload.get("attachment_confirmed", False)),
            send_gate_ready=bool(payload.get("send_gate_ready", False)),
            submit_adapter_ready=bool(payload.get("submit_adapter_ready", False)),
            submit_action_requested=bool(payload.get("submit_action_requested", False)),
            submit_action_performed=bool(payload.get("submit_action_performed", False)),
            chatgpt_submit_performed=bool(payload.get("chatgpt_submit_performed", False)),
            live_browser_used=bool(payload.get("live_browser_used", False)),
            forbidden_true_flags=forbidden,
            raw_conversation_text_logged=_bool_from_payload(payload, "raw_conversation_text_logged"),
            conversation_text_logged=_bool_from_payload(payload, "conversation_text_logged"),
            summary_lines=lines,
            reason="Flow evidence has forbidden true safety flags.",
        )

    return ChromeEvidenceBundle(
        ok=True,
        result=PASS_EVIDENCE_BUNDLE_VALIDATED,
        expected_browser=EXPECTED_BROWSER,
        flow_result=str(flow_result),
        flow_ok=bool(payload.get("ok", False)),
        evidence_path_hash=evidence_path_hash,
        evidence_basename=evidence_basename,
        canonical_report_basename=payload.get("canonical_report_basename"),
        canonical_report_path_hash=payload.get("canonical_report_path_hash"),
        attachment_confirmed=bool(payload.get("attachment_confirmed", False)),
        send_gate_ready=bool(payload.get("send_gate_ready", False)),
        submit_adapter_ready=bool(payload.get("submit_adapter_ready", False)),
        submit_action_requested=bool(payload.get("submit_action_requested", False)),
        submit_action_performed=bool(payload.get("submit_action_performed", False)),
        chatgpt_submit_performed=bool(payload.get("chatgpt_submit_performed", False)),
        live_browser_used=bool(payload.get("live_browser_used", False)),
        forbidden_true_flags=[],
        raw_conversation_text_logged=False,
        conversation_text_logged=False,
        summary_lines=lines,
        reason="Flow evidence bundle validated with safety invariants intact.",
    )


def load_and_validate_flow_evidence(path: Path | str) -> ChromeEvidenceBundle:
    evidence_path = Path(path).expanduser().resolve()
    if not evidence_path.exists():
        return ChromeEvidenceBundle(
            ok=False,
            result=BLOCKED_EVIDENCE_BUNDLE_MISSING,
            expected_browser=EXPECTED_BROWSER,
            flow_result=None,
            flow_ok=False,
            evidence_path_hash=None,
            evidence_basename=evidence_path.name,
            canonical_report_basename=None,
            canonical_report_path_hash=None,
            attachment_confirmed=False,
            send_gate_ready=False,
            submit_adapter_ready=False,
            submit_action_requested=False,
            submit_action_performed=False,
            chatgpt_submit_performed=False,
            live_browser_used=False,
            forbidden_true_flags=[],
            raw_conversation_text_logged=False,
            conversation_text_logged=False,
            summary_lines=[],
            reason="Flow evidence file does not exist.",
        )
    try:
        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ChromeEvidenceBundle(
            ok=False,
            result=BLOCKED_EVIDENCE_BUNDLE_INVALID_JSON,
            expected_browser=EXPECTED_BROWSER,
            flow_result=None,
            flow_ok=False,
            evidence_path_hash=_sha256_file(evidence_path),
            evidence_basename=evidence_path.name,
            canonical_report_basename=None,
            canonical_report_path_hash=None,
            attachment_confirmed=False,
            send_gate_ready=False,
            submit_adapter_ready=False,
            submit_action_requested=False,
            submit_action_performed=False,
            chatgpt_submit_performed=False,
            live_browser_used=False,
            forbidden_true_flags=[],
            raw_conversation_text_logged=False,
            conversation_text_logged=False,
            summary_lines=[],
            reason=f"Flow evidence JSON is invalid: {exc}",
        )
    if not isinstance(payload, dict):
        payload = {}
    return validate_flow_evidence_payload(payload, evidence_basename=evidence_path.name, evidence_path_hash=_sha256_file(evidence_path))


def write_evidence_bundle(bundle: ChromeEvidenceBundle, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = bundle.to_payload()
    result = PASS_EVIDENCE_BUNDLE_SUMMARY_WRITTEN if bundle.ok else bundle.result
    payload["write_result"] = result
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_evidence_summary_text(bundle: ChromeEvidenceBundle, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = list(bundle.summary_lines)
    if not lines:
        lines = [
            "Chrome upload flow evidence summary",
            "====================================",
            f"result: {bundle.result}",
            f"reason: {bundle.reason}",
        ]
    lines.extend(["", f"bundle_result       : {bundle.result}", f"bundle_ok           : {str(bundle.ok).lower()}", f"bundle_reason       : {bundle.reason}"])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path