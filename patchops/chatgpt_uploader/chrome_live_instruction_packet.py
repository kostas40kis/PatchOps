from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED = "PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED"
PASS_CHROME_LIVE_INSTRUCTION_PACKET_WRITTEN = "PASS_CHROME_LIVE_INSTRUCTION_PACKET_WRITTEN"
BLOCKED_LIVE_INSTRUCTION_BOUNDARY_MISSING = "BLOCKED_LIVE_INSTRUCTION_BOUNDARY_MISSING"
BLOCKED_LIVE_INSTRUCTION_BOUNDARY_INVALID_JSON = "BLOCKED_LIVE_INSTRUCTION_BOUNDARY_INVALID_JSON"
BLOCKED_LIVE_INSTRUCTION_UNSUPPORTED_KIND = "BLOCKED_LIVE_INSTRUCTION_UNSUPPORTED_KIND"
BLOCKED_LIVE_INSTRUCTION_BOUNDARY_NOT_CONFIRMED = "BLOCKED_LIVE_INSTRUCTION_BOUNDARY_NOT_CONFIRMED"
BLOCKED_LIVE_INSTRUCTION_UNSAFE = "BLOCKED_LIVE_INSTRUCTION_UNSAFE"

EXPECTED_BROWSER = "chrome"
EXPECTED_BOUNDARY_KIND = "chrome_uploader_explicit_live_action_boundary"
EXPECTED_BOUNDARY_RESULT = "PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED"
PACKET_SCHEMA_VERSION = "1"
PACKET_KIND = "chrome_uploader_live_instruction_packet_no_action"
REQUIRED_CONFIRMATION_TEXT = "PATCHOPS_CONFIRM_CHROME_LIVE_NO_SEND_ACTION"
DEFAULT_BOUNDARY_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_action_boundary.json"
DEFAULT_PACKET_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_instruction_packet.json"

FORBIDDEN_TRUE_FLAGS = {
    "selenium_used",
    "webdriver_used",
    "browser_dom_automation_used",
    "cloudflare_bypass_attempted",
    "captcha_bypass_attempted",
    "conversation_text_logged",
    "raw_conversation_text_logged",
    "random_page_click_performed",
    "chatgpt_submit_performed",
    "browser_action_performed",
    "send_button_pressed",
    "raw_conversation_text_available",
}
REQUIRED_TRUE_FIELDS = {
    "confirmation_required",
    "boundary_confirmed",
    "live_action_allowed",
    "no_send_verified",
    "attachment_verified",
    "safe_for_downstream_planning",
    "read_only_source_contract",
}
REQUIRED_FALSE_FIELDS = {
    "send_allowed",
    "browser_action_performed",
    "chatgpt_submit_performed",
    "raw_conversation_text_available",
}

INSTRUCTIONS = [
    "Use Chrome only; do not switch to Edge, Firefox, generic browser abstractions, WebDriver, or DOM automation.",
    "Ensure the target ChatGPT conversation is already open in a visible, human-supervised Chrome window before any future live action.",
    "Confirm you are not asking automation to read or log ChatGPT conversation text.",
    "Limit future live action to the no-send attachment path: focus existing Chrome, open the file picker, provide the canonical path, press Enter in the picker, and verify the attachment chip.",
    "Stop before Send. The send button must not be clicked or activated by this packet or any no-send follow-up.",
    "If the browser target is hidden, minimized, ambiguous, wrong, blocked by Cloudflare/CAPTCHA, or shows an unexpected modal, stop and report evidence instead of clicking.",
]
STOP_CONDITIONS = [
    "visible_chrome_target_missing",
    "wrong_browser_or_non_chrome_target",
    "hidden_or_minimized_browser_window",
    "ambiguous_chrome_target",
    "cloudflare_or_captcha_detected",
    "unexpected_modal_or_error_dialog",
    "send_button_focus_or_submit_risk",
    "conversation_text_required",
    "attachment_chip_missing_or_mismatched",
    "canonical_path_unavailable",
]
ALLOWED_NEXT_SCRIPTS = [
    "scripts/run_uploader_chrome_live_no_send_preflight.py",
    "scripts/run_uploader_chrome_upload_flow.py",
]
ALLOWED_ACTIONS_WITH_HUMAN_CONFIRMATION = [
    "focus_existing_chrome_window",
    "open_file_picker_with_human_visible_target",
    "type_canonical_path_into_picker",
    "press_enter_in_picker",
    "verify_attachment_chip_no_send",
]
ALWAYS_FORBIDDEN = [
    "send_chatgpt_message",
    "press_send_button",
    "read_conversation_text",
    "log_raw_conversation_text",
    "use_dom_automation",
    "use_webdriver",
    "bypass_cloudflare_or_captcha",
    "random_click",
    "open_hidden_browser",
]


