from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER = "PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER"
PASS_CHROME_ACCEPTANCE_HANDOFF_READER_WRITTEN = "PASS_CHROME_ACCEPTANCE_HANDOFF_READER_WRITTEN"
BLOCKED_HANDOFF_READER_MISSING = "BLOCKED_HANDOFF_READER_MISSING"
BLOCKED_HANDOFF_READER_INVALID_JSON = "BLOCKED_HANDOFF_READER_INVALID_JSON"
BLOCKED_HANDOFF_READER_UNSUPPORTED_KIND = "BLOCKED_HANDOFF_READER_UNSUPPORTED_KIND"
BLOCKED_HANDOFF_READER_NOT_ACCEPTED = "BLOCKED_HANDOFF_READER_NOT_ACCEPTED"
BLOCKED_HANDOFF_READER_UNSAFE = "BLOCKED_HANDOFF_READER_UNSAFE"

EXPECTED_BROWSER = "chrome"
EXPECTED_HANDOFF_KIND = "chrome_uploader_acceptance_no_send"
EXPECTED_ACCEPTANCE_RESULT = "PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND"
DEFAULT_HANDOFF_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_acceptance.json"
DEFAULT_CONSUMED_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_acceptance_consumed.json"
CONSUMED_SCHEMA_VERSION = "1"
CONSUMED_KIND = "chrome_uploader_acceptance_consumed_no_browser"
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
    "live_browser_used_by_reader",
}
REQUIRED_TRUE_FIELDS = {
    "no_send_verified",
    "attachment_verified",
    "chrome_executable_found",
    "chrome_target_ready",
    "canonical_report_found",
    "picker_opened",
    "exact_path_written",
    "file_upload_attempted",
}


@dataclass(frozen=True)
class ChromeAcceptanceHandoffReaderResult:
    ok: bool
    result: str
    schema_version: str
    consumed_kind: str
    expected_browser: str
    source_handoff_basename: str | None
    source_handoff_sha256: str | None
    source_acceptance_basename: str | None
    source_acceptance_sha256: str | None
    handoff_kind: str | None
    acceptance_result: str | None
    acceptance_ok: bool
    attempt_count: int
    min_attempts: int
    pass_count: int
    min_passes: int
    no_send_verified: bool
    attachment_verified: bool
    downstream_contract_accepted: bool
    downstream_contract_consumer: str | None
    downstream_contract_no_send_only: bool
    raw_conversation_text_available: bool
    browser_opened_by_reader: bool
    no_browser_action_performed: bool
    chatgpt_submit_performed: bool
    forbidden_true_flags: list[str]
    consumed_created_utc: str | None
    next_step_contract: dict[str, Any]
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


def _contract(payload: Mapping[str, Any]) -> dict[str, Any]:
    value = payload.get("downstream_contract")
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
    contract = _contract(payload)
    if bool(contract.get("raw_conversation_text_available", False)):
        found.add("raw_conversation_text_available")
    if bool(contract.get("conversation_text_logged", False)):
        found.add("conversation_text_logged")
    return sorted(found)


def _next_step_contract(*, accepted: bool, reason: str) -> dict[str, Any]:
    return {
        "contract": CONSUMED_KIND,
        "accepted": bool(accepted),
        "browser_lane": EXPECTED_BROWSER,
        "read_only_consumer": True,
        "browser_action_performed": False,
        "chatgpt_submit_performed": False,
        "no_send_verified": bool(accepted),
        "raw_conversation_text_available": False,
        "safe_for_downstream_planning": bool(accepted),
        "next_step_hint": "downstream orchestration may plan from accepted Chrome no-send uploader readiness without opening a browser",
        "reason": reason,
    }


