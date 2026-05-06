from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.chatgpt_uploader.attachment_verifier import (
    AttachmentVerificationResult,
    wait_for_attachment_visible,
    write_attachment_verification_evidence,
)
from patchops.chatgpt_uploader.edge_session_recovery import EdgeRecoveryUploadResult, run_edge_recovery_then_type_path_enter_no_send


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class RecoverUploadVerifyResult:
    status: str
    reason: str
    report_path: str | None
    upload_status: str
    attachment_status: str
    upload_result: dict[str, Any] | None
    attachment_result: dict[str, Any] | None
    upload_json_evidence: str | None
    upload_txt_evidence: str | None
    attachment_json_evidence: str | None
    attachment_txt_evidence: str | None
    safety_flags: dict[str, bool]
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def verify_stage_safety_flags(*, upload: EdgeRecoveryUploadResult | None = None, attachment: AttachmentVerificationResult | None = None) -> dict[str, bool]:
    upload_flags = dict(upload.safety_flags) if upload is not None else {}
    attachment_flags = dict(attachment.safety_flags) if attachment is not None else {}
    return {
        "normal_edge_launch_attempted": bool(upload_flags.get("normal_edge_launch_attempted", False)),
        "configured_target_open_attempted": bool(upload_flags.get("configured_target_open_attempted", False)),
        "target_config_overwritten": False,
        "hardcoded_target_url_used": False,
        "canonical_picker_trigger_attempted": bool(upload_flags.get("canonical_picker_trigger_attempted", False)),
        "file_picker_open_attempted": bool(upload_flags.get("file_picker_open_attempted", False)),
        "safe_click_attempted": bool(upload_flags.get("safe_click_attempted", False)),
        "slash_sent": bool(upload_flags.get("slash_sent", False)),
        "tab_sent": False,
        "second_enter_attempted": False,
        "plus_control_search_attempted": False,
        "menu_control_search_attempted": False,
        "ctrl_u_attempted": False,
        "file_path_written": bool(upload_flags.get("file_path_written", False)),
        "picker_enter_pressed": bool(upload_flags.get("picker_enter_pressed", False)),
        "file_upload_attempted": bool(upload_flags.get("file_upload_attempted", False)),
        "attachment_verification_attempted": bool(attachment_flags.get("attachment_verification_attempted", False)),
        "attachment_visible": bool(attachment and attachment.status == "PASS_ATTACHMENT_VISIBLE_NO_SEND"),
        "open_button_clicked": False,
        "chatgpt_submit_performed": False,
        "conversation_text_logged": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
        "random_page_click_performed": False,
    }


def _result(
    *,
    status: str,
    reason: str,
    report_path: str | None,
    upload: EdgeRecoveryUploadResult | None = None,
    attachment: AttachmentVerificationResult | None = None,
    upload_json_evidence: str | None = None,
    upload_txt_evidence: str | None = None,
    attachment_json_evidence: str | None = None,
    attachment_txt_evidence: str | None = None,
) -> RecoverUploadVerifyResult:
    return RecoverUploadVerifyResult(
        status=status,
        reason=reason,
        report_path=report_path,
        upload_status=upload.status if upload else "NOT_RUN",
        attachment_status=attachment.status if attachment else "NOT_RUN",
        upload_result=upload.to_payload() if upload else None,
        attachment_result=attachment.to_payload() if attachment else None,
        upload_json_evidence=upload_json_evidence,
        upload_txt_evidence=upload_txt_evidence,
        attachment_json_evidence=attachment_json_evidence,
        attachment_txt_evidence=attachment_txt_evidence,
        safety_flags=verify_stage_safety_flags(upload=upload, attachment=attachment),
        created_at=utc_now_iso(),
    )