@dataclass(frozen=True)
class ChromeLiveInstructionPacket:
    ok: bool
    result: str
    schema_version: str
    packet_kind: str
    expected_browser: str
    source_boundary_basename: str | None
    source_boundary_sha256: str | None
    source_ready_basename: str | None
    source_consumed_basename: str | None
    source_handoff_basename: str | None
    source_acceptance_basename: str | None
    boundary_kind: str | None
    boundary_result: str | None
    boundary_confirmed: bool
    live_action_allowed_by_boundary: bool
    packet_performs_browser_action: bool
    packet_performs_chatgpt_submit: bool
    packet_reads_conversation_text: bool
    send_allowed: bool
    no_send_verified: bool
    attachment_verified: bool
    safe_for_downstream_planning: bool
    human_must_confirm_visible_chrome: bool
    human_must_verify_no_send: bool
    instructions: list[str]
    stop_conditions: list[str]
    allowed_next_scripts: list[str]
    allowed_actions_with_human_confirmation: list[str]
    always_forbidden: list[str]
    forbidden_true_flags: list[str]
    packet_created_utc: str | None
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def sha256_file(path: Path | str) -> str:
    resolved = Path(path).expanduser().resolve()
    digest = hashlib.sha256()
    with resolved.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bool(payload: Mapping[str, Any], key: str) -> bool:
    if key in payload:
        return bool(payload[key])
    safety = payload.get("safety_flags")
    if isinstance(safety, dict) and key in safety:
        return bool(safety[key])
    return False


def forbidden_flags(payload: Mapping[str, Any]) -> list[str]:
    found = set(str(item) for item in payload.get("forbidden_true_flags", []) if item)
    safety = payload.get("safety_flags")
    if isinstance(safety, dict):
        for key in FORBIDDEN_TRUE_FLAGS:
            if bool(safety.get(key, False)):
                found.add(key)
    for key in FORBIDDEN_TRUE_FLAGS:
        if bool(payload.get(key, False)):
            found.add(key)
    return sorted(found)


def _packet(
    *,
    ok: bool,
    result: str,
    payload: Mapping[str, Any],
    source_boundary_basename: str | None,
    source_boundary_sha256: str | None,
    reason: str,
) -> ChromeLiveInstructionPacket:
    return ChromeLiveInstructionPacket(
        ok=bool(ok),
        result=result,
        schema_version=PACKET_SCHEMA_VERSION,
        packet_kind=PACKET_KIND,
        expected_browser=EXPECTED_BROWSER,
        source_boundary_basename=source_boundary_basename,
        source_boundary_sha256=source_boundary_sha256,
        source_ready_basename=payload.get("source_ready_basename"),
        source_consumed_basename=payload.get("source_consumed_basename"),
        source_handoff_basename=payload.get("source_handoff_basename"),
        source_acceptance_basename=payload.get("source_acceptance_basename"),
        boundary_kind=payload.get("boundary_kind"),
        boundary_result=payload.get("result"),
        boundary_confirmed=bool(payload.get("boundary_confirmed", False)),
        live_action_allowed_by_boundary=bool(payload.get("live_action_allowed", False)) if ok else False,
        packet_performs_browser_action=False,
        packet_performs_chatgpt_submit=False,
        packet_reads_conversation_text=False,
        send_allowed=False,
        no_send_verified=bool(payload.get("no_send_verified", False)),
        attachment_verified=bool(payload.get("attachment_verified", False)),
        safe_for_downstream_planning=bool(payload.get("safe_for_downstream_planning", False)),
        human_must_confirm_visible_chrome=True,
        human_must_verify_no_send=True,
        instructions=list(INSTRUCTIONS) if ok else [],
        stop_conditions=list(STOP_CONDITIONS),
        allowed_next_scripts=list(ALLOWED_NEXT_SCRIPTS) if ok else [],
        allowed_actions_with_human_confirmation=list(ALLOWED_ACTIONS_WITH_HUMAN_CONFIRMATION) if ok else [],
        always_forbidden=list(ALWAYS_FORBIDDEN),
        forbidden_true_flags=forbidden_flags(payload),
        packet_created_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat() if ok else None,
        reason=reason,
    )


