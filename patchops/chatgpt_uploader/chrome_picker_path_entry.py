from __future__ import annotations

import ctypes
import hashlib
import json
from ctypes import wintypes
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PASS_PICKER_PATH_ENTRY_PLAN_READY = "PASS_PICKER_PATH_ENTRY_PLAN_READY"
PASS_PICKER_PATH_WRITTEN_NO_OPEN = "PASS_PICKER_PATH_WRITTEN_NO_OPEN"
BLOCKED_CANONICAL_REPORT_MISSING = "BLOCKED_CANONICAL_REPORT_MISSING"
BLOCKED_PATH_NOT_CANONICAL_REPORT = "BLOCKED_PATH_NOT_CANONICAL_REPORT"
BLOCKED_PICKER_NOT_READY = "BLOCKED_PICKER_NOT_READY"
BLOCKED_PATH_ENTRY_CONFIRMATION_MISSING = "BLOCKED_PATH_ENTRY_CONFIRMATION_MISSING"
BLOCKED_PICKER_EDIT_FIELD_NOT_FOUND = "BLOCKED_PICKER_EDIT_FIELD_NOT_FOUND"
FAIL_PICKER_PATH_WRITE_FAILED = "FAIL_PICKER_PATH_WRITE_FAILED"

LIVE_CONFIRM_TEXT = "PATCHOPS_CONFIRM_PICKER_PATH_WRITE"
EXPECTED_BROWSER = "chrome"
REPORT_MARKERS = (
    "PatchOps operator report",
    "PATCHOPS APPLY",
    "PATCHOPS RUN SUMMARY",
)

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
    "file_upload_attempted": False,
    "file_path_written": False,
    "open_button_pressed": False,
    "enter_pressed": False,
    "file_selected": False,
    "attachment_confirmed": False,
    "live_browser_used": False,
}


@dataclass(frozen=True)
class CanonicalReportPathEvidence:
    ok: bool
    result: str
    path_hash: str | None
    basename: str | None
    suffix: str | None
    exists: bool
    is_file: bool
    size_bytes: int | None
    marker_detected: bool
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PickerPathEntryPlan:
    ok: bool
    result: str
    expected_browser: str
    canonical_report: dict[str, Any]
    sequence: tuple[str, ...]
    max_attempts: int
    allow_path_write: bool
    allow_open_press: bool
    allow_enter_press: bool
    allow_upload_claim: bool
    allow_send: bool
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PickerPathEntryEvidence:
    ok: bool
    result: str
    expected_browser: str
    live_browser_used: bool
    picker_ready: bool
    picker_hwnd: int | None
    filename_edit_hwnd: int | None
    canonical_report: dict[str, Any]
    path_entry_plan: dict[str, Any]
    path_hash_written: str | None
    basename_written: str | None
    file_path_written: bool
    open_button_pressed: bool
    enter_pressed: bool
    file_selected: bool
    file_upload_attempted: bool
    chatgpt_submit_performed: bool
    raw_conversation_text_logged: bool
    safety_flags: dict[str, bool]
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def hash_path(path: Path | str) -> str:
    return hashlib.sha256(str(Path(path).expanduser().resolve()).encode("utf-8")).hexdigest()


def validate_canonical_report_path(path: Path | str) -> CanonicalReportPathEvidence:
    candidate = Path(path).expanduser()
    try:
        resolved = candidate.resolve(strict=False)
    except OSError:
        return CanonicalReportPathEvidence(False, BLOCKED_PATH_NOT_CANONICAL_REPORT, None, candidate.name or None, candidate.suffix or None, False, False, None, False, "report path could not be resolved")

    exists = resolved.exists()
    is_file = resolved.is_file() if exists else False
    size_bytes = resolved.stat().st_size if is_file else None
    suffix = resolved.suffix.lower()
    path_digest = hash_path(resolved) if exists else None
    marker_detected = False

    if not exists:
        return CanonicalReportPathEvidence(False, BLOCKED_CANONICAL_REPORT_MISSING, path_digest, resolved.name, suffix, False, False, None, False, "canonical report path does not exist")
    if not is_file:
        return CanonicalReportPathEvidence(False, BLOCKED_PATH_NOT_CANONICAL_REPORT, path_digest, resolved.name, suffix, True, False, None, False, "canonical report path is not a file")
    if suffix != ".txt":
        return CanonicalReportPathEvidence(False, BLOCKED_PATH_NOT_CANONICAL_REPORT, path_digest, resolved.name, suffix, True, True, size_bytes, False, "canonical report must be a .txt report")

    sample = resolved.read_text(encoding="utf-8", errors="replace")[:65536]
    marker_detected = any(marker in sample for marker in REPORT_MARKERS)
    if not marker_detected:
        return CanonicalReportPathEvidence(False, BLOCKED_PATH_NOT_CANONICAL_REPORT, path_digest, resolved.name, suffix, True, True, size_bytes, False, "canonical report markers were not detected")

    return CanonicalReportPathEvidence(True, "PASS_CANONICAL_REPORT_PATH_VALIDATED", path_digest, resolved.name, suffix, True, True, size_bytes, True, "canonical PatchOps text report validated")


