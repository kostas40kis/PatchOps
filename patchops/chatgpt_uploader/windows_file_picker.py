from __future__ import annotations

import ctypes
from ctypes import wintypes
import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

PICKER_TITLE_KEYWORDS = ("open", "choose file", "choose files", "select file", "select files", "browse")
ERROR_TITLE_KEYWORDS = ("rename", "invalid", "error", "not found", "access denied")
ERROR_TEXT_KEYWORDS = (
    "the file name is not valid",
    "file name is not valid",
    "cannot find",
    "could not find",
    "access is denied",
    "file not found",
    "already exists",
    "is in use",
)
PICKER_CHILD_CLASSES = {"edit", "button", "combobox", "comboboxex32", "directuihwnd", "shelldll_defview", "workerw"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


@dataclass(frozen=True)
class WindowDescriptor:
    handle: int
    class_name: str
    title_sha256: str | None
    title_length: int
    title_has_open: bool
    title_has_choose: bool
    title_has_rename: bool
    title_has_error: bool
    visible: bool
    enabled: bool
    child_class_counts: dict[str, int]
    child_text_keyword_hits: list[str]
    rectangle: dict[str, int] | None = None
    owner_handle: int | None = None

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PickerDetection:
    status: str
    picker_detected: bool
    picker_count: int
    ambiguous: bool
    error_modal_detected: bool
    error_modal_count: int
    selected_picker: dict[str, Any] | None
    picker_candidates: list[dict[str, Any]]
    error_modal_candidates: list[dict[str, Any]]
    observed_window_count: int
    safety_flags: dict[str, bool]
    reason: str
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def default_safety_flags() -> dict[str, bool]:
    return {
        "file_picker_open_attempted": False,
        "file_path_written": False,
        "file_selected": False,
        "open_button_pressed": False,
        "file_upload_attempted": False,
        "chatgpt_submit_performed": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
        "random_page_click_performed": False,
        "conversation_text_logged": False,
    }


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    lower = text.lower()
    return any(needle in lower for needle in needles)


def _keyword_hits(text: str, needles: Iterable[str]) -> list[str]:
    lower = text.lower()
    return [needle for needle in needles if needle in lower]


def _get_window_text(hwnd: int) -> str:
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return ""
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value or ""
    except Exception:
        return ""


def _get_class_name(hwnd: int) -> str:
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        buffer = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buffer, 256)
        return buffer.value or ""
    except Exception:
        return ""


def _get_window_rect(hwnd: int) -> dict[str, int] | None:
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        rect = wintypes.RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return None
        return {"left": int(rect.left), "top": int(rect.top), "right": int(rect.right), "bottom": int(rect.bottom)}
    except Exception:
        return None


def _is_visible(hwnd: int) -> bool:
    try:
        return bool(ctypes.WinDLL("user32", use_last_error=True).IsWindowVisible(hwnd))
    except Exception:
        return False


def _is_enabled(hwnd: int) -> bool:
    try:
        return bool(ctypes.WinDLL("user32", use_last_error=True).IsWindowEnabled(hwnd))
    except Exception:
        return False


def _owner_handle(hwnd: int) -> int | None:
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        GW_OWNER = 4
        owner = user32.GetWindow(hwnd, GW_OWNER)
        return int(owner) if owner else None
    except Exception:
        return None


def _child_descriptors(hwnd: int) -> tuple[dict[str, int], list[str]]:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    EnumChildProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    class_counts: dict[str, int] = {}
    text_hits: set[str] = set()

    def callback(child: int, lparam: int) -> bool:
        try:
            cls = _get_class_name(int(child)).lower()
            if cls:
                class_counts[cls] = class_counts.get(cls, 0) + 1
            text = _get_window_text(int(child))
            for hit in _keyword_hits(text, ERROR_TEXT_KEYWORDS + PICKER_TITLE_KEYWORDS):
                text_hits.add(hit)
        except Exception:
            return True
        return True

    try:
        user32.EnumChildWindows(int(hwnd), EnumChildProc(callback), 0)
    except Exception:
        pass
    return class_counts, sorted(text_hits)


