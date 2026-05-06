from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.chatgpt_uploader.canonical_picker_trigger import run_canonical_picker_trigger
from patchops.chatgpt_uploader.slash_enter_trigger import close_single_detected_picker
from patchops.chatgpt_uploader.windows_file_picker import detect_file_picker


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class CanonicalUploadEnterStageResult:
    status: str
    reason: str
    report_path: str | None
    trigger_status: str
    trigger_attempts_requested: int
    trigger_attempts_completed: int
    trigger_pass_count: int
    path_typed: bool
    picker_enter_pressed: bool
    picker_closed_after_enter: bool
    picker_cleanup_closed: bool
    trigger_json_evidence: str | None
    trigger_txt_evidence: str | None
    safety_flags: dict[str, bool]
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def upload_enter_stage_safety_flags(
    *,
    open_attempted: bool = False,
    path_typed: bool = False,
    picker_enter_pressed: bool = False,
) -> dict[str, bool]:
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
        "file_path_typed": bool(path_typed),
        "file_path_written": bool(path_typed),
        "picker_enter_pressed": bool(picker_enter_pressed),
        "file_upload_attempted": bool(picker_enter_pressed),
        "file_selected_or_confirmed_by_picker_enter": bool(picker_enter_pressed),
        "open_button_clicked": False,
        "attachment_confirmed": False,
        "chatgpt_submit_performed": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
        "random_page_click_performed": False,
        "conversation_text_logged": False,
        "clipboard_written": False,
        "paste_attempted": False,
    }


def _send_keys(keys: str) -> tuple[bool, str]:
    try:
        from pywinauto.keyboard import send_keys  # type: ignore
    except Exception as exc:
        return False, f"pywinauto.keyboard unavailable:{exc}"
    try:
        send_keys(keys, pause=0.03, with_spaces=True, vk_packet=True)
        return True, "send_keys"
    except Exception as exc:
        return False, f"send_keys_failed:{exc}"


def _result(
    *,
    status: str,
    reason: str,
    report_path: str | None,
    trigger_status: str = "NOT_RUN",
    trigger_attempts_requested: int = 0,
    trigger_attempts_completed: int = 0,
    trigger_pass_count: int = 0,
    path_typed: bool = False,
    picker_enter_pressed: bool = False,
    picker_closed_after_enter: bool = False,
    picker_cleanup_closed: bool = False,
    trigger_json_evidence: str | None = None,
    trigger_txt_evidence: str | None = None,
) -> CanonicalUploadEnterStageResult:
    return CanonicalUploadEnterStageResult(
        status=status,
        reason=reason,
        report_path=report_path,
        trigger_status=trigger_status,
        trigger_attempts_requested=int(trigger_attempts_requested),
        trigger_attempts_completed=int(trigger_attempts_completed),
        trigger_pass_count=int(trigger_pass_count),
        path_typed=bool(path_typed),
        picker_enter_pressed=bool(picker_enter_pressed),
        picker_closed_after_enter=bool(picker_closed_after_enter),
        picker_cleanup_closed=bool(picker_cleanup_closed),
        trigger_json_evidence=trigger_json_evidence,
        trigger_txt_evidence=trigger_txt_evidence,
        safety_flags=upload_enter_stage_safety_flags(
            open_attempted=trigger_attempts_requested > 0,
            path_typed=path_typed,
            picker_enter_pressed=picker_enter_pressed,
        ),
        created_at=utc_now_iso(),
    )


def cleanup_open_picker() -> bool:
    detection = detect_file_picker(wait_seconds=0)
    if detection.picker_detected and not detection.ambiguous:
        return close_single_detected_picker(detection)
    return False


def wait_for_picker_closed(*, wait_seconds: float = 8.0, poll_interval_seconds: float = 0.25) -> bool:
    deadline = time.monotonic() + max(0.0, float(wait_seconds))
    while True:
        detection = detect_file_picker(wait_seconds=0)
        if not detection.picker_detected:
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(max(0.05, float(poll_interval_seconds)))


def type_path_and_press_enter(report_path: str | Path) -> tuple[bool, bool, str]:
    report_str = str(Path(report_path).expanduser().resolve())
    ok, type_reason = _send_keys(report_str)
    if not ok:
        return False, False, f"type_path:{type_reason}"
    time.sleep(0.20)
    ok, enter_reason = _send_keys("{ENTER}")
    if not ok:
        return True, False, f"type_path:{type_reason};enter:{enter_reason}"
    return True, True, f"type_path:{type_reason};enter:{enter_reason}"


