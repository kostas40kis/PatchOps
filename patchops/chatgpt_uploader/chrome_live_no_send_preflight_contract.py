from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED = "PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED"
PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_WRITTEN = "PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_WRITTEN"
BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_MISSING = "BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_MISSING"
BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_INVALID_JSON = "BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_INVALID_JSON"
BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSUPPORTED_KIND = "BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSUPPORTED_KIND"
BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_NOT_READY = "BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_NOT_READY"
BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSAFE = "BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSAFE"

EXPECTED_BROWSER = "chrome"
EXPECTED_PACKET_KIND = "chrome_uploader_live_instruction_packet_no_action"
EXPECTED_PACKET_RESULT = "PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED"
EXPECTED_BOUNDARY_KIND = "chrome_uploader_explicit_live_action_boundary"
EXPECTED_BOUNDARY_RESULT = "PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED"
CONTRACT_SCHEMA_VERSION = "1"
CONTRACT_KIND = "chrome_uploader_live_no_send_preflight_contract"
DEFAULT_PACKET_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_instruction_packet.json"
DEFAULT_CONTRACT_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_no_send_preflight_contract.json"

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
    "packet_performs_browser_action",
    "packet_performs_chatgpt_submit",
    "packet_reads_conversation_text",
    "send_allowed",
}
REQUIRED_TRUE_FIELDS = {
    "boundary_confirmed",
    "live_action_allowed_by_boundary",
    "no_send_verified",
    "attachment_verified",
    "safe_for_downstream_planning",
    "human_must_confirm_visible_chrome",
    "human_must_verify_no_send",
}
REQUIRED_FALSE_FIELDS = {
    "packet_performs_browser_action",
    "packet_performs_chatgpt_submit",
    "packet_reads_conversation_text",
    "send_allowed",
}