def describe_top_level_windows() -> list[WindowDescriptor]:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    descriptors: list[WindowDescriptor] = []

    def callback(hwnd: int, lparam: int) -> bool:
        try:
            handle = int(hwnd)
            if not _is_visible(handle):
                return True
            class_name = _get_class_name(handle)
            title = _get_window_text(handle)
            title_lower = title.lower()
            child_counts, child_hits = _child_descriptors(handle)
            descriptors.append(
                WindowDescriptor(
                    handle=handle,
                    class_name=class_name,
                    title_sha256=sha256_text(title) if title else None,
                    title_length=len(title),
                    title_has_open="open" in title_lower,
                    title_has_choose="choose" in title_lower or "select" in title_lower,
                    title_has_rename="rename" in title_lower,
                    title_has_error=_contains_any(title, ERROR_TITLE_KEYWORDS),
                    visible=True,
                    enabled=_is_enabled(handle),
                    child_class_counts=child_counts,
                    child_text_keyword_hits=child_hits,
                    rectangle=_get_window_rect(handle),
                    owner_handle=_owner_handle(handle),
                )
            )
        except Exception:
            return True
        return True

    user32.EnumWindows(EnumWindowsProc(callback), 0)
    return descriptors


def descriptor_is_picker(descriptor: WindowDescriptor) -> bool:
    class_lower = descriptor.class_name.lower()
    if class_lower != "#32770":
        return False
    title_signal = descriptor.title_has_open or descriptor.title_has_choose
    child_classes = set(descriptor.child_class_counts)
    has_file_name_capable_child = bool(child_classes.intersection({"edit", "combobox", "comboboxex32"}))
    has_open_button_or_shell = "button" in child_classes or "directuihwnd" in child_classes or "shelldll_defview" in child_classes
    return bool(title_signal and has_file_name_capable_child and has_open_button_or_shell)


def descriptor_is_known_error_modal(descriptor: WindowDescriptor) -> bool:
    class_lower = descriptor.class_name.lower()
    if class_lower != "#32770":
        return False
    if descriptor.title_has_rename or descriptor.title_has_error:
        return True
    return any(hit in ERROR_TEXT_KEYWORDS for hit in descriptor.child_text_keyword_hits)


def classify_descriptors(descriptors: list[WindowDescriptor]) -> PickerDetection:
    pickers = [d for d in descriptors if descriptor_is_picker(d)]
    errors = [d for d in descriptors if descriptor_is_known_error_modal(d)]
    ambiguous = len(pickers) > 1
    if ambiguous:
        status = "BLOCKED_AMBIGUOUS_PICKERS"
        reason = "multiple_file_picker_candidates"
    elif pickers:
        status = "PASS_PICKER_DETECTED"
        reason = "single_file_picker_candidate_detected"
    elif errors:
        status = "PASS_ERROR_MODAL_DETECTED"
        reason = "known_error_modal_detected"
    else:
        status = "PASS_NO_PICKER"
        reason = "no_file_picker_or_known_error_modal_detected"

    return PickerDetection(
        status=status,
        picker_detected=bool(pickers),
        picker_count=len(pickers),
        ambiguous=ambiguous,
        error_modal_detected=bool(errors),
        error_modal_count=len(errors),
        selected_picker=pickers[0].to_payload() if len(pickers) == 1 else None,
        picker_candidates=[d.to_payload() for d in pickers[:5]],
        error_modal_candidates=[d.to_payload() for d in errors[:5]],
        observed_window_count=len(descriptors),
        safety_flags=default_safety_flags(),
        reason=reason,
        created_at=utc_now_iso(),
    )


def detect_file_picker(*, wait_seconds: float = 0.0, poll_interval_seconds: float = 0.5) -> PickerDetection:
    deadline = time.time() + max(0.0, wait_seconds)
    last_detection = classify_descriptors(describe_top_level_windows())
    while time.time() <= deadline:
        detection = classify_descriptors(describe_top_level_windows())
        if detection.picker_detected or detection.error_modal_detected or detection.ambiguous:
            return detection
        last_detection = detection
        time.sleep(max(0.05, poll_interval_seconds))
    return last_detection


def write_detection_evidence(detection: PickerDetection, evidence_dir: str | Path, *, basename: str = "u2_02_file_picker_detection") -> tuple[Path, Path]:
    root = Path(evidence_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    safe_base = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in basename).strip("_") or "file_picker_detection"
    json_path = root / f"{safe_base}.json"
    txt_path = root / f"{safe_base}.txt"
    payload = detection.to_payload()
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "PATCHOPS CHATGPT UPLOADER FILE PICKER DETECTION",
        "================================================",
        f"Status                 : {detection.status}",
        f"Reason                 : {detection.reason}",
        f"PickerDetected         : {str(detection.picker_detected).lower()}",
        f"PickerCount            : {detection.picker_count}",
        f"Ambiguous              : {str(detection.ambiguous).lower()}",
        f"ErrorModalDetected     : {str(detection.error_modal_detected).lower()}",
        f"ErrorModalCount        : {detection.error_modal_count}",
        f"ObservedWindowCount    : {detection.observed_window_count}",
        "FilePathWritten        : false",
        "FileSelected           : false",
        "OpenButtonPressed      : false",
        "ChatGPTSubmitPerformed : false",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path
