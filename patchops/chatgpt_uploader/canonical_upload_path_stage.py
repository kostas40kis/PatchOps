from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.chatgpt_uploader.canonical_picker_trigger import run_canonical_picker_trigger
from patchops.chatgpt_uploader.picker_path_writer import PickerPathWriteResult, write_report_path_to_detected_picker
from patchops.chatgpt_uploader.slash_enter_trigger import close_single_detected_picker
from patchops.chatgpt_uploader.windows_file_picker import detect_file_picker


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class CanonicalUploadPathStageResult:
    status: str
    reason: str
    report_path: str | None
    trigger_status: str
    trigger_attempts_requested: int
    trigger_attempts_completed: int
    trigger_pass_count: int
    path_write_status: str
    path_written: bool
    picker_cleanup_closed: bool
    trigger_json_evidence: str | None
    trigger_txt_evidence: str | None
    safety_flags: dict[str, bool]
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def upload_path_stage_safety_flags(*, open_attempted: bool = False, path_written: bool = False) -> dict[str, bool]:
    return {
        "canonical_picker_trigger_attempted": bool(open_attempted),
        "file_picker_open_attempted": bool(open_attempted),
        "safe_click_attempted": bool(open_attempted),
        "slash_sent": bool(open_attempted),
        "tab_sent": False,
        "second_enter_attempted": False,
        "plus_control_search_attempted": False,
        "menu_control_search_attempted": False,
        "ctrl_u_attempted": False,
        "file_path_written": bool(path_written),
        "file_selected": False,
        "open_button_pressed": False,
        "attachment_confirmed": False,
        "file_upload_attempted": False,
        "chatgpt_submit_performed": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
        "random_page_click_performed": False,
        "conversation_text_logged": False,
        "clipboard_written": False,
        "paste_attempted": False,
    }


def _result(
    *,
    status: str,
    reason: str,
    report_path: str | None,
    trigger_status: str = "NOT_RUN",
    trigger_attempts_requested: int = 0,
    trigger_attempts_completed: int = 0,
    trigger_pass_count: int = 0,
    path_write_status: str = "NOT_RUN",
    path_written: bool = False,
    picker_cleanup_closed: bool = False,
    trigger_json_evidence: str | None = None,
    trigger_txt_evidence: str | None = None,
) -> CanonicalUploadPathStageResult:
    return CanonicalUploadPathStageResult(
        status=status,
        reason=reason,
        report_path=report_path,
        trigger_status=trigger_status,
        trigger_attempts_requested=int(trigger_attempts_requested),
        trigger_attempts_completed=int(trigger_attempts_completed),
        trigger_pass_count=int(trigger_pass_count),
        path_write_status=path_write_status,
        path_written=bool(path_written),
        picker_cleanup_closed=bool(picker_cleanup_closed),
        trigger_json_evidence=trigger_json_evidence,
        trigger_txt_evidence=trigger_txt_evidence,
        safety_flags=upload_path_stage_safety_flags(open_attempted=trigger_attempts_requested > 0, path_written=path_written),
        created_at=utc_now_iso(),
    )


def cleanup_open_picker() -> bool:
    detection = detect_file_picker(wait_seconds=0)
    if detection.picker_detected and not detection.ambiguous:
        return close_single_detected_picker(detection)
    return False