def _reader_result(
    *,
    ok: bool,
    result: str,
    payload: Mapping[str, Any],
    source_handoff_basename: str | None,
    source_handoff_sha256: str | None,
    reason: str,
) -> ChromeAcceptanceHandoffReaderResult:
    contract = _contract(payload)
    forbidden = forbidden_flags(payload)
    return ChromeAcceptanceHandoffReaderResult(
        ok=bool(ok),
        result=result,
        schema_version=CONSUMED_SCHEMA_VERSION,
        consumed_kind=CONSUMED_KIND,
        expected_browser=EXPECTED_BROWSER,
        source_handoff_basename=source_handoff_basename,
        source_handoff_sha256=source_handoff_sha256,
        source_acceptance_basename=payload.get("source_acceptance_basename"),
        source_acceptance_sha256=payload.get("source_acceptance_sha256"),
        handoff_kind=payload.get("handoff_kind"),
        acceptance_result=payload.get("acceptance_result"),
        acceptance_ok=bool(payload.get("acceptance_ok", False)),
        attempt_count=int(payload.get("attempt_count", 0) or 0),
        min_attempts=int(payload.get("min_attempts", 0) or 0),
        pass_count=int(payload.get("pass_count", 0) or 0),
        min_passes=int(payload.get("min_passes", 0) or 0),
        no_send_verified=bool(payload.get("no_send_verified", False)),
        attachment_verified=bool(payload.get("attachment_verified", False)),
        downstream_contract_accepted=bool(contract.get("accepted", False)),
        downstream_contract_consumer=contract.get("consumer"),
        downstream_contract_no_send_only=bool(contract.get("no_send_only", False)),
        raw_conversation_text_available=bool(contract.get("raw_conversation_text_available", False)),
        browser_opened_by_reader=False,
        no_browser_action_performed=True,
        chatgpt_submit_performed=_bool(payload, "chatgpt_submit_performed"),
        forbidden_true_flags=forbidden,
        consumed_created_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat() if ok else None,
        next_step_contract=_next_step_contract(accepted=ok, reason=reason),
        reason=reason,
    )


def validate_handoff_payload(
    payload: Mapping[str, Any],
    *,
    source_handoff_basename: str | None = None,
    source_handoff_sha256: str | None = None,
) -> ChromeAcceptanceHandoffReaderResult:
    handoff_kind = payload.get("handoff_kind")
    acceptance_result = payload.get("acceptance_result")
    contract = _contract(payload)
    forbidden = forbidden_flags(payload)
    missing_true = sorted(key for key in REQUIRED_TRUE_FIELDS if not bool(payload.get(key, False)))

    if handoff_kind != EXPECTED_HANDOFF_KIND:
        return _reader_result(
            ok=False,
            result=BLOCKED_HANDOFF_READER_UNSUPPORTED_KIND,
            payload=payload,
            source_handoff_basename=source_handoff_basename,
            source_handoff_sha256=source_handoff_sha256,
            reason="Handoff kind is not chrome_uploader_acceptance_no_send.",
        )
    if forbidden:
        return _reader_result(
            ok=False,
            result=BLOCKED_HANDOFF_READER_UNSAFE,
            payload=payload,
            source_handoff_basename=source_handoff_basename,
            source_handoff_sha256=source_handoff_sha256,
            reason="Handoff contains forbidden true safety flags or raw conversation availability.",
        )
    if _bool(payload, "chatgpt_submit_performed"):
        return _reader_result(
            ok=False,
            result=BLOCKED_HANDOFF_READER_UNSAFE,
            payload=payload,
            source_handoff_basename=source_handoff_basename,
            source_handoff_sha256=source_handoff_sha256,
            reason="Handoff indicates ChatGPT submit; reader only accepts no-send handoffs.",
        )
    if (
        not bool(payload.get("ok", False))
        or acceptance_result != EXPECTED_ACCEPTANCE_RESULT
        or not bool(payload.get("acceptance_ok", False))
        or not bool(payload.get("no_send_verified", False))
        or not bool(payload.get("attachment_verified", False))
        or not bool(contract.get("accepted", False))
        or not bool(contract.get("no_send_only", False))
        or bool(contract.get("raw_conversation_text_available", False))
        or missing_true
    ):
        reason = "Handoff is not accepted or is missing no-send readiness fields."
        if missing_true:
            reason += " Missing: " + ",".join(missing_true)
        return _reader_result(
            ok=False,
            result=BLOCKED_HANDOFF_READER_NOT_ACCEPTED,
            payload=payload,
            source_handoff_basename=source_handoff_basename,
            source_handoff_sha256=source_handoff_sha256,
            reason=reason,
        )
    if int(payload.get("attempt_count", 0) or 0) < int(payload.get("min_attempts", 0) or 0):
        return _reader_result(
            ok=False,
            result=BLOCKED_HANDOFF_READER_NOT_ACCEPTED,
            payload=payload,
            source_handoff_basename=source_handoff_basename,
            source_handoff_sha256=source_handoff_sha256,
            reason="Handoff attempt count is below its minimum threshold.",
        )
    if int(payload.get("pass_count", 0) or 0) < int(payload.get("min_passes", 0) or 0):
        return _reader_result(
            ok=False,
            result=BLOCKED_HANDOFF_READER_NOT_ACCEPTED,
            payload=payload,
            source_handoff_basename=source_handoff_basename,
            source_handoff_sha256=source_handoff_sha256,
            reason="Handoff pass count is below its minimum threshold.",
        )

    return _reader_result(
        ok=True,
        result=PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER,
        payload=payload,
        source_handoff_basename=source_handoff_basename,
        source_handoff_sha256=source_handoff_sha256,
        reason="Chrome no-send acceptance handoff was consumed read-only with no browser action.",
    )