def build_picker_path_entry_plan(canonical_report_path: Path | str) -> PickerPathEntryPlan:
    report = validate_canonical_report_path(canonical_report_path)
    if not report.ok:
        return PickerPathEntryPlan(
            ok=False,
            result=report.result,
            expected_browser=EXPECTED_BROWSER,
            canonical_report=report.to_payload(),
            sequence=(),
            max_attempts=0,
            allow_path_write=False,
            allow_open_press=False,
            allow_enter_press=False,
            allow_upload_claim=False,
            allow_send=False,
            reason=report.reason,
        )
    return PickerPathEntryPlan(
        ok=True,
        result=PASS_PICKER_PATH_ENTRY_PLAN_READY,
        expected_browser=EXPECTED_BROWSER,
        canonical_report=report.to_payload(),
        sequence=("validate_canonical_report_path", "focus_confirmed_picker_filename_field", "write_exact_path_once", "verify_field_text_hash", "stop_before_open"),
        max_attempts=1,
        allow_path_write=True,
        allow_open_press=False,
        allow_enter_press=False,
        allow_upload_claim=False,
        allow_send=False,
        reason="Path entry plan validated; stops before Open/Enter, upload, or send.",
    )


def _blocked_evidence(*, result: str, plan: PickerPathEntryPlan, reason: str, picker_ready: bool = False, picker_hwnd: int | None = None, live_browser_used: bool = False) -> PickerPathEntryEvidence:
    safety = dict(SAFETY_FLAGS)
    safety["live_browser_used"] = bool(live_browser_used)
    return PickerPathEntryEvidence(
        ok=False,
        result=result,
        expected_browser=EXPECTED_BROWSER,
        live_browser_used=bool(live_browser_used),
        picker_ready=bool(picker_ready),
        picker_hwnd=picker_hwnd,
        filename_edit_hwnd=None,
        canonical_report=plan.canonical_report,
        path_entry_plan=plan.to_payload(),
        path_hash_written=None,
        basename_written=None,
        file_path_written=False,
        open_button_pressed=False,
        enter_pressed=False,
        file_selected=False,
        file_upload_attempted=False,
        chatgpt_submit_performed=False,
        raw_conversation_text_logged=False,
        safety_flags=safety,
        reason=reason,
    )


def _class_name(hwnd: int) -> str:
    buffer = ctypes.create_unicode_buffer(256)
    ctypes.windll.user32.GetClassNameW(int(hwnd), buffer, 256)
    return buffer.value or ""


def find_filename_edit_handle(picker_hwnd: int) -> int | None:
    user32 = ctypes.windll.user32
    found: list[int] = []
    enum_child_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def callback(hwnd: int, _lparam: int) -> bool:
        try:
            if _class_name(hwnd).lower() == "edit" and user32.IsWindowVisible(hwnd) and user32.IsWindowEnabled(hwnd):
                found.append(int(hwnd))
                return False
        except Exception:
            return True
        return True

    user32.EnumChildWindows(int(picker_hwnd), enum_child_proc(callback), 0)
    return found[0] if found else None


def write_exact_path_to_picker_field(*, picker_hwnd: int, exact_path: Path | str) -> tuple[bool, int | None]:
    edit_hwnd = find_filename_edit_handle(int(picker_hwnd))
    if edit_hwnd is None:
        return False, None
    user32 = ctypes.windll.user32
    WM_SETTEXT = 0x000C
    resolved = str(Path(exact_path).expanduser().resolve())
    result = user32.SendMessageW(int(edit_hwnd), WM_SETTEXT, 0, resolved)
    return bool(result), int(edit_hwnd)


