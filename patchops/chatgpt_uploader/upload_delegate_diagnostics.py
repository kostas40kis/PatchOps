from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


TRUE_TEXT_PATTERNS = ("true", "True", "TRUE")
FALSE_TEXT_PATTERNS = ("false", "False", "FALSE")

SAFETY_KEYS = (
    "chatgpt_submit_performed",
    "conversation_text_logged",
    "selenium_used",
    "webdriver_used",
    "browser_dom_automation_used",
)

UPLOAD_STAGE_KEYS = (
    "browser_picker_opened",
    "picker_opened",
    "file_picker_opened",
    "path_typed",
    "report_path_typed",
    "enter_pressed_once",
    "file_upload_attempted",
    "attachment_visible",
    "attachment_ready",
    "upload_progress_resolved",
)


@dataclass(frozen=True)
class UploadDelegateDiagnostic:
    delegate_attempted: bool
    delegate_exit_code: int | None
    delegate_exit_zero: bool
    browser_picker_opened: bool
    path_typed: bool
    enter_pressed_once: bool
    file_upload_attempted: bool
    attachment_visible: bool
    attachment_ready: bool
    upload_progress_resolved: bool
    chatgpt_submit_performed: bool
    conversation_text_logged: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    failure_layer: str
    classification: str
    recommended_next_mode: str
    parsed_json_evidence_count: int
    parsed_text_marker_count: int
    stdout_tail: str
    stderr_tail: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_key(key: str) -> str:
    return str(key or "").strip().lower().replace("-", "_").replace(" ", "_")


def _contains_bool_marker(text: str, key: str, value: bool) -> bool:
    key = _normalize_key(key)
    wanted = TRUE_TEXT_PATTERNS if value else FALSE_TEXT_PATTERNS
    patterns = []
    for word in wanted:
        patterns.extend([
            rf"(?im)^\s*{re.escape(key)}\s*:\s*{word}\s*$",
            rf"(?im)^\s*{re.escape(key.upper())}\s*:\s*{word}\s*$",
            rf"(?im)^\s*{re.escape(key.replace('_', ' ').title())}\s*:\s*{word}\s*$",
            rf"(?im)\"{re.escape(key)}\"\s*:\s*{word.lower()}",
        ])
    return any(re.search(pattern, text or "") for pattern in patterns)


def _truthy_from_payload(payload: Any, key: str) -> bool:
    if not isinstance(payload, dict):
        return False

    key = _normalize_key(key)

    candidates = [
        key,
        key.upper(),
        key.lower(),
        key.replace("_", "-"),
        key.replace("_", " "),
    ]
    for candidate in candidates:
        if candidate in payload:
            return bool(payload.get(candidate))

    safety = payload.get("safety_flags")
    if isinstance(safety, dict):
        for candidate in candidates:
            if candidate in safety:
                return bool(safety.get(candidate))

    return False


def _load_json_file(path: Path) -> dict[str, Any] | None:
    try:
        if path.exists() and path.is_file() and path.suffix.lower() == ".json":
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            if isinstance(data, dict):
                return data
    except Exception:
        return None
    return None


def _collect_json_payloads(evidence_dir: Path | None, stdout: str, stderr: str) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []

    for text in (stdout or "", stderr or ""):
        for line in text.splitlines():
            if "JSON_EVIDENCE:" in line:
                candidate = Path(line.split("JSON_EVIDENCE:", 1)[1].strip())
                payload = _load_json_file(candidate)
                if payload is not None:
                    payloads.append(payload)

    if evidence_dir is not None:
        try:
            for path in sorted(Path(evidence_dir).rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:25]:
                payload = _load_json_file(path)
                if payload is not None:
                    payloads.append(payload)
        except Exception:
            pass

    return payloads


def _bool_from_all_sources(key: str, stdout: str, stderr: str, payloads: list[dict[str, Any]]) -> bool:
    combined = (stdout or "") + "\n" + (stderr or "")
    if _contains_bool_marker(combined, key, True):
        return True
    return any(_truthy_from_payload(payload, key) for payload in payloads)


