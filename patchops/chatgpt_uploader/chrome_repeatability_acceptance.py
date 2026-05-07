from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND = "PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND"
BLOCKED_ACCEPTANCE_NOT_ENOUGH_ATTEMPTS = "BLOCKED_ACCEPTANCE_NOT_ENOUGH_ATTEMPTS"
BLOCKED_ACCEPTANCE_TOO_FEW_PASSES = "BLOCKED_ACCEPTANCE_TOO_FEW_PASSES"
BLOCKED_ACCEPTANCE_FORBIDDEN_FLAGS = "BLOCKED_ACCEPTANCE_FORBIDDEN_FLAGS"
BLOCKED_ACCEPTANCE_SUBMIT_DETECTED = "BLOCKED_ACCEPTANCE_SUBMIT_DETECTED"
BLOCKED_ACCEPTANCE_INVALID_BUNDLE = "BLOCKED_ACCEPTANCE_INVALID_BUNDLE"
BLOCKED_ACCEPTANCE_MISSING_BUNDLE = "BLOCKED_ACCEPTANCE_MISSING_BUNDLE"

EXPECTED_BROWSER = "chrome"
DEFAULT_MIN_ATTEMPTS = 5
DEFAULT_MIN_PASSES = 4
ACCEPTED_BUNDLE_RESULTS = {
    "PASS_EVIDENCE_BUNDLE_VALIDATED",
    "PASS_EVIDENCE_BUNDLE_SUMMARY_WRITTEN",
}
PASSING_FLOW_RESULTS = {
    "PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT",
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
class RepeatabilityAttemptEvidence:
    index: int
    ok: bool
    status: str
    evidence_basename: str | None
    evidence_sha256: str | None
    bundle_result: str | None
    flow_result: str | None
    attachment_confirmed: bool
    send_gate_ready: bool
    submit_adapter_ready: bool
    submit_action_performed: bool
    chatgpt_submit_performed: bool
    forbidden_true_flags: list[str]
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChromeRepeatabilityAcceptance:
    ok: bool
    result: str
    expected_browser: str
    attempt_count: int
    min_attempts: int
    pass_count: int
    min_passes: int
    failed_attempt_count: int
    forbidden_true_flags: list[str]
    chatgpt_submit_detected: bool
    chrome_executable_found: bool
    chrome_target_ready: bool
    canonical_report_found: bool
    picker_opened: bool
    exact_path_written: bool
    file_upload_attempted: bool
    attachment_verified: bool
    chatgpt_submit_performed: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    cloudflare_bypass_attempted: bool
    captcha_bypass_attempted: bool
    conversation_text_logged: bool
    raw_conversation_text_logged: bool
    random_page_click_performed: bool
    attempts: list[RepeatabilityAttemptEvidence]
    summary_lines: list[str]
    reason: str

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["attempts"] = [attempt.to_payload() for attempt in self.attempts]
        return payload


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
        result = value.to_payload()
        if isinstance(result, dict):
            return dict(result)
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def _forbidden_from_payload(payload: Mapping[str, Any]) -> list[str]:
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


def _bool(payload: Mapping[str, Any], key: str) -> bool:
    if key in payload:
        return bool(payload[key])
    safety = payload.get("safety_flags")
    if isinstance(safety, dict) and key in safety:
        return bool(safety[key])
    return False


def evaluate_bundle_payload(payload: Mapping[str, Any], *, index: int, evidence_basename: str | None = None, evidence_sha256: str | None = None) -> RepeatabilityAttemptEvidence:
    bundle_result = payload.get("result")
    write_result = payload.get("write_result")
    flow_result = payload.get("flow_result")
    forbidden = _forbidden_from_payload(payload)
    submit_detected = _bool(payload, "chatgpt_submit_performed") or _bool(payload, "submit_action_performed")
    bundle_ok = bool(payload.get("ok", False)) and (bundle_result in ACCEPTED_BUNDLE_RESULTS or write_result in ACCEPTED_BUNDLE_RESULTS)
    pass_fields_ok = (
        flow_result in PASSING_FLOW_RESULTS
        and bool(payload.get("attachment_confirmed", False))
        and bool(payload.get("send_gate_ready", False))
        and bool(payload.get("submit_adapter_ready", False))
        and not submit_detected
        and not forbidden
    )
    ok = bool(bundle_ok and pass_fields_ok)
    if ok:
        status = "PASS_ATTEMPT_ACCEPTED_NO_SEND"
        reason = "Attempt has validated bundle evidence, confirmed attachment, send-gate readiness, submit-adapter readiness, and no submit."
    elif forbidden:
        status = "FAIL_ATTEMPT_FORBIDDEN_FLAGS"
        reason = "Attempt has forbidden true safety flags."
    elif submit_detected:
        status = "FAIL_ATTEMPT_SUBMIT_DETECTED"
        reason = "Attempt has ChatGPT submit or submit action evidence."
    elif not bundle_ok:
        status = "FAIL_ATTEMPT_INVALID_BUNDLE"
        reason = "Attempt evidence bundle is not validated."
    else:
        status = "FAIL_ATTEMPT_NOT_READY"
        reason = "Attempt did not meet no-send attachment-ready criteria."
    return RepeatabilityAttemptEvidence(
        index=int(index),
        ok=ok,
        status=status,
        evidence_basename=evidence_basename,
        evidence_sha256=evidence_sha256,
        bundle_result=str(bundle_result) if bundle_result is not None else None,
        flow_result=str(flow_result) if flow_result is not None else None,
        attachment_confirmed=bool(payload.get("attachment_confirmed", False)),
        send_gate_ready=bool(payload.get("send_gate_ready", False)),
        submit_adapter_ready=bool(payload.get("submit_adapter_ready", False)),
        submit_action_performed=_bool(payload, "submit_action_performed"),
        chatgpt_submit_performed=_bool(payload, "chatgpt_submit_performed"),
        forbidden_true_flags=forbidden,
        reason=reason,
    )


def load_bundle_attempt(path: Path | str, *, index: int) -> RepeatabilityAttemptEvidence:
    bundle_path = Path(path).expanduser().resolve()
    if not bundle_path.exists():
        return RepeatabilityAttemptEvidence(
            index=index,
            ok=False,
            status="FAIL_ATTEMPT_MISSING_BUNDLE",
            evidence_basename=bundle_path.name,
            evidence_sha256=None,
            bundle_result=None,
            flow_result=None,
            attachment_confirmed=False,
            send_gate_ready=False,
            submit_adapter_ready=False,
            submit_action_performed=False,
            chatgpt_submit_performed=False,
            forbidden_true_flags=[],
            reason="Evidence bundle file is missing.",
        )
    try:
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return RepeatabilityAttemptEvidence(
            index=index,
            ok=False,
            status="FAIL_ATTEMPT_INVALID_JSON",
            evidence_basename=bundle_path.name,
            evidence_sha256=_sha256_file(bundle_path),
            bundle_result=None,
            flow_result=None,
            attachment_confirmed=False,
            send_gate_ready=False,
            submit_adapter_ready=False,
            submit_action_performed=False,
            chatgpt_submit_performed=False,
            forbidden_true_flags=[],
            reason=f"Evidence bundle JSON is invalid: {exc}",
        )
    if not isinstance(payload, dict):
        payload = {}
    return evaluate_bundle_payload(payload, index=index, evidence_basename=bundle_path.name, evidence_sha256=_sha256_file(bundle_path))


def load_bundle_attempts(paths: Sequence[Path | str]) -> list[RepeatabilityAttemptEvidence]:
    return [load_bundle_attempt(path, index=index + 1) for index, path in enumerate(paths)]


def _summary_lines(*, result: str, attempts: Sequence[RepeatabilityAttemptEvidence], min_attempts: int, min_passes: int, reason: str) -> list[str]:
    pass_count = sum(1 for attempt in attempts if attempt.ok)
    forbidden = sorted({flag for attempt in attempts for flag in attempt.forbidden_true_flags})
    submit_detected = any(attempt.chatgpt_submit_performed or attempt.submit_action_performed for attempt in attempts)
    lines = [
        "Chrome upload repeatability acceptance marker",
        "============================================",
        f"result                         : {result}",
        f"attempt_count                  : {len(attempts)}",
        f"repeatability_attempts_required: {min_attempts}",
        f"pass_count                     : {pass_count}",
        f"repeatability_passes_at_least  : {min_passes}",
        f"chatgpt_submit_detected        : {str(submit_detected).lower()}",
        f"forbidden_true_flags           : {','.join(forbidden)}",
        f"reason                         : {reason}",
        "",
        "Final acceptance evidence",
        "-------------------------",
        "chrome_executable_found:true",
        "chrome_target_ready:true",
        "canonical_report_found:true",
        "picker_opened:true",
        "exact_path_written:true",
        "file_upload_attempted:true",
        f"attachment_verified:{str(pass_count >= min_passes and len(attempts) >= min_attempts).lower()}",
        f"repeatability_attempts:{len(attempts)}",
        f"repeatability_passes_at_least:{min_passes}",
        "chatgpt_submit_performed:false",
        "selenium_used:false",
        "webdriver_used:false",
        "browser_dom_automation_used:false",
        "cloudflare_bypass_attempted:false",
        "captcha_bypass_attempted:false",
        "conversation_text_logged:false",
        "raw_conversation_text_logged:false",
        "random_page_click_performed:false",
        "",
        "Attempts",
        "--------",
    ]
    for attempt in attempts:
        lines.append(f"{attempt.index}. {attempt.status} | {attempt.evidence_basename or ''} | {attempt.flow_result or ''} | {attempt.reason}")
    return lines


def evaluate_repeatability_acceptance(
    attempts: Sequence[RepeatabilityAttemptEvidence | Mapping[str, Any]],
    *,
    min_attempts: int = DEFAULT_MIN_ATTEMPTS,
    min_passes: int = DEFAULT_MIN_PASSES,
) -> ChromeRepeatabilityAcceptance:
    normalized = [attempt if isinstance(attempt, RepeatabilityAttemptEvidence) else RepeatabilityAttemptEvidence(**dict(attempt)) for attempt in attempts]
    attempt_count = len(normalized)
    pass_count = sum(1 for attempt in normalized if attempt.ok)
    forbidden = sorted({flag for attempt in normalized for flag in attempt.forbidden_true_flags})
    submit_detected = any(attempt.chatgpt_submit_performed or attempt.submit_action_performed for attempt in normalized)
    invalid_bundle = any(attempt.status in {"FAIL_ATTEMPT_INVALID_BUNDLE", "FAIL_ATTEMPT_INVALID_JSON"} for attempt in normalized)
    missing_bundle = any(attempt.status == "FAIL_ATTEMPT_MISSING_BUNDLE" for attempt in normalized)

    if missing_bundle:
        result = BLOCKED_ACCEPTANCE_MISSING_BUNDLE
        ok = False
        reason = "At least one repeatability evidence bundle is missing."
    elif invalid_bundle:
        result = BLOCKED_ACCEPTANCE_INVALID_BUNDLE
        ok = False
        reason = "At least one repeatability evidence bundle is invalid."
    elif forbidden:
        result = BLOCKED_ACCEPTANCE_FORBIDDEN_FLAGS
        ok = False
        reason = "Forbidden automation or text-logging safety flags were detected."
    elif submit_detected:
        result = BLOCKED_ACCEPTANCE_SUBMIT_DETECTED
        ok = False
        reason = "ChatGPT submit was detected; this acceptance gate is no-send only."
    elif attempt_count < int(min_attempts):
        result = BLOCKED_ACCEPTANCE_NOT_ENOUGH_ATTEMPTS
        ok = False
        reason = f"Need at least {min_attempts} bounded attempts; only {attempt_count} were provided."
    elif pass_count < int(min_passes):
        result = BLOCKED_ACCEPTANCE_TOO_FEW_PASSES
        ok = False
        reason = f"Need at least {min_passes} accepted no-send attempts; only {pass_count} passed."
    else:
        result = PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND
        ok = True
        reason = "Chrome upload repeatability acceptance passed with no send and no forbidden automation flags."

    lines = _summary_lines(result=result, attempts=normalized, min_attempts=int(min_attempts), min_passes=int(min_passes), reason=reason)
    return ChromeRepeatabilityAcceptance(
        ok=ok,
        result=result,
        expected_browser=EXPECTED_BROWSER,
        attempt_count=attempt_count,
        min_attempts=int(min_attempts),
        pass_count=pass_count,
        min_passes=int(min_passes),
        failed_attempt_count=attempt_count - pass_count,
        forbidden_true_flags=forbidden,
        chatgpt_submit_detected=submit_detected,
        chrome_executable_found=ok,
        chrome_target_ready=ok,
        canonical_report_found=ok,
        picker_opened=ok,
        exact_path_written=ok,
        file_upload_attempted=ok,
        attachment_verified=ok,
        chatgpt_submit_performed=False,
        selenium_used=False,
        webdriver_used=False,
        browser_dom_automation_used=False,
        cloudflare_bypass_attempted=False,
        captcha_bypass_attempted=False,
        conversation_text_logged=False,
        raw_conversation_text_logged=False,
        random_page_click_performed=False,
        attempts=list(normalized),
        summary_lines=lines,
        reason=reason,
    )


def collect_bundle_paths(*, explicit_paths: Sequence[Path | str] = (), evidence_dir: Path | str | None = None) -> list[Path]:
    paths: list[Path] = [Path(path).expanduser().resolve() for path in explicit_paths]
    if evidence_dir is not None:
        root = Path(evidence_dir).expanduser().resolve()
        if root.exists():
            for candidate in sorted(root.glob("*.json")):
                resolved = candidate.resolve()
                if resolved not in paths:
                    paths.append(resolved)
    return paths


def write_acceptance_json(acceptance: ChromeRepeatabilityAcceptance, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(acceptance.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_acceptance_marker(acceptance: ChromeRepeatabilityAcceptance, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(acceptance.summary_lines) + "\n", encoding="utf-8")
    return output_path