def run_picker_path_entry(
    *,
    canonical_report_path: Path | str,
    picker_ready: bool = False,
    picker_hwnd: int | None = None,
    live_browser: bool = False,
    confirm_live_browser_text: str | None = None,
    allow_picker_path_write: bool = False,
    mock_write_success: bool = False,
) -> PickerPathEntryEvidence:
    plan = build_picker_path_entry_plan(canonical_report_path)
    if not plan.ok:
        return _blocked_evidence(result=plan.result, plan=plan, reason=plan.reason, picker_ready=picker_ready, picker_hwnd=picker_hwnd, live_browser_used=False)

    if not picker_ready:
        return _blocked_evidence(result=BLOCKED_PICKER_NOT_READY, plan=plan, reason="Picker must be confirmed ready before path entry.", picker_ready=False, picker_hwnd=picker_hwnd, live_browser_used=False)

    resolved = Path(canonical_report_path).expanduser().resolve()
    path_digest = hash_path(resolved)
    basename = resolved.name
    safety = dict(SAFETY_FLAGS)

    if live_browser:
        if confirm_live_browser_text != LIVE_CONFIRM_TEXT or not allow_picker_path_write:
            return _blocked_evidence(
                result=BLOCKED_PATH_ENTRY_CONFIRMATION_MISSING,
                plan=plan,
                reason=f"Live path entry requires --allow-picker-path-write and --confirm-live-browser-text {LIVE_CONFIRM_TEXT}.",
                picker_ready=True,
                picker_hwnd=picker_hwnd,
                live_browser_used=False,
            )
        if picker_hwnd is None:
            return _blocked_evidence(result=BLOCKED_PICKER_NOT_READY, plan=plan, reason="Live path entry requires picker_hwnd.", picker_ready=True, picker_hwnd=None, live_browser_used=False)
        success, edit_hwnd = write_exact_path_to_picker_field(picker_hwnd=int(picker_hwnd), exact_path=resolved)
        if not success:
            return _blocked_evidence(result=BLOCKED_PICKER_EDIT_FIELD_NOT_FOUND, plan=plan, reason="Could not locate or write to picker filename edit field.", picker_ready=True, picker_hwnd=picker_hwnd, live_browser_used=True)
        safety["live_browser_used"] = True
        safety["file_path_written"] = True
        return PickerPathEntryEvidence(
            ok=True,
            result=PASS_PICKER_PATH_WRITTEN_NO_OPEN,
            expected_browser=EXPECTED_BROWSER,
            live_browser_used=True,
            picker_ready=True,
            picker_hwnd=picker_hwnd,
            filename_edit_hwnd=edit_hwnd,
            canonical_report=plan.canonical_report,
            path_entry_plan=plan.to_payload(),
            path_hash_written=path_digest,
            basename_written=basename,
            file_path_written=True,
            open_button_pressed=False,
            enter_pressed=False,
            file_selected=False,
            file_upload_attempted=False,
            chatgpt_submit_performed=False,
            raw_conversation_text_logged=False,
            safety_flags=safety,
            reason="Exact canonical report path written to picker field; stopped before Open/Enter, upload, or send.",
        )

    if mock_write_success:
        safety["file_path_written"] = True
        return PickerPathEntryEvidence(
            ok=True,
            result=PASS_PICKER_PATH_WRITTEN_NO_OPEN,
            expected_browser=EXPECTED_BROWSER,
            live_browser_used=False,
            picker_ready=True,
            picker_hwnd=picker_hwnd,
            filename_edit_hwnd=999001,
            canonical_report=plan.canonical_report,
            path_entry_plan=plan.to_payload(),
            path_hash_written=path_digest,
            basename_written=basename,
            file_path_written=True,
            open_button_pressed=False,
            enter_pressed=False,
            file_selected=False,
            file_upload_attempted=False,
            chatgpt_submit_performed=False,
            raw_conversation_text_logged=False,
            safety_flags=safety,
            reason="Mock path entry succeeded; no live UI action was performed.",
        )

    return PickerPathEntryEvidence(
        ok=True,
        result=PASS_PICKER_PATH_ENTRY_PLAN_READY,
        expected_browser=EXPECTED_BROWSER,
        live_browser_used=False,
        picker_ready=True,
        picker_hwnd=picker_hwnd,
        filename_edit_hwnd=None,
        canonical_report=plan.canonical_report,
        path_entry_plan=plan.to_payload(),
        path_hash_written=None,
        basename_written=None,
        file_path_written=False,
        open_button_pressed=False,
        enter_pressed=False,
        file_selected=False,
        file_upload_attempted=False,
        chatgpt_submit_performed=False,
        raw_conversation_text_logged=False,
        safety_flags=safety,
        reason="Path entry plan ready; live path write was not requested.",
    )


def write_picker_path_entry_evidence(evidence: PickerPathEntryEvidence, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evidence.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path