def run_canonical_type_path_enter_no_send(
    *,
    target_config_path: str | Path,
    report_path: str | Path,
    evidence_dir: str | Path,
    allow_open_picker: bool,
    timeout_seconds: int = 10,
    safe_click_x_ratio: float = 0.50,
    safe_click_y_ratio: float = 0.34,
) -> CanonicalUploadEnterStageResult:
    report_str = str(Path(report_path).expanduser().resolve())
    if not allow_open_picker:
        return _result(
            status="PASS_DRY_RUN_NO_PICKER_OPEN",
            reason="--allow-open-picker not provided; no picker opened, no path typed, no upload attempted",
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
        evidence_basename="u2_06_trigger_left_open_for_type_enter",
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

    path_typed, enter_pressed, write_reason = type_path_and_press_enter(report_str)
    if not path_typed:
        cleanup_closed = cleanup_open_picker()
        return _result(
            status="FAIL_PATH_NOT_TYPED",
            reason=write_reason,
            report_path=report_str,
            trigger_status=trigger_run.status,
            trigger_attempts_requested=trigger_run.attempts_requested,
            trigger_attempts_completed=trigger_run.attempts_completed,
            trigger_pass_count=trigger_run.pass_count,
            path_typed=False,
            picker_enter_pressed=False,
            picker_cleanup_closed=cleanup_closed,
            trigger_json_evidence=str(trigger_json),
            trigger_txt_evidence=str(trigger_txt),
        )
    if not enter_pressed:
        cleanup_closed = cleanup_open_picker()
        return _result(
            status="FAIL_PICKER_ENTER_NOT_PRESSED",
            reason=write_reason,
            report_path=report_str,
            trigger_status=trigger_run.status,
            trigger_attempts_requested=trigger_run.attempts_requested,
            trigger_attempts_completed=trigger_run.attempts_completed,
            trigger_pass_count=trigger_run.pass_count,
            path_typed=True,
            picker_enter_pressed=False,
            picker_cleanup_closed=cleanup_closed,
            trigger_json_evidence=str(trigger_json),
            trigger_txt_evidence=str(trigger_txt),
        )

    picker_closed = wait_for_picker_closed(wait_seconds=8.0, poll_interval_seconds=0.25)
    cleanup_closed = False if picker_closed else cleanup_open_picker()
    if picker_closed:
        return _result(
            status="PASS_UPLOAD_ATTEMPTED_PICKER_CLOSED_NO_SEND",
            reason=write_reason + ";picker closed after Enter; ChatGPT send not performed",
            report_path=report_str,
            trigger_status=trigger_run.status,
            trigger_attempts_requested=trigger_run.attempts_requested,
            trigger_attempts_completed=trigger_run.attempts_completed,
            trigger_pass_count=trigger_run.pass_count,
            path_typed=True,
            picker_enter_pressed=True,
            picker_closed_after_enter=True,
            picker_cleanup_closed=cleanup_closed,
            trigger_json_evidence=str(trigger_json),
            trigger_txt_evidence=str(trigger_txt),
        )
    return _result(
        status="FAIL_PICKER_STILL_OPEN_AFTER_ENTER",
        reason=write_reason + ";picker did not close after Enter",
        report_path=report_str,
        trigger_status=trigger_run.status,
        trigger_attempts_requested=trigger_run.attempts_requested,
        trigger_attempts_completed=trigger_run.attempts_completed,
        trigger_pass_count=trigger_run.pass_count,
        path_typed=True,
        picker_enter_pressed=True,
        picker_closed_after_enter=False,
        picker_cleanup_closed=cleanup_closed,
        trigger_json_evidence=str(trigger_json),
        trigger_txt_evidence=str(trigger_txt),
    )


def write_upload_enter_stage_evidence(result: CanonicalUploadEnterStageResult, evidence_dir: str | Path, *, basename: str = "u2_06_type_path_enter_no_send") -> tuple[Path, Path]:
    root = Path(evidence_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    safe_base = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in basename).strip("_") or "type_path_enter_no_send"
    json_path = root / f"{safe_base}.json"
    txt_path = root / f"{safe_base}.txt"
    payload = result.to_payload()
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "PATCHOPS CHATGPT UPLOADER TYPE PATH ENTER NO SEND",
        "=================================================",
        f"Status                 : {result.status}",
        f"Reason                 : {result.reason}",
        f"ReportPath             : {result.report_path or ''}",
        f"TriggerStatus          : {result.trigger_status}",
        f"TriggerAttempts        : {result.trigger_attempts_requested}",
        f"TriggerPassCount       : {result.trigger_pass_count}",
        f"PathTyped              : {str(result.path_typed).lower()}",
        f"PickerEnterPressed     : {str(result.picker_enter_pressed).lower()}",
        f"PickerClosedAfterEnter : {str(result.picker_closed_after_enter).lower()}",
        f"PickerCleanupClosed    : {str(result.picker_cleanup_closed).lower()}",
        f"CanonicalTrigger       : {str(result.safety_flags['canonical_picker_trigger_attempted']).lower()}",
        f"SlashSent              : {str(result.safety_flags['slash_sent']).lower()}",
        f"TabSent                : {str(result.safety_flags['tab_sent']).lower()}",
        f"SecondEnterAttempted   : {str(result.safety_flags['second_enter_attempted']).lower()}",
        f"PlusControlSearch      : {str(result.safety_flags['plus_control_search_attempted']).lower()}",
        f"MenuControlSearch      : {str(result.safety_flags['menu_control_search_attempted']).lower()}",
        f"CtrlUAttempted         : {str(result.safety_flags['ctrl_u_attempted']).lower()}",
        f"FilePathWritten        : {str(result.safety_flags['file_path_written']).lower()}",
        f"FileUploadAttempted    : {str(result.safety_flags['file_upload_attempted']).lower()}",
        f"FileSelectedByEnter    : {str(result.safety_flags['file_selected_or_confirmed_by_picker_enter']).lower()}",
        "OpenButtonClicked      : false",
        "AttachmentConfirmed    : false",
        "ChatGPTSubmitPerformed : false",
        "SeleniumUsed           : false",
        "WebDriverUsed          : false",
        "BrowserDomAutomation   : false",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path
