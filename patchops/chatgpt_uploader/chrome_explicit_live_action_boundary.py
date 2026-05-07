from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED = "PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED"
PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_WRITTEN = "PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_WRITTEN"
BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_MISSING = "BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_MISSING"
BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_INVALID_JSON = "BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_INVALID_JSON"
BLOCKED_LIVE_BOUNDARY_UNSUPPORTED_KIND = "BLOCKED_LIVE_BOUNDARY_UNSUPPORTED_KIND"
BLOCKED_LIVE_BOUNDARY_NOT_READY = "BLOCKED_LIVE_BOUNDARY_NOT_READY"
BLOCKED_LIVE_BOUNDARY_UNSAFE = "BLOCKED_LIVE_BOUNDARY_UNSAFE"
BLOCKED_LIVE_BOUNDARY_CONFIRMATION_REQUIRED = "BLOCKED_LIVE_BOUNDARY_CONFIRMATION_REQUIRED"

EXPECTED_BROWSER = "chrome"
EXPECTED_READY_CONTRACT_KIND = "chrome_uploader_downstream_ready_contract"
EXPECTED_READY_RESULT = "PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED"
BOUNDARY_SCHEMA_VERSION = "1"
BOUNDARY_KIND = "chrome_uploader_explicit_live_action_boundary"
REQUIRED_CONFIRMATION_TEXT = "PATCHOPS_CONFIRM_CHROME_LIVE_NO_SEND_ACTION"
DEFAULT_READY_CONTRACT_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_ready_contract.json"
DEFAULT_BOUNDARY_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_action_boundary.json"

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
    "safe_for_downstream_planning",
    "read_only_contract",
    "no_send_verified",
    "attachment_verified",
    "downstream_contract_accepted",
}
REQUIRED_FALSE_FIELDS = {
    "browser_action_performed",
    "chatgpt_submit_performed",
    "raw_conversation_text_available",
}
ALLOWED_WITH_CONFIRMATION = [
    "focus_existing_chrome_window",
    "open_file_picker_with_human_visible_target",
    "type_canonical_path_into_picker",
    "press_enter_in_picker",
    "verify_attachment_chip_no_send",
]
ALWAYS_FORBIDDEN = [
    "send_chatgpt_message",
    "read_conversation_text",
    "use_dom_automation",
    "use_webdriver",
    "bypass_cloudflare_or_captcha",
    "random_click",
    "open_hidden_browser",
]


@dataclass(frozen=True)
class ChromeExplicitLiveActionBoundary:
    ok: bool
    result: str
    schema_version: str
    boundary_kind: str
    expected_browser: str
    source_ready_basename: str | None
    source_ready_sha256: str | None
    source_consumed_basename: str | None
    source_consumed_sha256: str | None
    source_handoff_basename: str | None
    source_acceptance_basename: str | None
    ready_contract_kind: str | None
    ready_result: str | None
    consumed_result: str | None
    acceptance_result: str | None
    no_send_verified: bool
    attachment_verified: bool
    safe_for_downstream_planning: bool
    read_only_source_contract: bool
    confirmation_required: bool
    required_confirmation_text: str
    confirmation_supplied: bool
    boundary_confirmed: bool
    live_action_allowed: bool
    send_allowed: bool
    browser_action_performed: bool
    chatgpt_submit_performed: bool
    raw_conversation_text_available: bool
    forbidden_true_flags: list[str]
    allowed_with_confirmation: list[str]
    always_forbidden: list[str]
    boundary_created_utc: str | None
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


