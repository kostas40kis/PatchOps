from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PASS_CHROME_ACCEPTANCE_HANDOFF_WRITTEN = "PASS_CHROME_ACCEPTANCE_HANDOFF_WRITTEN"
PASS_CHROME_ACCEPTANCE_HANDOFF_VALIDATED = "PASS_CHROME_ACCEPTANCE_HANDOFF_VALIDATED"
BLOCKED_ACCEPTANCE_HANDOFF_MISSING = "BLOCKED_ACCEPTANCE_HANDOFF_MISSING"
BLOCKED_ACCEPTANCE_HANDOFF_INVALID_JSON = "BLOCKED_ACCEPTANCE_HANDOFF_INVALID_JSON"
BLOCKED_ACCEPTANCE_NOT_PASSED = "BLOCKED_ACCEPTANCE_NOT_PASSED"
BLOCKED_ACCEPTANCE_HANDOFF_UNSAFE = "BLOCKED_ACCEPTANCE_HANDOFF_UNSAFE"

EXPECTED_BROWSER = "chrome"
EXPECTED_ACCEPTANCE_RESULT = "PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND"
HANDOFF_SCHEMA_VERSION = "1"
HANDOFF_KIND = "chrome_uploader_acceptance_no_send"
DEFAULT_HANDOFF_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_acceptance.json"
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
REQUIRED_TRUE_FIELDS = {
    "chrome_executable_found",
    "chrome_target_ready",
    "canonical_report_found",
    "picker_opened",
    "exact_path_written",
    "file_upload_attempted",
    "attachment_verified",
}


@dataclass(frozen=True)
class ChromeAcceptanceHandoff:
    ok: bool
    result: str
    schema_version: str
    handoff_kind: str
    expected_browser: str
    source_acceptance_basename: str | None
    source_acceptance_sha256: str | None
    acceptance_result: str | None
    acceptance_ok: bool
    attempt_count: int
    min_attempts: int
    pass_count: int
    min_passes: int
    failed_attempt_count: int
    no_send_verified: bool
    chrome_executable_found: bool
    chrome_target_ready: bool
    canonical_report_found: bool
    picker_opened: bool
    exact_path_written: bool
    file_upload_attempted: bool
    attachment_verified: bool
    chatgpt_submit_performed: bool
    forbidden_true_flags: list[str]
    handoff_created_utc: str | None
    downstream_contract: dict[str, Any]
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
    for attempt in payload.get("attempts", []) if isinstance(payload.get("attempts"), list) else []:
        if isinstance(attempt, dict):
            for item in attempt.get("forbidden_true_flags", []) or []:
                if item:
                    found.add(str(item))
            for key in FORBIDDEN_TRUE_FLAGS:
                if bool(attempt.get(key, False)):
                    found.add(key)
    return sorted(found)


def _contract_payload(*, accepted: bool, reason: str) -> dict[str, Any]:
    return {
        "contract": HANDOFF_KIND,
        "consumer": "patchops_downstream_orchestrator",
        "accepted": bool(accepted),
        "browser_lane": EXPECTED_BROWSER,
        "no_send_only": True,
        "requires_human_supervision_for_live_browser": True,
        "raw_conversation_text_available": False,
        "conversation_text_logged": False,
        "next_step_hint": "downstream components may consume this handoff as proof that Chrome uploader reached accepted no-send readiness",
        "reason": reason,
    }


def validate_acceptance_payload(
    payload: Mapping[str, Any],
    *,
    source_acceptance_basename: str | None = None,
    source_acceptance_sha256: str | None = None,
) -> ChromeAcceptanceHandoff:
    acceptance_result = payload.get("result")
    acceptance_ok = bool(payload.get("ok", False))
    attempt_count = int(payload.get("attempt_count", 0) or 0)
    min_attempts = int(payload.get("min_attempts", 0) or 0)
    pass_count = int(payload.get("pass_count", 0) or 0)
    min_passes = int(payload.get("min_passes", 0) or 0)
    failed_attempt_count = int(payload.get("failed_attempt_count", 0) or 0)
    forbidden = forbidden_flags(payload)
    chatgpt_submit_performed = _bool(payload, "chatgpt_submit_performed") or bool(payload.get("chatgpt_submit_detected", False))
    field_values = {key: _bool(payload, key) for key in REQUIRED_TRUE_FIELDS}
    missing_true = sorted(key for key, value in field_values.items() if not value)

    reason = "Chrome acceptance handoff validated."
    result = PASS_CHROME_ACCEPTANCE_HANDOFF_VALIDATED
    ok = True

    if acceptance_result != EXPECTED_ACCEPTANCE_RESULT or not acceptance_ok:
        ok = False
        result = BLOCKED_ACCEPTANCE_NOT_PASSED
        reason = "Acceptance payload must be PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND with ok=true."
    elif forbidden:
        ok = False
        result = BLOCKED_ACCEPTANCE_HANDOFF_UNSAFE
        reason = "Acceptance payload contains forbidden true safety flags."
    elif chatgpt_submit_performed:
        ok = False
        result = BLOCKED_ACCEPTANCE_HANDOFF_UNSAFE
        reason = "Acceptance payload indicates ChatGPT submit; handoff is no-send only."
    elif missing_true:
        ok = False
        result = BLOCKED_ACCEPTANCE_NOT_PASSED
        reason = "Acceptance payload is missing required true readiness fields: " + ",".join(missing_true)
    elif attempt_count < min_attempts or pass_count < min_passes or min_attempts <= 0 or min_passes <= 0:
        ok = False
        result = BLOCKED_ACCEPTANCE_NOT_PASSED
        reason = "Acceptance payload does not meet repeatability attempt/pass thresholds."

    no_send_verified = ok and not chatgpt_submit_performed
    return ChromeAcceptanceHandoff(
        ok=ok,
        result=result,
        schema_version=HANDOFF_SCHEMA_VERSION,
        handoff_kind=HANDOFF_KIND,
        expected_browser=EXPECTED_BROWSER,
        source_acceptance_basename=source_acceptance_basename,
        source_acceptance_sha256=source_acceptance_sha256,
        acceptance_result=str(acceptance_result) if acceptance_result is not None else None,
        acceptance_ok=acceptance_ok,
        attempt_count=attempt_count,
        min_attempts=min_attempts,
        pass_count=pass_count,
        min_passes=min_passes,
        failed_attempt_count=failed_attempt_count,
        no_send_verified=no_send_verified,
        chrome_executable_found=field_values["chrome_executable_found"],
        chrome_target_ready=field_values["chrome_target_ready"],
        canonical_report_found=field_values["canonical_report_found"],
        picker_opened=field_values["picker_opened"],
        exact_path_written=field_values["exact_path_written"],
        file_upload_attempted=field_values["file_upload_attempted"],
        attachment_verified=field_values["attachment_verified"],
        chatgpt_submit_performed=False if no_send_verified else chatgpt_submit_performed,
        forbidden_true_flags=forbidden,
        handoff_created_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        downstream_contract=_contract_payload(accepted=ok, reason=reason),
        reason=reason,
    )