def _forbidden_side_effect(stdout: str, stderr: str, payloads: list[dict[str, Any]]) -> bool:
    for key in SAFETY_KEYS:
        if _bool_from_all_sources(key, stdout, stderr, payloads):
            return True
    return False


def _classify(payload: dict[str, Any]) -> tuple[str, str, str]:
    if payload["chatgpt_submit_performed"]:
        return (
            "forbidden_send",
            "forbidden_send_detected",
            "stop_and_repair_explicit_send_gate",
        )
    if payload["selenium_used"] or payload["webdriver_used"] or payload["browser_dom_automation_used"]:
        return (
            "forbidden_automation_backend",
            "forbidden_automation_backend_detected",
            "stop_and_remove_webdriver_or_dom_path",
        )
    if not payload["delegate_attempted"]:
        return (
            "delegate_not_attempted",
            "delegate_not_attempted",
            "rerun_with_existing_target_focused",
        )
    if not payload["delegate_exit_zero"]:
        return (
            "delegate_exit_nonzero",
            "delegate_crashed_or_blocked",
            "inspect_delegate_stdout_stderr_and_repair_first_exception",
        )
    if not payload["browser_picker_opened"]:
        return (
            "picker_not_opened",
            "upload_delegate_did_not_open_picker",
            "patch_picker_trigger_or_focus_gate",
        )
    if not payload["path_typed"]:
        return (
            "report_path_not_typed",
            "picker_opened_but_path_not_typed",
            "patch_picker_path_writer_or_dialog_focus",
        )
    if not payload["enter_pressed_once"]:
        return (
            "enter_not_confirmed",
            "path_typed_but_enter_not_confirmed",
            "patch_enter_confirmation_once",
        )
    if not payload["attachment_visible"]:
        return (
            "attachment_not_visible",
            "upload_attempted_but_attachment_not_visible",
            "patch_attachment_verifier_detection_or_wait",
        )
    if not payload["attachment_ready"]:
        return (
            "attachment_not_ready",
            "attachment_visible_but_not_ready",
            "patch_attachment_ready_wait",
        )
    if not payload["upload_progress_resolved"]:
        return (
            "upload_progress_unresolved",
            "attachment_ready_but_upload_progress_unresolved",
            "patch_upload_progress_wait",
        )
    return (
        "",
        "delegate_attachment_verified_no_send",
        "continue_to_u2_7c_no_send_existing_target_upload_proof",
    )


def classify_delegate_output(
    *,
    delegate_attempted: bool,
    delegate_exit_code: int | None,
    stdout: str = "",
    stderr: str = "",
    evidence_dir: str | Path | None = None,
) -> UploadDelegateDiagnostic:
    evidence_path = Path(evidence_dir).expanduser().resolve() if evidence_dir is not None else None
    payloads = _collect_json_payloads(evidence_path, stdout, stderr)

    payload = {
        "delegate_attempted": bool(delegate_attempted),
        "delegate_exit_code": delegate_exit_code,
        "delegate_exit_zero": delegate_exit_code == 0,
        "browser_picker_opened": _bool_from_all_sources("browser_picker_opened", stdout, stderr, payloads)
        or _bool_from_all_sources("picker_opened", stdout, stderr, payloads)
        or _bool_from_all_sources("file_picker_opened", stdout, stderr, payloads),
        "path_typed": _bool_from_all_sources("path_typed", stdout, stderr, payloads)
        or _bool_from_all_sources("report_path_typed", stdout, stderr, payloads),
        "enter_pressed_once": _bool_from_all_sources("enter_pressed_once", stdout, stderr, payloads)
        or _bool_from_all_sources("enter_pressed", stdout, stderr, payloads),
        "file_upload_attempted": bool(delegate_attempted)
        or _bool_from_all_sources("file_upload_attempted", stdout, stderr, payloads),
        "attachment_visible": _bool_from_all_sources("attachment_visible", stdout, stderr, payloads),
        "attachment_ready": _bool_from_all_sources("attachment_ready", stdout, stderr, payloads),
        "upload_progress_resolved": _bool_from_all_sources("upload_progress_resolved", stdout, stderr, payloads),
        "chatgpt_submit_performed": _bool_from_all_sources("chatgpt_submit_performed", stdout, stderr, payloads),
        "conversation_text_logged": _bool_from_all_sources("conversation_text_logged", stdout, stderr, payloads),
        "selenium_used": _bool_from_all_sources("selenium_used", stdout, stderr, payloads),
        "webdriver_used": _bool_from_all_sources("webdriver_used", stdout, stderr, payloads),
        "browser_dom_automation_used": _bool_from_all_sources("browser_dom_automation_used", stdout, stderr, payloads),
    }

    failure_layer, classification, recommended_next_mode = _classify(payload)

    marker_count = 0
    combined = (stdout or "") + "\n" + (stderr or "")
    for key in UPLOAD_STAGE_KEYS + SAFETY_KEYS:
        if _contains_bool_marker(combined, key, True) or _contains_bool_marker(combined, key, False):
            marker_count += 1

    return UploadDelegateDiagnostic(
        failure_layer=failure_layer,
        classification=classification,
        recommended_next_mode=recommended_next_mode,
        parsed_json_evidence_count=len(payloads),
        parsed_text_marker_count=marker_count,
        stdout_tail=(stdout or "")[-5000:],
        stderr_tail=(stderr or "")[-5000:],
        **payload,
    )