def run_canonical_open_write_path_no_open(
    *,
    target_config_path: str | Path,
    report_path: str | Path,
    evidence_dir: str | Path,
    allow_open_picker: bool,
    timeout_seconds: int = 10,
    safe_click_x_ratio: float = 0.50,
    safe_click_y_ratio: float = 0.34,
) -> CanonicalUploadPathStageResult:
    report_str = str(Path(report_path).expanduser())
    if not allow_open_picker:
        return _result(
            status="PASS_DRY_RUN_NO_PICKER_OPEN",
            reason="--allow-open-picker not provided; no picker opened and no path written",
            report_path=report_str,
        )

    trigger_run, trigger_json, trigger_txt = run_canonical_picker_trigger(
        target_config_path=target_config_path,
        evidence_dir=evidence_dir,
        allow_open_picker=True,
        timeout_seconds=max(1, int(timeout_seconds)),
        safe_click_x_ratio=float(safe_click_x_ratio),
        safe_click_y_ratio=float(safe_click_y_ratio),
        close_picker_on_detect=False,
        evidence_basename="u2_05_trigger_left_open_for_path_write",
    )
    if trigger_run.status != "PASS":
        cleanup_open_picker()
        return _result(
            status="BLOCKED_TRIGGER_NOT_PASS",
            reason=f"canonical trigger did not pass: {trigger_run.status}",
            report_path=report_str,
            trigger_status=trigger_run.status,
            trigger_attempts_requested=trigger_run.attempts_requested,
            trigger_attempts_completed=trigger_run.attempts_completed,
            trigger_pass_count=trigger_run.pass_count,
            trigger_json_evidence=str(trigger_json),
            trigger_txt_evidence=str(trigger_txt),
        )

    path_result: PickerPathWriteResult = write_report_path_to_detected_picker(report_path=report_path, wait_seconds=1.0)
    cleanup_closed = cleanup_open_picker()
    if path_result.status == "PASS_PATH_WRITTEN_NO_OPEN" and path_result.wrote_path:
        return _result(
            status="PASS_PATH_WRITTEN_NO_OPEN",
            reason="canonical picker opened, exact report path written, Open not pressed, picker cleaned up",
            report_path=path_result.report_path or report_str,
            trigger_status=trigger_run.status,
            trigger_attempts_requested=trigger_run.attempts_requested,
            trigger_attempts_completed=trigger_run.attempts_completed,
            trigger_pass_count=trigger_run.pass_count,
            path_write_status=path_result.status,
            path_written=True,
            picker_cleanup_closed=cleanup_closed,
            trigger_json_evidence=str(trigger_json),
            trigger_txt_evidence=str(trigger_txt),
        )
    return _result(
        status="FAIL_OR_BLOCKED_PATH_NOT_WRITTEN",
        reason=f"path writer returned {path_result.status}: {path_result.reason}",
        report_path=path_result.report_path or report_str,
        trigger_status=trigger_run.status,
        trigger_attempts_requested=trigger_run.attempts_requested,
        trigger_attempts_completed=trigger_run.attempts_completed,
        trigger_pass_count=trigger_run.pass_count,
        path_write_status=path_result.status,
        path_written=bool(path_result.wrote_path),
        picker_cleanup_closed=cleanup_closed,
        trigger_json_evidence=str(trigger_json),
        trigger_txt_evidence=str(trigger_txt),
    )


def write_upload_path_stage_evidence(result: CanonicalUploadPathStageResult, evidence_dir: str | Path, *, basename: str = "u2_05_open_write_path_no_open") -> tuple[Path, Path]:
    root = Path(evidence_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    safe_base = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in basename).strip("_") or "open_write_path_no_open"
    json_path = root / f"{safe_base}.json"
    txt_path = root / f"{safe_base}.txt"
    payload = result.to_payload()
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "PATCHOPS CHATGPT UPLOADER CANONICAL OPEN WRITE PATH NO OPEN",
        "============================================================",
        f"Status                 : {result.status}",
        f"Reason                 : {result.reason}",
        f"ReportPath             : {result.report_path or ''}",
        f"TriggerStatus          : {result.trigger_status}",
        f"TriggerAttempts        : {result.trigger_attempts_requested}",
        f"TriggerPassCount       : {result.trigger_pass_count}",
        f"PathWriteStatus        : {result.path_write_status}",
        f"PathWritten            : {str(result.path_written).lower()}",
        f"PickerCleanupClosed    : {str(result.picker_cleanup_closed).lower()}",
        f"CanonicalTrigger       : {str(result.safety_flags['canonical_picker_trigger_attempted']).lower()}",
        f"SlashSent              : {str(result.safety_flags['slash_sent']).lower()}",
        f"TabSent                : {str(result.safety_flags['tab_sent']).lower()}",
        f"SecondEnterAttempted   : {str(result.safety_flags['second_enter_attempted']).lower()}",
        f"PlusControlSearch      : {str(result.safety_flags['plus_control_search_attempted']).lower()}",
        f"MenuControlSearch      : {str(result.safety_flags['menu_control_search_attempted']).lower()}",
        f"CtrlUAttempted         : {str(result.safety_flags['ctrl_u_attempted']).lower()}",
        "FileSelected           : false",
        "OpenButtonPressed      : false",
        "AttachmentConfirmed    : false",
        "FileUploadAttempted    : false",
        "ChatGPTSubmitPerformed : false",
        "SeleniumUsed           : false",
        "WebDriverUsed          : false",
        "BrowserDomAutomation   : false",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path
