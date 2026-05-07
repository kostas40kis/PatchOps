from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.chatgpt_uploader.chrome_picker_path_entry import (
    BLOCKED_CANONICAL_REPORT_MISSING,
    BLOCKED_PATH_NOT_CANONICAL_REPORT,
    hash_path,
    validate_canonical_report_path,
)

PASS_ATTACHMENT_CONFIRMED_NO_SEND = "PASS_ATTACHMENT_CONFIRMED_NO_SEND"
PASS_ATTACHMENT_VERIFICATION_WAITING = "PASS_ATTACHMENT_VERIFICATION_WAITING"
BLOCKED_ATTACHMENT_NOT_FOUND = "BLOCKED_ATTACHMENT_NOT_FOUND"
BLOCKED_ATTACHMENT_AMBIGUOUS = "BLOCKED_ATTACHMENT_AMBIGUOUS"
BLOCKED_UPLOAD_NOT_ATTEMPTED = "BLOCKED_UPLOAD_NOT_ATTEMPTED"
BLOCKED_ATTACHMENT_VERIFICATION_CONFIRMATION_MISSING = "BLOCKED_ATTACHMENT_VERIFICATION_CONFIRMATION_MISSING"
BLOCKED_LIVE_ATTACHMENT_VERIFICATION_UNSUPPORTED = "BLOCKED_LIVE_ATTACHMENT_VERIFICATION_UNSUPPORTED"

EXPECTED_BROWSER = "chrome"
LIVE_CONFIRM_TEXT = "PATCHOPS_CONFIRM_ATTACHMENT_VERIFY_NO_SEND"

SAFETY_FLAGS = {
    "selenium_used": False,
    "webdriver_used": False,
    "browser_dom_automation_used": False,
    "cloudflare_bypass_attempted": False,
    "captcha_bypass_attempted": False,
    "conversation_text_logged": False,
    "raw_conversation_text_logged": False,
    "random_page_click_performed": False,
    "chatgpt_submit_performed": False,
    "send_allowed": False,
    "send_button_pressed": False,
    "file_upload_attempted": False,
    "attachment_confirmed": False,
    "live_browser_used": False,
}


@dataclass(frozen=True)
class AttachmentCandidate:
    basename: str
    basename_sha256: str
    suffix: str
    visible: bool
    stable: bool
    remove_button_visible: bool
    progress_visible: bool
    error_visible: bool
    source: str = "descriptor"
    selected: bool = False

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AttachmentVerificationEvidence:
    ok: bool
    result: str
    expected_browser: str
    live_browser_used: bool
    upload_attempted_before_verification: bool
    file_upload_attempted: bool
    canonical_report: dict[str, Any]
    expected_basename: str | None
    expected_basename_sha256: str | None
    candidate_count: int
    matching_candidate_count: int
    selected_attachment: dict[str, Any] | None
    attachment_confirmed: bool
    attachment_stable: bool
    attachment_error_visible: bool
    chatgpt_submit_performed: bool
    send_allowed: bool
    raw_conversation_text_logged: bool
    candidates: list[AttachmentCandidate]
    safety_flags: dict[str, bool]
    reason: str

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["candidates"] = [candidate.to_payload() for candidate in self.candidates]
        return payload