def load_acceptance_payload(path: Path | str) -> tuple[dict[str, Any] | None, ChromeAcceptanceHandoff | None]:
    acceptance_path = Path(path).expanduser().resolve()
    if not acceptance_path.exists():
        handoff = ChromeAcceptanceHandoff(
            ok=False,
            result=BLOCKED_ACCEPTANCE_HANDOFF_MISSING,
            schema_version=HANDOFF_SCHEMA_VERSION,
            handoff_kind=HANDOFF_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_acceptance_basename=acceptance_path.name,
            source_acceptance_sha256=None,
            acceptance_result=None,
            acceptance_ok=False,
            attempt_count=0,
            min_attempts=0,
            pass_count=0,
            min_passes=0,
            failed_attempt_count=0,
            no_send_verified=False,
            chrome_executable_found=False,
            chrome_target_ready=False,
            canonical_report_found=False,
            picker_opened=False,
            exact_path_written=False,
            file_upload_attempted=False,
            attachment_verified=False,
            chatgpt_submit_performed=False,
            forbidden_true_flags=[],
            handoff_created_utc=None,
            downstream_contract=_contract_payload(accepted=False, reason="Acceptance JSON file is missing."),
            reason="Acceptance JSON file is missing.",
        )
        return None, handoff
    try:
        payload = json.loads(acceptance_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        handoff = ChromeAcceptanceHandoff(
            ok=False,
            result=BLOCKED_ACCEPTANCE_HANDOFF_INVALID_JSON,
            schema_version=HANDOFF_SCHEMA_VERSION,
            handoff_kind=HANDOFF_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_acceptance_basename=acceptance_path.name,
            source_acceptance_sha256=sha256_file(acceptance_path),
            acceptance_result=None,
            acceptance_ok=False,
            attempt_count=0,
            min_attempts=0,
            pass_count=0,
            min_passes=0,
            failed_attempt_count=0,
            no_send_verified=False,
            chrome_executable_found=False,
            chrome_target_ready=False,
            canonical_report_found=False,
            picker_opened=False,
            exact_path_written=False,
            file_upload_attempted=False,
            attachment_verified=False,
            chatgpt_submit_performed=False,
            forbidden_true_flags=[],
            handoff_created_utc=None,
            downstream_contract=_contract_payload(accepted=False, reason=f"Acceptance JSON is invalid: {exc}"),
            reason=f"Acceptance JSON is invalid: {exc}",
        )
        return None, handoff
    if not isinstance(payload, dict):
        payload = {}
    return payload, None


def load_and_validate_acceptance(path: Path | str) -> ChromeAcceptanceHandoff:
    acceptance_path = Path(path).expanduser().resolve()
    payload, blocked = load_acceptance_payload(acceptance_path)
    if blocked is not None:
        return blocked
    assert payload is not None
    return validate_acceptance_payload(
        payload,
        source_acceptance_basename=acceptance_path.name,
        source_acceptance_sha256=sha256_file(acceptance_path),
    )


def write_acceptance_handoff(handoff: ChromeAcceptanceHandoff, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = handoff.to_payload()
    payload["write_result"] = PASS_CHROME_ACCEPTANCE_HANDOFF_WRITTEN if handoff.ok else handoff.result
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_acceptance_handoff_marker(handoff: ChromeAcceptanceHandoff, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Chrome acceptance handoff",
        "=========================",
        f"result:{handoff.result}",
        f"ok:{str(handoff.ok).lower()}",
        f"handoff_kind:{handoff.handoff_kind}",
        f"expected_browser:{handoff.expected_browser}",
        f"source_acceptance:{handoff.source_acceptance_basename or ''}",
        f"source_acceptance_sha256:{handoff.source_acceptance_sha256 or ''}",
        f"acceptance_result:{handoff.acceptance_result or ''}",
        f"attempt_count:{handoff.attempt_count}",
        f"pass_count:{handoff.pass_count}",
        f"no_send_verified:{str(handoff.no_send_verified).lower()}",
        f"attachment_verified:{str(handoff.attachment_verified).lower()}",
        "chatgpt_submit_performed:false",
        "selenium_used:false",
        "webdriver_used:false",
        "browser_dom_automation_used:false",
        "conversation_text_logged:false",
        "raw_conversation_text_logged:false",
        f"reason:{handoff.reason}",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path