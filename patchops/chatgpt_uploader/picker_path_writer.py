from __future__ import annotations

import ctypes
from ctypes import wintypes
import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.chatgpt_uploader.report_resolver import ReportResolutionError, resolve_report
from patchops.chatgpt_uploader.windows_file_picker import PickerDetection, detect_file_picker, write_detection_evidence

WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E

EDIT_LIKE_CLASSES = {"edit", "combobox", "comboboxex32"}


class PickerPathWriteError(RuntimeError):
    pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


@dataclass(frozen=True)
class PickerPathWriteResult:
    status: str
    reason: str
    report_path: str | None
    report_name: str | None
    report_sha256: str | None
    picker_detected: bool
    picker_count: int
    error_modal_detected: bool
    ambiguous: bool
    picker_handle: int | None
    target_control_handle: int | None
    target_control_class: str | None
    wrote_path: bool
    verified_control_text_hash: str | None
    safety_flags: dict[str, bool]
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def default_path_write_safety_flags(*, wrote_path: bool) -> dict[str, bool]:
    return {
        "file_picker_open_attempted": False,
        "file_path_written": bool(wrote_path),
        "file_selected": False,
        "open_button_pressed": False,
        "file_upload_attempted": False,
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


def _get_class_name(hwnd: int) -> str:
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        buffer = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(int(hwnd), buffer, 256)
        return buffer.value or ""
    except Exception:
        return ""


def _get_text(hwnd: int) -> str:
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        length = int(user32.SendMessageW(int(hwnd), WM_GETTEXTLENGTH, 0, 0))
        buffer = ctypes.create_unicode_buffer(max(length + 1, 2))
        user32.SendMessageW(int(hwnd), WM_GETTEXT, len(buffer), buffer)
        return buffer.value or ""
    except Exception:
        return ""


def _set_text(hwnd: int, text: str) -> bool:
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        result = user32.SendMessageW(int(hwnd), WM_SETTEXT, 0, ctypes.c_wchar_p(text))
        return bool(result)
    except Exception:
        return False


def _visible_enabled(hwnd: int) -> bool:
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        return bool(user32.IsWindowVisible(int(hwnd))) and bool(user32.IsWindowEnabled(int(hwnd)))
    except Exception:
        return False


def child_windows(parent_hwnd: int) -> list[int]:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    EnumChildProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    handles: list[int] = []

    def callback(hwnd: int, lparam: int) -> bool:
        handles.append(int(hwnd))
        return True

    try:
        user32.EnumChildWindows(int(parent_hwnd), EnumChildProc(callback), 0)
    except Exception:
        pass
    return handles


def find_filename_control_handle(picker_handle: int) -> tuple[int | None, str | None]:
    """Find a likely File name field inside an already-open Windows picker.

    Preference is Edit-like controls with the broadest standard compatibility. This
    does not use global keyboard shortcuts and does not click outside the picker.
    """
    edit_like: list[tuple[int, str]] = []
    for hwnd in child_windows(picker_handle):
        cls = _get_class_name(hwnd)
        if cls.lower() in EDIT_LIKE_CLASSES and _visible_enabled(hwnd):
            edit_like.append((hwnd, cls))
    if not edit_like:
        return None, None
    # In common file dialogs the filename Edit/ComboBox is among the last edit-like controls.
    hwnd, cls = edit_like[-1]
    return hwnd, cls


def _result(
    *,
    status: str,
    reason: str,
    detection: PickerDetection,
    report_path: str | None = None,
    report_name: str | None = None,
    report_sha256: str | None = None,
    picker_handle: int | None = None,
    target_control_handle: int | None = None,
    target_control_class: str | None = None,
    wrote_path: bool = False,
    verified_text: str | None = None,
) -> PickerPathWriteResult:
    return PickerPathWriteResult(
        status=status,
        reason=reason,
        report_path=report_path,
        report_name=report_name,
        report_sha256=report_sha256,
        picker_detected=detection.picker_detected,
        picker_count=detection.picker_count,
        error_modal_detected=detection.error_modal_detected,
        ambiguous=detection.ambiguous,
        picker_handle=picker_handle,
        target_control_handle=target_control_handle,
        target_control_class=target_control_class,
        wrote_path=bool(wrote_path),
        verified_control_text_hash=sha256_text(verified_text) if verified_text is not None else None,
        safety_flags=default_path_write_safety_flags(wrote_path=wrote_path),
        created_at=utc_now_iso(),
    )


def write_report_path_to_detected_picker(*, report_path: str | Path, wait_seconds: float = 0.0) -> PickerPathWriteResult:
    try:
        resolved = resolve_report(report_path=report_path)
    except ReportResolutionError as exc:
        empty_detection = detect_file_picker(wait_seconds=0)
        return _result(status="FAIL_REPORT_NOT_RESOLVED", reason=str(exc), detection=empty_detection)

    detection = detect_file_picker(wait_seconds=max(0.0, wait_seconds))
    if detection.ambiguous:
        return _result(
            status="BLOCKED_AMBIGUOUS_PICKERS",
            reason="multiple_file_picker_candidates",
            detection=detection,
            report_path=resolved.path,
            report_name=resolved.name,
            report_sha256=resolved.sha256,
        )
    if not detection.picker_detected:
        status = "PASS_NO_PICKER_NO_WRITE" if not detection.error_modal_detected else "PASS_ERROR_MODAL_NO_WRITE"
        return _result(
            status=status,
            reason=detection.reason,
            detection=detection,
            report_path=resolved.path,
            report_name=resolved.name,
            report_sha256=resolved.sha256,
        )
    picker = detection.selected_picker or {}
    picker_handle = picker.get("handle")
    if picker_handle is None:
        return _result(
            status="FAIL_PICKER_HANDLE_MISSING",
            reason="selected picker did not include a handle",
            detection=detection,
            report_path=resolved.path,
            report_name=resolved.name,
            report_sha256=resolved.sha256,
        )
    control_handle, control_class = find_filename_control_handle(int(picker_handle))
    if control_handle is None:
        return _result(
            status="FAIL_FILENAME_CONTROL_NOT_FOUND",
            reason="no visible enabled edit-like filename control found",
            detection=detection,
            report_path=resolved.path,
            report_name=resolved.name,
            report_sha256=resolved.sha256,
            picker_handle=int(picker_handle),
        )

    ok = _set_text(int(control_handle), resolved.path)
    time.sleep(0.15)
    verified = _get_text(int(control_handle))
    if not ok or verified != resolved.path:
        return _result(
            status="FAIL_PATH_WRITE_NOT_VERIFIED",
            reason="WM_SETTEXT failed or control text did not match the exact report path",
            detection=detection,
            report_path=resolved.path,
            report_name=resolved.name,
            report_sha256=resolved.sha256,
            picker_handle=int(picker_handle),
            target_control_handle=int(control_handle),
            target_control_class=control_class,
            wrote_path=False,
            verified_text=verified,
        )

    return _result(
        status="PASS_PATH_WRITTEN_NO_OPEN",
        reason="exact report path written to picker filename field; Open not pressed",
        detection=detection,
        report_path=resolved.path,
        report_name=resolved.name,
        report_sha256=resolved.sha256,
        picker_handle=int(picker_handle),
        target_control_handle=int(control_handle),
        target_control_class=control_class,
        wrote_path=True,
        verified_text=verified,
    )


def write_path_writer_evidence(result: PickerPathWriteResult, evidence_dir: str | Path, *, basename: str = "u2_03_picker_path_writer") -> tuple[Path, Path]:
    root = Path(evidence_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    safe_base = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in basename).strip("_") or "picker_path_writer"
    json_path = root / f"{safe_base}.json"
    txt_path = root / f"{safe_base}.txt"
    payload = result.to_payload()
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "PATCHOPS CHATGPT UPLOADER PICKER PATH WRITER",
        "================================================",
        f"Status                 : {result.status}",
        f"Reason                 : {result.reason}",
        f"ReportPath             : {result.report_path or ''}",
        f"ReportName             : {result.report_name or ''}",
        f"ReportSha256           : {result.report_sha256 or ''}",
        f"PickerDetected         : {str(result.picker_detected).lower()}",
        f"PickerCount            : {result.picker_count}",
        f"Ambiguous              : {str(result.ambiguous).lower()}",
        f"PathWritten            : {str(result.wrote_path).lower()}",
        "OpenButtonPressed      : false",
        "FileSelected           : false",
        "FileUploadAttempted    : false",
        "AttachmentConfirmed    : false",
        "ChatGPTSubmitPerformed : false",
        "ClipboardWritten       : false",
        "PasteAttempted         : false",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path