def load_and_validate_handoff(path: Path | str) -> ChromeAcceptanceHandoffReaderResult:
    handoff_path = Path(path).expanduser().resolve()
    if not handoff_path.exists():
        return ChromeAcceptanceHandoffReaderResult(
            ok=False,
            result=BLOCKED_HANDOFF_READER_MISSING,
            schema_version=CONSUMED_SCHEMA_VERSION,
            consumed_kind=CONSUMED_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_handoff_basename=handoff_path.name,
            source_handoff_sha256=None,
            source_acceptance_basename=None,
            source_acceptance_sha256=None,
            handoff_kind=None,
            acceptance_result=None,
            acceptance_ok=False,
            attempt_count=0,
            min_attempts=0,
            pass_count=0,
            min_passes=0,
            no_send_verified=False,
            attachment_verified=False,
            downstream_contract_accepted=False,
            downstream_contract_consumer=None,
            downstream_contract_no_send_only=False,
            raw_conversation_text_available=False,
            browser_opened_by_reader=False,
            no_browser_action_performed=True,
            chatgpt_submit_performed=False,
            forbidden_true_flags=[],
            consumed_created_utc=None,
            next_step_contract=_next_step_contract(accepted=False, reason="Handoff file is missing."),
            reason="Handoff file is missing.",
        )
    try:
        payload = json.loads(handoff_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ChromeAcceptanceHandoffReaderResult(
            ok=False,
            result=BLOCKED_HANDOFF_READER_INVALID_JSON,
            schema_version=CONSUMED_SCHEMA_VERSION,
            consumed_kind=CONSUMED_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_handoff_basename=handoff_path.name,
            source_handoff_sha256=sha256_file(handoff_path),
            source_acceptance_basename=None,
            source_acceptance_sha256=None,
            handoff_kind=None,
            acceptance_result=None,
            acceptance_ok=False,
            attempt_count=0,
            min_attempts=0,
            pass_count=0,
            min_passes=0,
            no_send_verified=False,
            attachment_verified=False,
            downstream_contract_accepted=False,
            downstream_contract_consumer=None,
            downstream_contract_no_send_only=False,
            raw_conversation_text_available=False,
            browser_opened_by_reader=False,
            no_browser_action_performed=True,
            chatgpt_submit_performed=False,
            forbidden_true_flags=[],
            consumed_created_utc=None,
            next_step_contract=_next_step_contract(accepted=False, reason=f"Handoff JSON is invalid: {exc}"),
            reason=f"Handoff JSON is invalid: {exc}",
        )
    if not isinstance(payload, dict):
        payload = {}
    return validate_handoff_payload(
        payload,
        source_handoff_basename=handoff_path.name,
        source_handoff_sha256=sha256_file(handoff_path),
    )


def write_consumed_handoff(result: ChromeAcceptanceHandoffReaderResult, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = result.to_payload()
    payload["write_result"] = PASS_CHROME_ACCEPTANCE_HANDOFF_READER_WRITTEN if result.ok else result.result
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_consumed_handoff_marker(result: ChromeAcceptanceHandoffReaderResult, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Chrome acceptance handoff reader",
        "================================",
        f"result:{result.result}",
        f"ok:{str(result.ok).lower()}",
        f"consumed_kind:{result.consumed_kind}",
        f"handoff_kind:{result.handoff_kind or ''}",
        f"expected_browser:{result.expected_browser}",
        f"source_handoff:{result.source_handoff_basename or ''}",
        f"source_handoff_sha256:{result.source_handoff_sha256 or ''}",
        f"acceptance_result:{result.acceptance_result or ''}",
        f"attempt_count:{result.attempt_count}",
        f"pass_count:{result.pass_count}",
        f"no_send_verified:{str(result.no_send_verified).lower()}",
        f"attachment_verified:{str(result.attachment_verified).lower()}",
        f"downstream_contract_accepted:{str(result.downstream_contract_accepted).lower()}",
        "browser_opened_by_reader:false",
        "no_browser_action_performed:true",
        "chatgpt_submit_performed:false",
        "selenium_used:false",
        "webdriver_used:false",
        "browser_dom_automation_used:false",
        "conversation_text_logged:false",
        "raw_conversation_text_logged:false",
        f"reason:{result.reason}",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path