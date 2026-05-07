from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED = "PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED"
PASS_CHROME_DOWNSTREAM_READY_CONTRACT_WRITTEN = "PASS_CHROME_DOWNSTREAM_READY_CONTRACT_WRITTEN"
BLOCKED_DOWNSTREAM_READY_CONSUMED_MISSING = "BLOCKED_DOWNSTREAM_READY_CONSUMED_MISSING"
BLOCKED_DOWNSTREAM_READY_CONSUMED_INVALID_JSON = "BLOCKED_DOWNSTREAM_READY_CONSUMED_INVALID_JSON"
BLOCKED_DOWNSTREAM_READY_UNSUPPORTED_KIND = "BLOCKED_DOWNSTREAM_READY_UNSUPPORTED_KIND"
BLOCKED_DOWNSTREAM_READY_NOT_ACCEPTED = "BLOCKED_DOWNSTREAM_READY_NOT_ACCEPTED"
BLOCKED_DOWNSTREAM_READY_UNSAFE = "BLOCKED_DOWNSTREAM_READY_UNSAFE"

EXPECTED_BROWSER = "chrome"
EXPECTED_CONSUMED_KIND = "chrome_uploader_acceptance_consumed_no_browser"
EXPECTED_CONSUMED_RESULT = "PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER"
READY_CONTRACT_SCHEMA_VERSION = "1"
READY_CONTRACT_KIND = "chrome_uploader_downstream_ready_contract"
DEFAULT_CONSUMED_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_acceptance_consumed.json"
DEFAULT_READY_CONTRACT_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_ready_contract.json"

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
    "browser_opened_by_reader",
    "browser_action_performed",
    "live_browser_used",
    "live_browser_used_by_reader",
    "raw_conversation_text_available",
}
REQUIRED_TRUE_FIELDS = {
    "no_browser_action_performed",
    "no_send_verified",
    "attachment_verified",
    "downstream_contract_accepted",
    "downstream_contract_no_send_only",
}

ALLOWED_NEXT_ACTIONS = [
    "read_acceptance_summary",
    "plan_downstream_orchestration",
    "prepare_explicit_live_test_instructions",
    "request_human_confirmation_before_browser_action",
]
FORBIDDEN_NEXT_ACTIONS = [
    "open_browser_without_explicit_live_confirmation",
    "send_chatgpt_message",
    "read_conversation_text",
    "use_dom_automation",
    "use_webdriver",
    "bypass_cloudflare_or_captcha",
    "random_click",
]


@dataclass(frozen=True)
class ChromeDownstreamReadyContract:
    ok: bool
    result: str
    schema_version: str
    ready_contract_kind: str
    expected_browser: str
    source_consumed_basename: str | None
    source_consumed_sha256: str | None
    source_handoff_basename: str | None
    source_handoff_sha256: str | None
    source_acceptance_basename: str | None
    source_acceptance_sha256: str | None
    consumed_kind: str | None
    consumed_result: str | None
    acceptance_result: str | None
    acceptance_ok: bool
    attempt_count: int
    min_attempts: int
    pass_count: int
    min_passes: int
    no_send_verified: bool
    attachment_verified: bool
    downstream_contract_accepted: bool
    safe_for_downstream_planning: bool
    read_only_contract: bool
    browser_action_performed: bool
    chatgpt_submit_performed: bool
    raw_conversation_text_available: bool
    forbidden_true_flags: list[str]
    allowed_next_actions: list[str]
    forbidden_next_actions: list[str]
    ready_created_utc: str | None
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


def _next_contract(payload: Mapping[str, Any]) -> dict[str, Any]:
    value = payload.get("next_step_contract")
    return dict(value) if isinstance(value, dict) else {}


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
    contract = _next_contract(payload)
    for key in ("browser_action_performed", "chatgpt_submit_performed", "raw_conversation_text_available"):
        if bool(contract.get(key, False)):
            found.add(key)
    return sorted(found)