def _boundary(
    *,
    ok: bool,
    result: str,
    payload: Mapping[str, Any],
    source_ready_basename: str | None,
    source_ready_sha256: str | None,
    confirmation_text: str | None,
    reason: str,
) -> ChromeExplicitLiveActionBoundary:
    confirmation_supplied = bool(confirmation_text)
    boundary_confirmed = confirmation_text == REQUIRED_CONFIRMATION_TEXT
    return ChromeExplicitLiveActionBoundary(
        ok=bool(ok),
        result=result,
        schema_version=BOUNDARY_SCHEMA_VERSION,
        boundary_kind=BOUNDARY_KIND,
        expected_browser=EXPECTED_BROWSER,
        source_ready_basename=source_ready_basename,
        source_ready_sha256=source_ready_sha256,
        source_consumed_basename=payload.get("source_consumed_basename"),
        source_consumed_sha256=payload.get("source_consumed_sha256"),
        source_handoff_basename=payload.get("source_handoff_basename"),
        source_acceptance_basename=payload.get("source_acceptance_basename"),
        ready_contract_kind=payload.get("ready_contract_kind"),
        ready_result=payload.get("result"),
        consumed_result=payload.get("consumed_result"),
        acceptance_result=payload.get("acceptance_result"),
        no_send_verified=bool(payload.get("no_send_verified", False)),
        attachment_verified=bool(payload.get("attachment_verified", False)),
        safe_for_downstream_planning=bool(payload.get("safe_for_downstream_planning", False)),
        read_only_source_contract=bool(payload.get("read_only_contract", False)),
        confirmation_required=True,
        required_confirmation_text=REQUIRED_CONFIRMATION_TEXT,
        confirmation_supplied=confirmation_supplied,
        boundary_confirmed=boundary_confirmed if ok else False,
        live_action_allowed=bool(ok and boundary_confirmed),
        send_allowed=False,
        browser_action_performed=False,
        chatgpt_submit_performed=False,
        raw_conversation_text_available=False,
        forbidden_true_flags=forbidden_flags(payload),
        allowed_with_confirmation=list(ALLOWED_WITH_CONFIRMATION) if ok else [],
        always_forbidden=list(ALWAYS_FORBIDDEN),
        boundary_created_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat() if ok else None,
        reason=reason,
    )


def validate_ready_contract_payload(
    payload: Mapping[str, Any],
    *,
    source_ready_basename: str | None = None,
    source_ready_sha256: str | None = None,
    confirmation_text: str | None = None,
) -> ChromeExplicitLiveActionBoundary:
    ready_kind = payload.get("ready_contract_kind")
    ready_result = payload.get("result")
    forbidden = forbidden_flags(payload)
    missing_true = sorted(key for key in REQUIRED_TRUE_FIELDS if not bool(payload.get(key, False)))
    false_violations = sorted(key for key in REQUIRED_FALSE_FIELDS if bool(payload.get(key, False)))

    if ready_kind != EXPECTED_READY_CONTRACT_KIND:
        return _boundary(
            ok=False,
            result=BLOCKED_LIVE_BOUNDARY_UNSUPPORTED_KIND,
            payload=payload,
            source_ready_basename=source_ready_basename,
            source_ready_sha256=source_ready_sha256,
            confirmation_text=confirmation_text,
            reason="Ready contract kind is not chrome_uploader_downstream_ready_contract.",
        )
    if forbidden:
        return _boundary(
            ok=False,
            result=BLOCKED_LIVE_BOUNDARY_UNSAFE,
            payload=payload,
            source_ready_basename=source_ready_basename,
            source_ready_sha256=source_ready_sha256,
            confirmation_text=confirmation_text,
            reason="Ready contract contains forbidden true safety flags.",
        )
    if (
        not bool(payload.get("ok", False))
        or ready_result != EXPECTED_READY_RESULT
        or payload.get("expected_browser") != EXPECTED_BROWSER
        or missing_true
        or false_violations
    ):
        reason = "Ready contract is not accepted for live-action boundary planning."
        if missing_true:
            reason += " Missing true fields: " + ",".join(missing_true)
        if false_violations:
            reason += " False-field violations: " + ",".join(false_violations)
        return _boundary(
            ok=False,
            result=BLOCKED_LIVE_BOUNDARY_NOT_READY,
            payload=payload,
            source_ready_basename=source_ready_basename,
            source_ready_sha256=source_ready_sha256,
            confirmation_text=confirmation_text,
            reason=reason,
        )
    if confirmation_text != REQUIRED_CONFIRMATION_TEXT:
        return _boundary(
            ok=False,
            result=BLOCKED_LIVE_BOUNDARY_CONFIRMATION_REQUIRED,
            payload=payload,
            source_ready_basename=source_ready_basename,
            source_ready_sha256=source_ready_sha256,
            confirmation_text=confirmation_text,
            reason=f"Explicit live boundary confirmation is required: {REQUIRED_CONFIRMATION_TEXT}. No browser action was performed.",
        )

    return _boundary(
        ok=True,
        result=PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED,
        payload=payload,
        source_ready_basename=source_ready_basename,
        source_ready_sha256=source_ready_sha256,
        confirmation_text=confirmation_text,
        reason="Explicit live-action boundary is confirmed for future Chrome no-send actions only; this step performed no browser action.",
    )