REQUIRED_VISIBLE_STATE = [
    "visible_existing_chrome_window",
    "correct_target_conversation_already_open",
    "file_picker_not_open_initially",
    "send_button_not_focused",
    "no_cloudflare_or_captcha",
    "no_unexpected_modal",
]
PERMITTED_FUTURE_ACTIONS = [
    "focus_existing_chrome_window",
    "open_file_picker_with_human_visible_target",
    "type_canonical_path_into_picker",
    "press_enter_in_picker",
    "verify_attachment_chip_no_send",
]
FORBIDDEN_ACTIONS = [
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
DEFAULT_ALLOWED_NEXT_SCRIPT = "scripts/run_uploader_chrome_live_no_send_executor.py"


@dataclass(frozen=True)
class ChromeLiveNoSendPreflightContract:
    ok: bool
    result: str
    schema_version: str
    contract_kind: str
    expected_browser: str
    source_packet_basename: str | None
    source_packet_sha256: str | None
    source_boundary_basename: str | None
    source_ready_basename: str | None
    source_consumed_basename: str | None
    source_handoff_basename: str | None
    source_acceptance_basename: str | None
    packet_kind: str | None
    packet_result: str | None
    boundary_kind: str | None
    boundary_result: str | None
    preflight_contract_ready: bool
    no_send_verified: bool
    attachment_verified: bool
    safe_for_downstream_planning: bool
    packet_performs_browser_action: bool
    packet_performs_chatgpt_submit: bool
    packet_reads_conversation_text: bool
    browser_action_performed: bool
    chatgpt_submit_performed: bool
    send_allowed: bool
    raw_conversation_text_available: bool
    human_must_confirm_visible_chrome: bool
    human_must_verify_no_send: bool
    required_visible_state: list[str]
    permitted_future_actions: list[str]
    forbidden_actions: list[str]
    stop_conditions: list[str]
    allowed_next_script: str | None
    forbidden_true_flags: list[str]
    preflight_created_utc: str | None
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


def _list(payload: Mapping[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return []


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


def _contract(
    *,
    ok: bool,
    result: str,
    payload: Mapping[str, Any],
    source_packet_basename: str | None,
    source_packet_sha256: str | None,
    reason: str,
) -> ChromeLiveNoSendPreflightContract:
    stop_conditions = _list(payload, "stop_conditions") or [
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
    return ChromeLiveNoSendPreflightContract(
        ok=bool(ok),
        result=result,
        schema_version=CONTRACT_SCHEMA_VERSION,
        contract_kind=CONTRACT_KIND,
        expected_browser=EXPECTED_BROWSER,
        source_packet_basename=source_packet_basename,
        source_packet_sha256=source_packet_sha256,
        source_boundary_basename=payload.get("source_boundary_basename"),
        source_ready_basename=payload.get("source_ready_basename"),
        source_consumed_basename=payload.get("source_consumed_basename"),
        source_handoff_basename=payload.get("source_handoff_basename"),
        source_acceptance_basename=payload.get("source_acceptance_basename"),
        packet_kind=payload.get("packet_kind"),
        packet_result=payload.get("result"),
        boundary_kind=payload.get("boundary_kind"),
        boundary_result=payload.get("boundary_result"),
        preflight_contract_ready=bool(ok),
        no_send_verified=bool(payload.get("no_send_verified", False)),
        attachment_verified=bool(payload.get("attachment_verified", False)),
        safe_for_downstream_planning=bool(payload.get("safe_for_downstream_planning", False)),
        packet_performs_browser_action=False,
        packet_performs_chatgpt_submit=False,
        packet_reads_conversation_text=False,
        browser_action_performed=False,
        chatgpt_submit_performed=False,
        send_allowed=False,
        raw_conversation_text_available=False,
        human_must_confirm_visible_chrome=bool(payload.get("human_must_confirm_visible_chrome", True)),
        human_must_verify_no_send=bool(payload.get("human_must_verify_no_send", True)),
        required_visible_state=list(REQUIRED_VISIBLE_STATE) if ok else [],
        permitted_future_actions=list(PERMITTED_FUTURE_ACTIONS) if ok else [],
        forbidden_actions=list(FORBIDDEN_ACTIONS),
        stop_conditions=stop_conditions,
        allowed_next_script=DEFAULT_ALLOWED_NEXT_SCRIPT if ok else None,
        forbidden_true_flags=forbidden_flags(payload),
        preflight_created_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat() if ok else None,
        reason=reason,
    )


def validate_instruction_packet_payload(
    payload: Mapping[str, Any],
    *,
    source_packet_basename: str | None = None,
    source_packet_sha256: str | None = None,
) -> ChromeLiveNoSendPreflightContract:
    packet_kind = payload.get("packet_kind")
    packet_result = payload.get("result")
    boundary_kind = payload.get("boundary_kind")
    boundary_result = payload.get("boundary_result")
    forbidden = forbidden_flags(payload)
    missing_true = sorted(key for key in REQUIRED_TRUE_FIELDS if not bool(payload.get(key, False)))
    false_violations = sorted(key for key in REQUIRED_FALSE_FIELDS if bool(payload.get(key, False)))

    if packet_kind != EXPECTED_PACKET_KIND:
        return _contract(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSUPPORTED_KIND,
            payload=payload,
            source_packet_basename=source_packet_basename,
            source_packet_sha256=source_packet_sha256,
            reason="Instruction packet kind is not chrome_uploader_live_instruction_packet_no_action.",
        )
    if forbidden:
        return _contract(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSAFE,
            payload=payload,
            source_packet_basename=source_packet_basename,
            source_packet_sha256=source_packet_sha256,
            reason="Instruction packet contains forbidden true safety flags.",
        )
    if (
        not bool(payload.get("ok", False))
        or packet_result != EXPECTED_PACKET_RESULT
        or payload.get("expected_browser") != EXPECTED_BROWSER
        or boundary_kind != EXPECTED_BOUNDARY_KIND
        or boundary_result != EXPECTED_BOUNDARY_RESULT
        or missing_true
        or false_violations
    ):
        reason = "Instruction packet is not ready for live no-send preflight contract generation."
        if missing_true:
            reason += " Missing true fields: " + ",".join(missing_true)
        if false_violations:
            reason += " False-field violations: " + ",".join(false_violations)
        return _contract(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_NOT_READY,
            payload=payload,
            source_packet_basename=source_packet_basename,
            source_packet_sha256=source_packet_sha256,
            reason=reason,
        )

    return _contract(
        ok=True,
        result=PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED,
        payload=payload,
        source_packet_basename=source_packet_basename,
        source_packet_sha256=source_packet_sha256,
        reason="Chrome live no-send preflight contract generated from validated instruction packet; no browser action was performed.",
    )


def load_and_validate_instruction_packet(path: Path | str) -> ChromeLiveNoSendPreflightContract:
    packet_path = Path(path).expanduser().resolve()
    if not packet_path.exists():
        return ChromeLiveNoSendPreflightContract(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_MISSING,
            schema_version=CONTRACT_SCHEMA_VERSION,
            contract_kind=CONTRACT_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_packet_basename=packet_path.name,
            source_packet_sha256=None,
            source_boundary_basename=None,
            source_ready_basename=None,
            source_consumed_basename=None,
            source_handoff_basename=None,
            source_acceptance_basename=None,
            packet_kind=None,
            packet_result=None,
            boundary_kind=None,
            boundary_result=None,
            preflight_contract_ready=False,
            no_send_verified=False,
            attachment_verified=False,
            safe_for_downstream_planning=False,
            packet_performs_browser_action=False,
            packet_performs_chatgpt_submit=False,
            packet_reads_conversation_text=False,
            browser_action_performed=False,
            chatgpt_submit_performed=False,
            send_allowed=False,
            raw_conversation_text_available=False,
            human_must_confirm_visible_chrome=True,
            human_must_verify_no_send=True,
            required_visible_state=[],
            permitted_future_actions=[],
            forbidden_actions=list(FORBIDDEN_ACTIONS),
            stop_conditions=["instruction_packet_missing"],
            allowed_next_script=None,
            forbidden_true_flags=[],
            preflight_created_utc=None,
            reason="Instruction packet JSON file is missing.",
        )
    try:
        payload = json.loads(packet_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ChromeLiveNoSendPreflightContract(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_INVALID_JSON,
            schema_version=CONTRACT_SCHEMA_VERSION,
            contract_kind=CONTRACT_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_packet_basename=packet_path.name,
            source_packet_sha256=sha256_file(packet_path),
            source_boundary_basename=None,
            source_ready_basename=None,
            source_consumed_basename=None,
            source_handoff_basename=None,
            source_acceptance_basename=None,
            packet_kind=None,
            packet_result=None,
            boundary_kind=None,
            boundary_result=None,
            preflight_contract_ready=False,
            no_send_verified=False,
            attachment_verified=False,
            safe_for_downstream_planning=False,
            packet_performs_browser_action=False,
            packet_performs_chatgpt_submit=False,
            packet_reads_conversation_text=False,
            browser_action_performed=False,
            chatgpt_submit_performed=False,
            send_allowed=False,
            raw_conversation_text_available=False,
            human_must_confirm_visible_chrome=True,
            human_must_verify_no_send=True,
            required_visible_state=[],
            permitted_future_actions=[],
            forbidden_actions=list(FORBIDDEN_ACTIONS),
            stop_conditions=["instruction_packet_invalid_json"],
            allowed_next_script=None,
            forbidden_true_flags=[],
            preflight_created_utc=None,
            reason=f"Instruction packet JSON is invalid: {exc}",
        )
    if not isinstance(payload, dict):
        payload = {}
    return validate_instruction_packet_payload(
        payload,
        source_packet_basename=packet_path.name,
        source_packet_sha256=sha256_file(packet_path),
    )


def write_preflight_contract(contract: ChromeLiveNoSendPreflightContract, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = contract.to_payload()
    payload["write_result"] = PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_WRITTEN if contract.ok else contract.result
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_preflight_contract_marker(contract: ChromeLiveNoSendPreflightContract, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Chrome live no-send preflight contract",
        "======================================",
        f"result:{contract.result}",
        f"ok:{str(contract.ok).lower()}",
        f"contract_kind:{contract.contract_kind}",
        f"expected_browser:{contract.expected_browser}",
        f"packet_kind:{contract.packet_kind or ''}",
        f"packet_result:{contract.packet_result or ''}",
        f"boundary_kind:{contract.boundary_kind or ''}",
        f"boundary_result:{contract.boundary_result or ''}",
        f"preflight_contract_ready:{str(contract.preflight_contract_ready).lower()}",
        f"no_send_verified:{str(contract.no_send_verified).lower()}",
        f"attachment_verified:{str(contract.attachment_verified).lower()}",
        f"safe_for_downstream_planning:{str(contract.safe_for_downstream_planning).lower()}",
        "packet_performs_browser_action:false",
        "packet_performs_chatgpt_submit:false",
        "packet_reads_conversation_text:false",
        "browser_action_performed:false",
        "chatgpt_submit_performed:false",
        "send_allowed:false",
        "raw_conversation_text_available:false",
        f"human_must_confirm_visible_chrome:{str(contract.human_must_confirm_visible_chrome).lower()}",
        f"human_must_verify_no_send:{str(contract.human_must_verify_no_send).lower()}",
        "selenium_used:false",
        "webdriver_used:false",
        "browser_dom_automation_used:false",
        "cloudflare_bypass_attempted:false",
        "captcha_bypass_attempted:false",
        "conversation_text_logged:false",
        "raw_conversation_text_logged:false",
        "random_page_click_performed:false",
        "",
        "Required visible state",
        "----------------------",
    ]
    lines.extend(f"- {item}" for item in contract.required_visible_state)
    lines.extend(["", "Permitted future actions", "------------------------"])
    lines.extend(f"- {item}" for item in contract.permitted_future_actions)
    lines.extend(["", "Stop conditions", "---------------"])
    lines.extend(f"- {item}" for item in contract.stop_conditions)
    lines.extend(["", f"allowed_next_script:{contract.allowed_next_script or ''}", f"forbidden_actions:{','.join(contract.forbidden_actions)}", f"reason:{contract.reason}"])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path