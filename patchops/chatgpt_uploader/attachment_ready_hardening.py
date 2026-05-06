from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REQUIRED_TRUE_IN_ORDER = (
    ("existing_target_found", "existing_target_not_found", "open_or_focus_configured_edge_chatgpt_target"),
    ("existing_target_focused", "existing_target_not_focused", "repair_edge_focus_before_upload"),
    ("launch_skipped_existing_target", "launch_not_skipped", "repair_existing_target_preferred_launch_skip"),
    ("canonical_trigger_attempted", "canonical_trigger_not_attempted", "repair_live_picker_permission_or_trigger_gate"),
    ("slash_sent", "slash_not_sent", "repair_canonical_slash_trigger"),
    ("browser_picker_opened", "picker_not_opened", "repair_picker_open_detection_or_focus"),
    ("file_path_written", "file_path_not_written", "repair_file_dialog_path_writer"),
    ("picker_enter_pressed", "picker_enter_not_pressed", "repair_single_enter_confirmation"),
    ("file_upload_attempted", "file_upload_not_attempted", "repair_delegate_upload_attempt_state"),
    ("attachment_verification_attempted", "attachment_verification_not_attempted", "repair_attachment_verification_gate"),
    ("attachment_visible", "attachment_not_visible", "repair_attachment_visibility_detection_or_wait"),
    ("attachment_ready", "attachment_not_ready", "repair_attachment_ready_wait"),
    ("upload_progress_resolved", "upload_progress_unresolved", "repair_upload_progress_wait"),
)

FORBIDDEN_TRUE_KEYS = (
    "chatgpt_submit_performed",
    "conversation_text_logged",
    "selenium_used",
    "webdriver_used",
    "browser_dom_automation_used",
    "random_page_click_performed",
)