def sha256_text(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def basename_hash(basename: str) -> str:
    return sha256_text(Path(str(basename)).name)


def build_attachment_candidate(
    *,
    basename: str,
    visible: bool = True,
    stable: bool = True,
    remove_button_visible: bool = True,
    progress_visible: bool = False,
    error_visible: bool = False,
    source: str = "descriptor",
    selected: bool = False,
) -> AttachmentCandidate:
    clean_name = Path(str(basename)).name
    return AttachmentCandidate(
        basename=clean_name,
        basename_sha256=basename_hash(clean_name),
        suffix=Path(clean_name).suffix.lower(),
        visible=bool(visible),
        stable=bool(stable),
        remove_button_visible=bool(remove_button_visible),
        progress_visible=bool(progress_visible),
        error_visible=bool(error_visible),
        source=str(source or "descriptor"),
        selected=bool(selected),
    )


def candidate_from_payload(payload: Mapping[str, Any]) -> AttachmentCandidate:
    return build_attachment_candidate(
        basename=str(payload.get("basename") or payload.get("name") or payload.get("filename") or ""),
        visible=bool(payload.get("visible", True)),
        stable=bool(payload.get("stable", True)),
        remove_button_visible=bool(payload.get("remove_button_visible", payload.get("remove_visible", True))),
        progress_visible=bool(payload.get("progress_visible", False)),
        error_visible=bool(payload.get("error_visible", False)),
        source=str(payload.get("source") or "descriptor"),
        selected=bool(payload.get("selected", False)),
    )


def _candidate_matches(candidate: AttachmentCandidate, expected_basename: str) -> bool:
    return (
        candidate.basename == expected_basename
        and candidate.visible
        and candidate.stable
        and candidate.remove_button_visible
        and not candidate.progress_visible
        and not candidate.error_visible
    )


def _blocked_evidence(
    *,
    result: str,
    canonical_report: dict[str, Any],
    expected_basename: str | None,
    upload_attempted_before_verification: bool,
    candidates: Sequence[AttachmentCandidate],
    reason: str,
    live_browser_used: bool = False,
) -> AttachmentVerificationEvidence:
    safety = dict(SAFETY_FLAGS)
    safety["live_browser_used"] = bool(live_browser_used)
    safety["file_upload_attempted"] = bool(upload_attempted_before_verification)
    matches = [candidate for candidate in candidates if expected_basename and _candidate_matches(candidate, expected_basename)]
    return AttachmentVerificationEvidence(
        ok=False,
        result=result,
        expected_browser=EXPECTED_BROWSER,
        live_browser_used=bool(live_browser_used),
        upload_attempted_before_verification=bool(upload_attempted_before_verification),
        file_upload_attempted=bool(upload_attempted_before_verification),
        canonical_report=canonical_report,
        expected_basename=expected_basename,
        expected_basename_sha256=basename_hash(expected_basename) if expected_basename else None,
        candidate_count=len(candidates),
        matching_candidate_count=len(matches),
        selected_attachment=None,
        attachment_confirmed=False,
        attachment_stable=False,
        attachment_error_visible=any(candidate.error_visible for candidate in candidates),
        chatgpt_submit_performed=False,
        send_allowed=False,
        raw_conversation_text_logged=False,
        candidates=list(candidates),
        safety_flags=safety,
        reason=reason,
    )


def verify_attachment_candidates(
    *,
    canonical_report_path: Path | str,
    upload_attempted_before_verification: bool,
    candidates: Sequence[AttachmentCandidate | Mapping[str, Any]],
    live_browser_used: bool = False,
) -> AttachmentVerificationEvidence:
    report = validate_canonical_report_path(canonical_report_path)
    if not report.ok:
        return _blocked_evidence(
            result=report.result,
            canonical_report=report.to_payload(),
            expected_basename=report.basename,
            upload_attempted_before_verification=upload_attempted_before_verification,
            candidates=[],
            reason=report.reason,
            live_browser_used=False,
        )

    expected_basename = str(report.basename)
    normalized_candidates = [candidate if isinstance(candidate, AttachmentCandidate) else candidate_from_payload(candidate) for candidate in candidates]

    if not upload_attempted_before_verification:
        return _blocked_evidence(
            result=BLOCKED_UPLOAD_NOT_ATTEMPTED,
            canonical_report=report.to_payload(),
            expected_basename=expected_basename,
            upload_attempted_before_verification=False,
            candidates=normalized_candidates,
            reason="Attachment verification requires a prior controlled picker Enter/upload attempt.",
            live_browser_used=live_browser_used,
        )

    matches = [candidate for candidate in normalized_candidates if _candidate_matches(candidate, expected_basename)]
    if not matches:
        result = PASS_ATTACHMENT_VERIFICATION_WAITING if normalized_candidates else BLOCKED_ATTACHMENT_NOT_FOUND
        reason = "No stable visible attachment candidate matched the canonical report basename yet."
        return _blocked_evidence(
            result=result,
            canonical_report=report.to_payload(),
            expected_basename=expected_basename,
            upload_attempted_before_verification=True,
            candidates=normalized_candidates,
            reason=reason,
            live_browser_used=live_browser_used,
        )

    if len(matches) > 1:
        return _blocked_evidence(
            result=BLOCKED_ATTACHMENT_AMBIGUOUS,
            canonical_report=report.to_payload(),
            expected_basename=expected_basename,
            upload_attempted_before_verification=True,
            candidates=normalized_candidates,
            reason="Multiple stable visible attachment candidates matched the canonical report basename.",
            live_browser_used=live_browser_used,
        )

    selected = matches[0]
    marked_candidates = [
        AttachmentCandidate(
            basename=candidate.basename,
            basename_sha256=candidate.basename_sha256,
            suffix=candidate.suffix,
            visible=candidate.visible,
            stable=candidate.stable,
            remove_button_visible=candidate.remove_button_visible,
            progress_visible=candidate.progress_visible,
            error_visible=candidate.error_visible,
            source=candidate.source,
            selected=candidate.basename_sha256 == selected.basename_sha256 and candidate.source == selected.source,
        )
        for candidate in normalized_candidates
    ]
    selected_payload = selected.to_payload()
    selected_payload["selected"] = True
    safety = dict(SAFETY_FLAGS)
    safety["live_browser_used"] = bool(live_browser_used)
    safety["file_upload_attempted"] = True
    safety["attachment_confirmed"] = True

    return AttachmentVerificationEvidence(
        ok=True,
        result=PASS_ATTACHMENT_CONFIRMED_NO_SEND,
        expected_browser=EXPECTED_BROWSER,
        live_browser_used=bool(live_browser_used),
        upload_attempted_before_verification=True,
        file_upload_attempted=True,
        canonical_report=report.to_payload(),
        expected_basename=expected_basename,
        expected_basename_sha256=basename_hash(expected_basename),
        candidate_count=len(normalized_candidates),
        matching_candidate_count=1,
        selected_attachment=selected_payload,
        attachment_confirmed=True,
        attachment_stable=True,
        attachment_error_visible=False,
        chatgpt_submit_performed=False,
        send_allowed=False,
        raw_conversation_text_logged=False,
        candidates=marked_candidates,
        safety_flags=safety,
        reason="Canonical report attachment was confirmed by stable visible descriptor; send remains blocked.",
    )


def verify_attachment_no_send(
    *,
    canonical_report_path: Path | str,
    upload_attempted_before_verification: bool = False,
    attachment_descriptors: Sequence[AttachmentCandidate | Mapping[str, Any]] = (),
    live_browser: bool = False,
    confirm_live_browser_text: str | None = None,
) -> AttachmentVerificationEvidence:
    if live_browser:
        report = validate_canonical_report_path(canonical_report_path)
        expected_basename = report.basename if report.basename else None
        if confirm_live_browser_text != LIVE_CONFIRM_TEXT:
            return _blocked_evidence(
                result=BLOCKED_ATTACHMENT_VERIFICATION_CONFIRMATION_MISSING,
                canonical_report=report.to_payload(),
                expected_basename=expected_basename,
                upload_attempted_before_verification=upload_attempted_before_verification,
                candidates=[],
                reason=f"Live attachment verification requires --confirm-live-browser-text {LIVE_CONFIRM_TEXT}.",
                live_browser_used=False,
            )
        return _blocked_evidence(
            result=BLOCKED_LIVE_ATTACHMENT_VERIFICATION_UNSUPPORTED,
            canonical_report=report.to_payload(),
            expected_basename=expected_basename,
            upload_attempted_before_verification=upload_attempted_before_verification,
            candidates=[],
            reason="Live attachment UI reading is not implemented in this patch; provide safe descriptors from an approved detector in a later patch.",
            live_browser_used=False,
        )

    return verify_attachment_candidates(
        canonical_report_path=canonical_report_path,
        upload_attempted_before_verification=upload_attempted_before_verification,
        candidates=attachment_descriptors,
        live_browser_used=False,
    )


def write_attachment_verification_evidence(evidence: AttachmentVerificationEvidence, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evidence.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path