def _contract(
    *,
    ok: bool,
    result: str,
    payload: Mapping[str, Any],
    source_consumed_basename: str | None,
    source_consumed_sha256: str | None,
    reason: str,
) -> ChromeDownstreamReadyContract:
    next_contract = _next_contract(payload)
    forbidden = forbidden_flags(payload)
    return ChromeDownstreamReadyContract(
        ok=bool(ok),
        result=result,
        schema_version=READY_CONTRACT_SCHEMA_VERSION,
        ready_contract_kind=READY_CONTRACT_KIND,
        expected_browser=EXPECTED_BROWSER,
        source_consumed_basename=source_consumed_basename,
        source_consumed_sha256=source_consumed_sha256,
        source_handoff_basename=payload.get("source_handoff_basename"),
        source_handoff_sha256=payload.get("source_handoff_sha256"),
        source_acceptance_basename=payload.get("source_acceptance_basename"),
        source_acceptance_sha256=payload.get("source_acceptance_sha256"),
        consumed_kind=payload.get("consumed_kind"),
        consumed_result=payload.get("result"),
        acceptance_result=payload.get("acceptance_result"),
        acceptance_ok=bool(payload.get("acceptance_ok", False)),
        attempt_count=int(payload.get("attempt_count", 0) or 0),
        min_attempts=int(payload.get("min_attempts", 0) or 0),
        pass_count=int(payload.get("pass_count", 0) or 0),
        min_passes=int(payload.get("min_passes", 0) or 0),
        no_send_verified=bool(payload.get("no_send_verified", False)),
        attachment_verified=bool(payload.get("attachment_verified", False)),
        downstream_contract_accepted=bool(payload.get("downstream_contract_accepted", False)),
        safe_for_downstream_planning=bool(ok and next_contract.get("safe_for_downstream_planning", False)),
        read_only_contract=True,
        browser_action_performed=False,
        chatgpt_submit_performed=False,
        raw_conversation_text_available=False,
        forbidden_true_flags=forbidden,
        allowed_next_actions=list(ALLOWED_NEXT_ACTIONS) if ok else [],
        forbidden_next_actions=list(FORBIDDEN_NEXT_ACTIONS),
        ready_created_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat() if ok else None,
        reason=reason,
    )


def validate_consumed_payload(
    payload: Mapping[str, Any],
    *,
    source_consumed_basename: str | None = None,
    source_consumed_sha256: str | None = None,
) -> ChromeDownstreamReadyContract:
    consumed_kind = payload.get("consumed_kind")
    consumed_result = payload.get("result")
    next_contract = _next_contract(payload)
    forbidden = forbidden_flags(payload)
    missing_true = sorted(key for key in REQUIRED_TRUE_FIELDS if not bool(payload.get(key, False)))

    if consumed_kind != EXPECTED_CONSUMED_KIND:
        return _contract(
            ok=False,
            result=BLOCKED_DOWNSTREAM_READY_UNSUPPORTED_KIND,
            payload=payload,
            source_consumed_basename=source_consumed_basename,
            source_consumed_sha256=source_consumed_sha256,
            reason="Consumed handoff kind is not chrome_uploader_acceptance_consumed_no_browser.",
        )
    if forbidden:
        return _contract(
            ok=False,
            result=BLOCKED_DOWNSTREAM_READY_UNSAFE,
            payload=payload,
            source_consumed_basename=source_consumed_basename,
            source_consumed_sha256=source_consumed_sha256,
            reason="Consumed handoff has forbidden true safety flags or raw conversation availability.",
        )
    if (
        not bool(payload.get("ok", False))
        or consumed_result != EXPECTED_CONSUMED_RESULT
        or payload.get("expected_browser") != EXPECTED_BROWSER
        or not bool(payload.get("no_send_verified", False))
        or not bool(payload.get("attachment_verified", False))
        or not bool(payload.get("downstream_contract_accepted", False))
        or not bool(payload.get("downstream_contract_no_send_only", False))
        or not bool(payload.get("no_browser_action_performed", False))
        or bool(payload.get("browser_opened_by_reader", False))
        or bool(payload.get("chatgpt_submit_performed", False))
        or bool(payload.get("raw_conversation_text_available", False))
        or not bool(next_contract.get("safe_for_downstream_planning", False))
        or bool(next_contract.get("browser_action_performed", False))
        or bool(next_contract.get("chatgpt_submit_performed", False))
        or missing_true
    ):
        reason = "Consumed handoff is not accepted, not read-only, or missing downstream readiness fields."
        if missing_true:
            reason += " Missing: " + ",".join(missing_true)
        return _contract(
            ok=False,
            result=BLOCKED_DOWNSTREAM_READY_NOT_ACCEPTED,
            payload=payload,
            source_consumed_basename=source_consumed_basename,
            source_consumed_sha256=source_consumed_sha256,
            reason=reason,
        )
    if int(payload.get("attempt_count", 0) or 0) < int(payload.get("min_attempts", 0) or 0):
        return _contract(
            ok=False,
            result=BLOCKED_DOWNSTREAM_READY_NOT_ACCEPTED,
            payload=payload,
            source_consumed_basename=source_consumed_basename,
            source_consumed_sha256=source_consumed_sha256,
            reason="Consumed handoff attempt count is below the minimum threshold.",
        )
    if int(payload.get("pass_count", 0) or 0) < int(payload.get("min_passes", 0) or 0):
        return _contract(
            ok=False,
            result=BLOCKED_DOWNSTREAM_READY_NOT_ACCEPTED,
            payload=payload,
            source_consumed_basename=source_consumed_basename,
            source_consumed_sha256=source_consumed_sha256,
            reason="Consumed handoff pass count is below the minimum threshold.",
        )

    return _contract(
        ok=True,
        result=PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED,
        payload=payload,
        source_consumed_basename=source_consumed_basename,
        source_consumed_sha256=source_consumed_sha256,
        reason="Chrome no-send consumed handoff is ready for downstream planning; no browser action was performed.",
    )