def load_and_validate_ready_contract(path: Path | str, *, confirmation_text: str | None = None) -> ChromeExplicitLiveActionBoundary:
    ready_path = Path(path).expanduser().resolve()
    if not ready_path.exists():
        return ChromeExplicitLiveActionBoundary(
            ok=False,
            result=BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_MISSING,
            schema_version=BOUNDARY_SCHEMA_VERSION,
            boundary_kind=BOUNDARY_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_ready_basename=ready_path.name,
            source_ready_sha256=None,
            source_consumed_basename=None,
            source_consumed_sha256=None,
            source_handoff_basename=None,
            source_acceptance_basename=None,
            ready_contract_kind=None,
            ready_result=None,
            consumed_result=None,
            acceptance_result=None,
            no_send_verified=False,
            attachment_verified=False,
            safe_for_downstream_planning=False,
            read_only_source_contract=False,
            confirmation_required=True,
            required_confirmation_text=REQUIRED_CONFIRMATION_TEXT,
            confirmation_supplied=bool(confirmation_text),
            boundary_confirmed=False,
            live_action_allowed=False,
            send_allowed=False,
            browser_action_performed=False,
            chatgpt_submit_performed=False,
            raw_conversation_text_available=False,
            forbidden_true_flags=[],
            allowed_with_confirmation=[],
            always_forbidden=list(ALWAYS_FORBIDDEN),
            boundary_created_utc=None,
            reason="Ready contract file is missing.",
        )
    try:
        payload = json.loads(ready_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ChromeExplicitLiveActionBoundary(
            ok=False,
            result=BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_INVALID_JSON,
            schema_version=BOUNDARY_SCHEMA_VERSION,
            boundary_kind=BOUNDARY_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_ready_basename=ready_path.name,
            source_ready_sha256=sha256_file(ready_path),
            source_consumed_basename=None,
            source_consumed_sha256=None,
            source_handoff_basename=None,
            source_acceptance_basename=None,
            ready_contract_kind=None,
            ready_result=None,
            consumed_result=None,
            acceptance_result=None,
            no_send_verified=False,
            attachment_verified=False,
            safe_for_downstream_planning=False,
            read_only_source_contract=False,
            confirmation_required=True,
            required_confirmation_text=REQUIRED_CONFIRMATION_TEXT,
            confirmation_supplied=bool(confirmation_text),
            boundary_confirmed=False,
            live_action_allowed=False,
            send_allowed=False,
            browser_action_performed=False,
            chatgpt_submit_performed=False,
            raw_conversation_text_available=False,
            forbidden_true_flags=[],
            allowed_with_confirmation=[],
            always_forbidden=list(ALWAYS_FORBIDDEN),
            boundary_created_utc=None,
            reason=f"Ready contract JSON is invalid: {exc}",
        )
    if not isinstance(payload, dict):
        payload = {}
    return validate_ready_contract_payload(
        payload,
        source_ready_basename=ready_path.name,
        source_ready_sha256=sha256_file(ready_path),
        confirmation_text=confirmation_text,
    )


def write_live_action_boundary(boundary: ChromeExplicitLiveActionBoundary, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = boundary.to_payload()
    payload["write_result"] = PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_WRITTEN if boundary.ok else boundary.result
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_live_action_boundary_marker(boundary: ChromeExplicitLiveActionBoundary, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Chrome explicit live-action boundary",
        "====================================",
        f"result:{boundary.result}",
        f"ok:{str(boundary.ok).lower()}",
        f"boundary_kind:{boundary.boundary_kind}",
        f"expected_browser:{boundary.expected_browser}",
        f"source_ready:{boundary.source_ready_basename or ''}",
        f"source_ready_sha256:{boundary.source_ready_sha256 or ''}",
        f"ready_contract_kind:{boundary.ready_contract_kind or ''}",
        f"ready_result:{boundary.ready_result or ''}",
        f"confirmation_required:{str(boundary.confirmation_required).lower()}",
        f"required_confirmation_text:{boundary.required_confirmation_text}",
        f"boundary_confirmed:{str(boundary.boundary_confirmed).lower()}",
        f"live_action_allowed:{str(boundary.live_action_allowed).lower()}",
        "send_allowed:false",
        "browser_action_performed:false",
        "chatgpt_submit_performed:false",
        "raw_conversation_text_available:false",
        "selenium_used:false",
        "webdriver_used:false",
        "browser_dom_automation_used:false",
        "conversation_text_logged:false",
        "raw_conversation_text_logged:false",
        f"allowed_with_confirmation:{','.join(boundary.allowed_with_confirmation)}",
        f"always_forbidden:{','.join(boundary.always_forbidden)}",
        f"reason:{boundary.reason}",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path