def validate_boundary_payload(
    payload: Mapping[str, Any],
    *,
    source_boundary_basename: str | None = None,
    source_boundary_sha256: str | None = None,
) -> ChromeLiveInstructionPacket:
    boundary_kind = payload.get("boundary_kind")
    boundary_result = payload.get("result")
    forbidden = forbidden_flags(payload)
    missing_true = sorted(key for key in REQUIRED_TRUE_FIELDS if not bool(payload.get(key, False)))
    false_violations = sorted(key for key in REQUIRED_FALSE_FIELDS if bool(payload.get(key, False)))

    if boundary_kind != EXPECTED_BOUNDARY_KIND:
        return _packet(
            ok=False,
            result=BLOCKED_LIVE_INSTRUCTION_UNSUPPORTED_KIND,
            payload=payload,
            source_boundary_basename=source_boundary_basename,
            source_boundary_sha256=source_boundary_sha256,
            reason="Boundary kind is not chrome_uploader_explicit_live_action_boundary.",
        )
    if forbidden:
        return _packet(
            ok=False,
            result=BLOCKED_LIVE_INSTRUCTION_UNSAFE,
            payload=payload,
            source_boundary_basename=source_boundary_basename,
            source_boundary_sha256=source_boundary_sha256,
            reason="Boundary contains forbidden true safety flags.",
        )
    if (
        not bool(payload.get("ok", False))
        or boundary_result != EXPECTED_BOUNDARY_RESULT
        or payload.get("expected_browser") != EXPECTED_BROWSER
        or payload.get("required_confirmation_text") != REQUIRED_CONFIRMATION_TEXT
        or missing_true
        or false_violations
    ):
        reason = "Boundary is not confirmed or not ready for no-action instruction packet generation."
        if missing_true:
            reason += " Missing true fields: " + ",".join(missing_true)
        if false_violations:
            reason += " False-field violations: " + ",".join(false_violations)
        return _packet(
            ok=False,
            result=BLOCKED_LIVE_INSTRUCTION_BOUNDARY_NOT_CONFIRMED,
            payload=payload,
            source_boundary_basename=source_boundary_basename,
            source_boundary_sha256=source_boundary_sha256,
            reason=reason,
        )

    return _packet(
        ok=True,
        result=PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED,
        payload=payload,
        source_boundary_basename=source_boundary_basename,
        source_boundary_sha256=source_boundary_sha256,
        reason="No-action live instruction packet generated from confirmed Chrome boundary; no browser action was performed.",
    )