def write_delegate_diagnostic_evidence(evidence_dir: str | Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    out_dir = Path(evidence_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = payload.get("timestamp") or ""
    if not stamp:
        from datetime import datetime
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = out_dir / f"u2_7b_upload_delegate_diagnostic_{stamp}.json"
    txt_path = out_dir / f"u2_7b_upload_delegate_diagnostic_{stamp}.txt"

    payload = dict(payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")

    lines = [
        "PATCHOPS U2.7B UPLOAD DELEGATE LAYER DIAGNOSTIC",
        "================================================",
        f"PATCHOPS_U2_7B_STATUS: {payload.get('status', '')}",
        f"RESULT: {payload.get('result', '')}",
        f"RESULT_LABEL: {payload.get('result_label', '')}",
        f"JSON_EVIDENCE: {json_path}",
        f"TXT_EVIDENCE: {txt_path}",
        f"EXISTING_TARGET_FOUND: {str(payload.get('existing_target_found', False)).lower()}",
        f"EXISTING_TARGET_FOCUSED: {str(payload.get('existing_target_focused', False)).lower()}",
        f"DELEGATE_ATTEMPTED: {str(payload.get('delegate_attempted', False)).lower()}",
        f"DELEGATE_EXIT_CODE: {payload.get('delegate_exit_code', '')}",
        f"DELEGATE_EXIT_ZERO: {str(payload.get('delegate_exit_zero', False)).lower()}",
        f"BROWSER_PICKER_OPENED: {str(payload.get('browser_picker_opened', False)).lower()}",
        f"PATH_TYPED: {str(payload.get('path_typed', False)).lower()}",
        f"ENTER_PRESSED_ONCE: {str(payload.get('enter_pressed_once', False)).lower()}",
        f"FILE_UPLOAD_ATTEMPTED: {str(payload.get('file_upload_attempted', False)).lower()}",
        f"ATTACHMENT_VISIBLE: {str(payload.get('attachment_visible', False)).lower()}",
        f"ATTACHMENT_READY: {str(payload.get('attachment_ready', False)).lower()}",
        f"UPLOAD_PROGRESS_RESOLVED: {str(payload.get('upload_progress_resolved', False)).lower()}",
        f"FAILURE_LAYER: {payload.get('failure_layer', '')}",
        f"CLASSIFICATION: {payload.get('classification', '')}",
        f"RECOMMENDED_NEXT_MODE: {payload.get('recommended_next_mode', '')}",
        f"PARSED_JSON_EVIDENCE_COUNT: {payload.get('parsed_json_evidence_count', 0)}",
        f"PARSED_TEXT_MARKER_COUNT: {payload.get('parsed_text_marker_count', 0)}",
        "CHATGPT_SUBMIT_PERFORMED: false",
        "CONVERSATION_TEXT_LOGGED: false",
        "SELENIUM_USED: false",
        "WEBDRIVER_USED: false",
        "BROWSER_DOM_AUTOMATION_USED: false",
        "",
    ]
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path