@dataclass(frozen=True)
class AttachmentReadyHardeningResult:
    status: str
    result: str
    result_label: str
    failure_layer: str
    recommended_next_mode: str
    existing_target_found: bool
    existing_target_focused: bool
    launch_skipped_existing_target: bool
    normal_edge_launch_attempted: bool
    canonical_trigger_attempted: bool
    slash_sent: bool
    browser_picker_opened: bool
    file_path_written: bool
    picker_enter_pressed: bool
    file_upload_attempted: bool
    attachment_verification_attempted: bool
    attachment_visible: bool
    attachment_ready: bool
    upload_progress_resolved: bool
    chatgpt_submit_performed: bool
    conversation_text_logged: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    random_page_click_performed: bool
    source_status: str
    source_result: str
    source_json_evidence: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _as_bool(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _source_payload(stdout: str) -> dict[str, Any]:
    for line in (stdout or "").splitlines():
        if line.startswith("JSON_EVIDENCE:"):
            candidate = Path(line.split(":", 1)[1].strip())
            if candidate.exists():
                data = json.loads(candidate.read_text(encoding="utf-8", errors="replace"))
                if isinstance(data, dict):
                    data["source_json_evidence"] = str(candidate)
                    return data
    return {}


def load_source_payload_from_stdout(stdout: str) -> dict[str, Any]:
    return _source_payload(stdout)


def classify_attachment_ready_payload(payload: dict[str, Any]) -> AttachmentReadyHardeningResult:
    payload = dict(payload or {})

    forbidden_hit = next((key for key in FORBIDDEN_TRUE_KEYS if _as_bool(payload, key)), "")

    if forbidden_hit:
        status = "FAIL_FORBIDDEN_SIDE_EFFECT"
        result = "FAIL_FORBIDDEN_SIDE_EFFECT"
        result_label = "FAIL_FORBIDDEN_SIDE_EFFECT"
        failure_layer = forbidden_hit
        recommended_next_mode = "stop_and_repair_forbidden_side_effect_guard"
    else:
        missing = ""
        recommended_next_mode = ""
        for key, failure, recommendation in REQUIRED_TRUE_IN_ORDER:
            if not _as_bool(payload, key):
                missing = failure
                recommended_next_mode = recommendation
                break

        if missing:
            status = "PASS_OR_BLOCKED"
            result = "PASS_OR_BLOCKED_ATTACHMENT_READY_HARDENING_FIRST_LAYER_CLASSIFIED"
            result_label = "PASS_OR_BLOCKED_ATTACHMENT_READY_HARDENING_FIRST_LAYER_CLASSIFIED"
            failure_layer = missing
        else:
            status = "PASS"
            result = "PASS_ATTACHMENT_READY_NO_SEND_HARDENED"
            result_label = "PASS_ATTACHMENT_READY_NO_SEND_HARDENED"
            failure_layer = ""
            recommended_next_mode = "continue_to_u2_7e_repeatability_or_queue_foundation"

    return AttachmentReadyHardeningResult(
        status=status,
        result=result,
        result_label=result_label,
        failure_layer=failure_layer,
        recommended_next_mode=recommended_next_mode,
        existing_target_found=_as_bool(payload, "existing_target_found"),
        existing_target_focused=_as_bool(payload, "existing_target_focused"),
        launch_skipped_existing_target=_as_bool(payload, "launch_skipped_existing_target"),
        normal_edge_launch_attempted=_as_bool(payload, "normal_edge_launch_attempted"),
        canonical_trigger_attempted=_as_bool(payload, "canonical_trigger_attempted"),
        slash_sent=_as_bool(payload, "slash_sent"),
        browser_picker_opened=_as_bool(payload, "browser_picker_opened"),
        file_path_written=_as_bool(payload, "file_path_written"),
        picker_enter_pressed=_as_bool(payload, "picker_enter_pressed"),
        file_upload_attempted=_as_bool(payload, "file_upload_attempted"),
        attachment_verification_attempted=_as_bool(payload, "attachment_verification_attempted"),
        attachment_visible=_as_bool(payload, "attachment_visible"),
        attachment_ready=_as_bool(payload, "attachment_ready"),
        upload_progress_resolved=_as_bool(payload, "upload_progress_resolved"),
        chatgpt_submit_performed=_as_bool(payload, "chatgpt_submit_performed"),
        conversation_text_logged=_as_bool(payload, "conversation_text_logged"),
        selenium_used=_as_bool(payload, "selenium_used"),
        webdriver_used=_as_bool(payload, "webdriver_used"),
        browser_dom_automation_used=_as_bool(payload, "browser_dom_automation_used"),
        random_page_click_performed=_as_bool(payload, "random_page_click_performed"),
        source_status=str(payload.get("status") or ""),
        source_result=str(payload.get("result") or ""),
        source_json_evidence=str(payload.get("source_json_evidence") or payload.get("json_evidence") or ""),
    )


def write_attachment_ready_hardening_evidence(evidence_dir: str | Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    out_dir = Path(evidence_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "u2_7d_attachment_ready_hardening.json"
    txt_path = out_dir / "u2_7d_attachment_ready_hardening.txt"

    payload = dict(payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")

    lines = [
        "PATCHOPS U2.7D ATTACHMENT READY NO-SEND HARDENING",
        "=================================================",
        f"PATCHOPS_U2_7D_STATUS: {payload.get('status', '')}",
        f"RESULT: {payload.get('result', '')}",
        f"RESULT_LABEL: {payload.get('result_label', '')}",
        f"JSON_EVIDENCE: {json_path}",
        f"TXT_EVIDENCE: {txt_path}",
        f"FAILURE_LAYER: {payload.get('failure_layer', '')}",
        f"RECOMMENDED_NEXT_MODE: {payload.get('recommended_next_mode', '')}",
        f"EXISTING_TARGET_FOUND: {str(payload.get('existing_target_found', False)).lower()}",
        f"EXISTING_TARGET_FOCUSED: {str(payload.get('existing_target_focused', False)).lower()}",
        f"LAUNCH_SKIPPED_EXISTING_TARGET: {str(payload.get('launch_skipped_existing_target', False)).lower()}",
        f"NORMAL_EDGE_LAUNCH_ATTEMPTED: {str(payload.get('normal_edge_launch_attempted', False)).lower()}",
        f"CANONICAL_TRIGGER_ATTEMPTED: {str(payload.get('canonical_trigger_attempted', False)).lower()}",
        f"SLASH_SENT: {str(payload.get('slash_sent', False)).lower()}",
        f"BROWSER_PICKER_OPENED: {str(payload.get('browser_picker_opened', False)).lower()}",
        f"FILE_PATH_WRITTEN: {str(payload.get('file_path_written', False)).lower()}",
        f"PICKER_ENTER_PRESSED: {str(payload.get('picker_enter_pressed', False)).lower()}",
        f"FILE_UPLOAD_ATTEMPTED: {str(payload.get('file_upload_attempted', False)).lower()}",
        f"ATTACHMENT_VERIFICATION_ATTEMPTED: {str(payload.get('attachment_verification_attempted', False)).lower()}",
        f"ATTACHMENT_VISIBLE: {str(payload.get('attachment_visible', False)).lower()}",
        f"ATTACHMENT_READY: {str(payload.get('attachment_ready', False)).lower()}",
        f"UPLOAD_PROGRESS_RESOLVED: {str(payload.get('upload_progress_resolved', False)).lower()}",
        "CHATGPT_SUBMIT_PERFORMED: false",
        "CONVERSATION_TEXT_LOGGED: false",
        "SELENIUM_USED: false",
        "WEBDRIVER_USED: false",
        "BROWSER_DOM_AUTOMATION_USED: false",
        "RANDOM_PAGE_CLICK_PERFORMED: false",
        "",
    ]
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path