def load_and_validate_boundary(path: Path | str) -> ChromeLiveInstructionPacket:
    boundary_path = Path(path).expanduser().resolve()
    if not boundary_path.exists():
        return ChromeLiveInstructionPacket(
            ok=False,
            result=BLOCKED_LIVE_INSTRUCTION_BOUNDARY_MISSING,
            schema_version=PACKET_SCHEMA_VERSION,
            packet_kind=PACKET_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_boundary_basename=boundary_path.name,
            source_boundary_sha256=None,
            source_ready_basename=None,
            source_consumed_basename=None,
            source_handoff_basename=None,
            source_acceptance_basename=None,
            boundary_kind=None,
            boundary_result=None,
            boundary_confirmed=False,
            live_action_allowed_by_boundary=False,
            packet_performs_browser_action=False,
            packet_performs_chatgpt_submit=False,
            packet_reads_conversation_text=False,
            send_allowed=False,
            no_send_verified=False,
            attachment_verified=False,
            safe_for_downstream_planning=False,
            human_must_confirm_visible_chrome=True,
            human_must_verify_no_send=True,
            instructions=[],
            stop_conditions=list(STOP_CONDITIONS),
            allowed_next_scripts=[],
            allowed_actions_with_human_confirmation=[],
            always_forbidden=list(ALWAYS_FORBIDDEN),
            forbidden_true_flags=[],
            packet_created_utc=None,
            reason="Boundary JSON file is missing.",
        )
    try:
        payload = json.loads(boundary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ChromeLiveInstructionPacket(
            ok=False,
            result=BLOCKED_LIVE_INSTRUCTION_BOUNDARY_INVALID_JSON,
            schema_version=PACKET_SCHEMA_VERSION,
            packet_kind=PACKET_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_boundary_basename=boundary_path.name,
            source_boundary_sha256=sha256_file(boundary_path),
            source_ready_basename=None,
            source_consumed_basename=None,
            source_handoff_basename=None,
            source_acceptance_basename=None,
            boundary_kind=None,
            boundary_result=None,
            boundary_confirmed=False,
            live_action_allowed_by_boundary=False,
            packet_performs_browser_action=False,
            packet_performs_chatgpt_submit=False,
            packet_reads_conversation_text=False,
            send_allowed=False,
            no_send_verified=False,
            attachment_verified=False,
            safe_for_downstream_planning=False,
            human_must_confirm_visible_chrome=True,
            human_must_verify_no_send=True,
            instructions=[],
            stop_conditions=list(STOP_CONDITIONS),
            allowed_next_scripts=[],
            allowed_actions_with_human_confirmation=[],
            always_forbidden=list(ALWAYS_FORBIDDEN),
            forbidden_true_flags=[],
            packet_created_utc=None,
            reason=f"Boundary JSON is invalid: {exc}",
        )
    if not isinstance(payload, dict):
        payload = {}
    return validate_boundary_payload(
        payload,
        source_boundary_basename=boundary_path.name,
        source_boundary_sha256=sha256_file(boundary_path),
    )


def write_instruction_packet(packet: ChromeLiveInstructionPacket, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = packet.to_payload()
    payload["write_result"] = PASS_CHROME_LIVE_INSTRUCTION_PACKET_WRITTEN if packet.ok else packet.result
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_instruction_packet_marker(packet: ChromeLiveInstructionPacket, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Chrome live instruction packet",
        "==============================",
        f"result:{packet.result}",
        f"ok:{str(packet.ok).lower()}",
        f"packet_kind:{packet.packet_kind}",
        f"expected_browser:{packet.expected_browser}",
        f"boundary_kind:{packet.boundary_kind or ''}",
        f"boundary_result:{packet.boundary_result or ''}",
        f"boundary_confirmed:{str(packet.boundary_confirmed).lower()}",
        f"live_action_allowed_by_boundary:{str(packet.live_action_allowed_by_boundary).lower()}",
        "packet_performs_browser_action:false",
        "packet_performs_chatgpt_submit:false",
        "packet_reads_conversation_text:false",
        "send_allowed:false",
        f"human_must_confirm_visible_chrome:{str(packet.human_must_confirm_visible_chrome).lower()}",
        f"human_must_verify_no_send:{str(packet.human_must_verify_no_send).lower()}",
        "selenium_used:false",
        "webdriver_used:false",
        "browser_dom_automation_used:false",
        "cloudflare_bypass_attempted:false",
        "captcha_bypass_attempted:false",
        "conversation_text_logged:false",
        "raw_conversation_text_logged:false",
        "random_page_click_performed:false",
        "",
        "Instructions",
        "------------",
    ]
    lines.extend(f"- {item}" for item in packet.instructions)
    lines.extend(["", "Stop conditions", "---------------"])
    lines.extend(f"- {item}" for item in packet.stop_conditions)
    lines.extend(["", f"allowed_next_scripts:{','.join(packet.allowed_next_scripts)}", f"always_forbidden:{','.join(packet.always_forbidden)}", f"reason:{packet.reason}"])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path