def load_and_validate_consumed(path: Path | str) -> ChromeDownstreamReadyContract:
    consumed_path = Path(path).expanduser().resolve()
    if not consumed_path.exists():
        return ChromeDownstreamReadyContract(
            ok=False,
            result=BLOCKED_DOWNSTREAM_READY_CONSUMED_MISSING,
            schema_version=READY_CONTRACT_SCHEMA_VERSION,
            ready_contract_kind=READY_CONTRACT_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_consumed_basename=consumed_path.name,
            source_consumed_sha256=None,
            source_handoff_basename=None,
            source_handoff_sha256=None,
            source_acceptance_basename=None,
            source_acceptance_sha256=None,
            consumed_kind=None,
            consumed_result=None,
            acceptance_result=None,
            acceptance_ok=False,
            attempt_count=0,
            min_attempts=0,
            pass_count=0,
            min_passes=0,
            no_send_verified=False,
            attachment_verified=False,
            downstream_contract_accepted=False,
            safe_for_downstream_planning=False,
            read_only_contract=True,
            browser_action_performed=False,
            chatgpt_submit_performed=False,
            raw_conversation_text_available=False,
            forbidden_true_flags=[],
            allowed_next_actions=[],
            forbidden_next_actions=list(FORBIDDEN_NEXT_ACTIONS),
            ready_created_utc=None,
            reason="Consumed handoff file is missing.",
        )
    try:
        payload = json.loads(consumed_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ChromeDownstreamReadyContract(
            ok=False,
            result=BLOCKED_DOWNSTREAM_READY_CONSUMED_INVALID_JSON,
            schema_version=READY_CONTRACT_SCHEMA_VERSION,
            ready_contract_kind=READY_CONTRACT_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_consumed_basename=consumed_path.name,
            source_consumed_sha256=sha256_file(consumed_path),
            source_handoff_basename=None,
            source_handoff_sha256=None,
            source_acceptance_basename=None,
            source_acceptance_sha256=None,
            consumed_kind=None,
            consumed_result=None,
            acceptance_result=None,
            acceptance_ok=False,
            attempt_count=0,
            min_attempts=0,
            pass_count=0,
            min_passes=0,
            no_send_verified=False,
            attachment_verified=False,
            downstream_contract_accepted=False,
            safe_for_downstream_planning=False,
            read_only_contract=True,
            browser_action_performed=False,
            chatgpt_submit_performed=False,
            raw_conversation_text_available=False,
            forbidden_true_flags=[],
            allowed_next_actions=[],
            forbidden_next_actions=list(FORBIDDEN_NEXT_ACTIONS),
            ready_created_utc=None,
            reason=f"Consumed handoff JSON is invalid: {exc}",
        )
    if not isinstance(payload, dict):
        payload = {}
    return validate_consumed_payload(
        payload,
        source_consumed_basename=consumed_path.name,
        source_consumed_sha256=sha256_file(consumed_path),
    )


def write_ready_contract(contract: ChromeDownstreamReadyContract, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = contract.to_payload()
    payload["write_result"] = PASS_CHROME_DOWNSTREAM_READY_CONTRACT_WRITTEN if contract.ok else contract.result
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_ready_contract_marker(contract: ChromeDownstreamReadyContract, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Chrome downstream ready contract",
        "=================================",
        f"result:{contract.result}",
        f"ok:{str(contract.ok).lower()}",
        f"ready_contract_kind:{contract.ready_contract_kind}",
        f"expected_browser:{contract.expected_browser}",
        f"source_consumed:{contract.source_consumed_basename or ''}",
        f"source_consumed_sha256:{contract.source_consumed_sha256 or ''}",
        f"consumed_kind:{contract.consumed_kind or ''}",
        f"consumed_result:{contract.consumed_result or ''}",
        f"acceptance_result:{contract.acceptance_result or ''}",
        f"no_send_verified:{str(contract.no_send_verified).lower()}",
        f"attachment_verified:{str(contract.attachment_verified).lower()}",
        f"safe_for_downstream_planning:{str(contract.safe_for_downstream_planning).lower()}",
        "read_only_contract:true",
        "browser_action_performed:false",
        "chatgpt_submit_performed:false",
        "raw_conversation_text_available:false",
        "selenium_used:false",
        "webdriver_used:false",
        "browser_dom_automation_used:false",
        "conversation_text_logged:false",
        "raw_conversation_text_logged:false",
        f"allowed_next_actions:{','.join(contract.allowed_next_actions)}",
        f"forbidden_next_actions:{','.join(contract.forbidden_next_actions)}",
        f"reason:{contract.reason}",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path