def run_recover_upload_verify_attachment_no_send(
    *,
    target_config_path: str | Path,
    report_path: str | Path,
    evidence_dir: str | Path,
    allow_launch_edge: bool,
    allow_open_picker: bool,
    launch_wait_seconds: float = 8.0,
    attachment_wait_seconds: float = 20.0,
    timeout_seconds: int = 10,
    safe_click_x_ratio: float = 0.50,
    safe_click_y_ratio: float = 0.34,
) -> RecoverUploadVerifyResult:
    evidence_root = Path(evidence_dir).expanduser().resolve()
    evidence_root.mkdir(parents=True, exist_ok=True)
    upload = run_edge_recovery_then_type_path_enter_no_send(
        target_config_path=target_config_path,
        report_path=report_path,
        evidence_dir=evidence_root,
        allow_launch_edge=bool(allow_launch_edge),
        allow_open_picker=bool(allow_open_picker),
        launch_wait_seconds=float(launch_wait_seconds),
        timeout_seconds=max(1, int(timeout_seconds)),
        safe_click_x_ratio=float(safe_click_x_ratio),
        safe_click_y_ratio=float(safe_click_y_ratio),
    )
    if upload.status != "PASS_UPLOAD_ATTEMPTED_PICKER_CLOSED_NO_SEND":
        return _result(
            status="BLOCKED_UPLOAD_NOT_PASS_NO_SEND",
            reason=f"upload stage did not pass: {upload.status}",
            report_path=upload.report_path or str(Path(report_path).expanduser().resolve()),
            upload=upload,
        )
    attachment = wait_for_attachment_visible(
        target_config_path=target_config_path,
        expected_report_path=report_path,
        wait_seconds=float(attachment_wait_seconds),
        focus_timeout_seconds=max(1, int(timeout_seconds)),
    )
    attachment_json, attachment_txt = write_attachment_verification_evidence(attachment, evidence_root)
    if attachment.status == "PASS_ATTACHMENT_VISIBLE_NO_SEND":
        return _result(
            status="PASS_ATTACHMENT_VERIFIED_NO_SEND",
            reason="upload stage passed and expected report filename is visible as an attachment; ChatGPT send not performed",
            report_path=upload.report_path,
            upload=upload,
            attachment=attachment,
            attachment_json_evidence=str(attachment_json),
            attachment_txt_evidence=str(attachment_txt),
        )
    return _result(
        status="FAIL_ATTACHMENT_NOT_VERIFIED_NO_SEND",
        reason=f"upload stage passed but attachment verification returned {attachment.status}",
        report_path=upload.report_path,
        upload=upload,
        attachment=attachment,
        attachment_json_evidence=str(attachment_json),
        attachment_txt_evidence=str(attachment_txt),
    )


def write_recover_upload_verify_evidence(result: RecoverUploadVerifyResult, evidence_dir: str | Path, *, basename: str = "u2_07_recover_upload_verify") -> tuple[Path, Path]:
    root = Path(evidence_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    safe_base = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in basename).strip("_") or "recover_upload_verify"
    json_path = root / f"{safe_base}.json"
    txt_path = root / f"{safe_base}.txt"
    json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "PATCHOPS CHATGPT UPLOADER RECOVER UPLOAD VERIFY NO SEND",
        "========================================================",
        f"Status                         : {result.status}",
        f"Reason                         : {result.reason}",
        f"ReportPath                     : {result.report_path or ''}",
        f"UploadStatus                   : {result.upload_status}",
        f"AttachmentStatus               : {result.attachment_status}",
        f"NormalEdgeLaunchAttempted      : {str(result.safety_flags['normal_edge_launch_attempted']).lower()}",
        f"CanonicalTriggerAttempted      : {str(result.safety_flags['canonical_picker_trigger_attempted']).lower()}",
        f"SlashSent                      : {str(result.safety_flags['slash_sent']).lower()}",
        f"TabSent                        : {str(result.safety_flags['tab_sent']).lower()}",
        f"SecondEnterAttempted           : {str(result.safety_flags['second_enter_attempted']).lower()}",
        f"PlusControlSearch              : {str(result.safety_flags['plus_control_search_attempted']).lower()}",
        f"MenuControlSearch              : {str(result.safety_flags['menu_control_search_attempted']).lower()}",
        f"CtrlUAttempted                 : {str(result.safety_flags['ctrl_u_attempted']).lower()}",
        f"FilePathWritten                : {str(result.safety_flags['file_path_written']).lower()}",
        f"PickerEnterPressed             : {str(result.safety_flags['picker_enter_pressed']).lower()}",
        f"FileUploadAttempted            : {str(result.safety_flags['file_upload_attempted']).lower()}",
        f"AttachmentVerificationAttempted: {str(result.safety_flags['attachment_verification_attempted']).lower()}",
        f"AttachmentVisible              : {str(result.safety_flags['attachment_visible']).lower()}",
        "OpenButtonClicked              : false",
        "ChatGPTSubmitPerformed         : false",
        "ConversationTextLogged         : false",
        "SeleniumUsed                   : false",
        "WebDriverUsed                  : false",
        "BrowserDomAutomation           : false",
        "RandomPageClick                : false",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path
