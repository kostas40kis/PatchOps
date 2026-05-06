from __future__ import annotations

import ctypes
import importlib.util
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.chatgpt_uploader.config import load_config
from patchops.chatgpt_uploader.edge_target import focus_chatgpt_edge_target
from patchops.chatgpt_uploader.preflight_policy import decide_launch_permission
from patchops.chatgpt_uploader.windows_file_picker import PickerDetection, detect_file_picker

WM_CLOSE = 0x0010

# Kept for existing tests/docs, but U2.4E live flow does not use plus/menu search.
POSITIVE_PLUS_IDS = ("composer-plus-btn", "attach", "attachment", "upload", "file-upload", "upload-button")
POSITIVE_PLUS_NAMES = ("attach", "add photos", "add files", "upload", "file", "+", "paperclip")
POSITIVE_MENU_NAMES = ("add photos", "add files", "photos & files", "photos and files", "upload from computer", "attach files", "upload file", "upload files")
REJECT_NAMES = (
    "send", "submit", "voice", "dictate", "new chat", "temporary chat", "sidebar", "profile", "account",
    "settings", "help", "apps", "gpts", "explore", "model", "search", "tools", "reason", "canvas",
    "regenerate", "stop", "read aloud", "copy", "thumbs", "like", "dislike"
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def pywinauto_available() -> bool:
    return importlib.util.find_spec("pywinauto") is not None


@dataclass(frozen=True)
class TriggerCandidate:
    source: str
    name: str
    automation_id: str
    control_type: str
    class_name: str
    score: int
    reason: str
    rectangle: dict[str, int] | None

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class UploadTriggerAttempt:
    index: int
    status: str
    reason: str
    edge_status: str
    trigger_backend: str
    plus_candidate: dict[str, Any] | None
    menu_candidate: dict[str, Any] | None
    observed_plus_candidates: list[dict[str, Any]]
    observed_menu_candidates: list[dict[str, Any]]
    picker_status: str
    picker_detected: bool
    picker_count: int
    picker_closed: bool
    keyboard_shortcut_attempted: bool
    tab_enter_attempted: bool
    neutral_click_attempted: bool
    safe_click_attempted: bool
    safe_click_point: dict[str, int] | None
    tab_sent: bool
    enter_count: int
    stopped_before_second_enter: bool
    safety_flags: dict[str, bool]
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class UploadTriggerRun:
    status: str
    attempts_requested: int
    attempts_completed: int
    pass_count: int
    attempts: list[dict[str, Any]]
    safety_flags: dict[str, bool]
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def default_trigger_safety_flags(
    *,
    picker_open_attempted: bool = False,
    keyboard_shortcut_attempted: bool = False,
    tab_enter_attempted: bool = False,
    neutral_click_attempted: bool = False,
    safe_click_attempted: bool | None = None,
) -> dict[str, bool]:
    safe_click = bool(neutral_click_attempted if safe_click_attempted is None else safe_click_attempted)
    return {
        "upload_trigger_attempted": bool(picker_open_attempted or keyboard_shortcut_attempted or tab_enter_attempted),
        "file_picker_open_attempted": bool(picker_open_attempted or keyboard_shortcut_attempted or tab_enter_attempted),
        "keyboard_shortcut_attempted": bool(keyboard_shortcut_attempted),
        "tab_enter_attempted": bool(tab_enter_attempted),
        "neutral_click_attempted": bool(neutral_click_attempted),
        "safe_click_attempted": safe_click,
        "plus_control_search_attempted": False,
        "menu_control_search_attempted": False,
        "ctrl_u_attempted": False,
        "file_path_written": False,
        "file_selected": False,
        "open_button_pressed": False,
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


def score_plus_candidate(*, name: str, automation_id: str, control_type: str, class_name: str) -> tuple[int, str]:
    hay = " ".join([name, automation_id, control_type, class_name]).lower()
    if any(bad in hay for bad in REJECT_NAMES):
        return -100, "rejected_by_name"
    score = 0
    reasons: list[str] = []
    if any(token in automation_id.lower() for token in POSITIVE_PLUS_IDS):
        score += 80
        reasons.append("positive_automation_id")
    if any(token in name.lower() for token in POSITIVE_PLUS_NAMES):
        score += 40
        reasons.append("positive_name")
    if control_type.lower() in {"button", "splitbutton", "menuitem", "custom"}:
        score += 10
        reasons.append("clickable_control_type")
    if class_name.lower() in {"button", "menuflyoutpresenter"}:
        score += 5
        reasons.append("positive_class")
    return score, "+".join(reasons) if reasons else "no_positive_signal"


def score_menu_candidate(*, name: str, automation_id: str, control_type: str, class_name: str) -> tuple[int, str]:
    hay = " ".join([name, automation_id, control_type, class_name]).lower()
    if any(bad in hay for bad in ("send", "camera", "image generation", "drive", "onedrive", "connect", "take photo")):
        return -100, "rejected_by_name"
    score = 0
    reasons: list[str] = []
    if any(token in name.lower() for token in POSITIVE_MENU_NAMES):
        score += 80
        reasons.append("positive_menu_name")
    if control_type.lower() in {"menuitem", "button", "listitem", "text"}:
        score += 10
        reasons.append("menu_clickable_type")
    return score, "+".join(reasons) if reasons else "no_positive_signal"


def _send_keys(keys: str) -> tuple[bool, str]:
    try:
        from pywinauto.keyboard import send_keys  # type: ignore
    except Exception as exc:
        return False, f"pywinauto.keyboard unavailable:{exc}"
    try:
        send_keys(keys, pause=0.05, with_spaces=True, vk_packet=False)
        return True, "send_keys"
    except Exception as exc:
        return False, f"send_keys_failed:{exc}"


def _mouse_click(x: int, y: int) -> tuple[bool, str]:
    try:
        from pywinauto.mouse import click  # type: ignore
    except Exception as exc:
        return False, f"pywinauto.mouse unavailable:{exc}"
    try:
        click(button="left", coords=(int(x), int(y)))
        return True, f"safe_click:{x},{y}"
    except Exception as exc:
        return False, f"safe_click_failed:{exc}"


def _send_wm_close(hwnd: int) -> bool:
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        return bool(user32.PostMessageW(int(hwnd), WM_CLOSE, 0, 0))
    except Exception:
        return False


def close_single_detected_picker(detection: PickerDetection) -> bool:
    picker = detection.selected_picker or {}
    handle = picker.get("handle")
    if handle is None:
        return False
    ok = _send_wm_close(int(handle))
    time.sleep(0.5)
    after = detect_file_picker(wait_seconds=0)
    return bool(ok and not after.picker_detected)


def _attempt_result(
    *,
    index: int,
    status: str,
    reason: str,
    edge_status: str = "UNKNOWN",
    trigger_backend: str = "single_safe_click_tab_enter",
    picker_detection: PickerDetection | None = None,
    picker_closed: bool = False,
    picker_open_attempted: bool = False,
    tab_enter_attempted: bool = False,
    neutral_click_attempted: bool = False,
    safe_click_attempted: bool = False,
    safe_click_point: dict[str, int] | None = None,
    tab_sent: bool = False,
    enter_count: int = 0,
    stopped_before_second_enter: bool = False,
) -> UploadTriggerAttempt:
    return UploadTriggerAttempt(
        index=index,
        status=status,
        reason=reason,
        edge_status=edge_status,
        trigger_backend=trigger_backend,
        plus_candidate=None,
        menu_candidate=None,
        observed_plus_candidates=[],
        observed_menu_candidates=[],
        picker_status=picker_detection.status if picker_detection else "NOT_CHECKED",
        picker_detected=picker_detection.picker_detected if picker_detection else False,
        picker_count=picker_detection.picker_count if picker_detection else 0,
        picker_closed=picker_closed,
        keyboard_shortcut_attempted=False,
        tab_enter_attempted=tab_enter_attempted,
        neutral_click_attempted=neutral_click_attempted,
        safe_click_attempted=safe_click_attempted,
        safe_click_point=safe_click_point,
        tab_sent=tab_sent,
        enter_count=int(enter_count),
        stopped_before_second_enter=bool(stopped_before_second_enter),
        safety_flags=default_trigger_safety_flags(
            picker_open_attempted=picker_open_attempted,
            keyboard_shortcut_attempted=False,
            tab_enter_attempted=tab_enter_attempted,
            neutral_click_attempted=neutral_click_attempted,
            safe_click_attempted=safe_click_attempted,
        ),
        created_at=utc_now_iso(),
    )


def blocked_missing_pywinauto_attempt(*, index: int = 1) -> UploadTriggerAttempt:
    return _attempt_result(
        index=index,
        status="BLOCKED_MISSING_PYWINAUTO",
        reason="pywinauto is required for the single safe-click Tab/Enter trigger but is not installed in this Python runtime",
        edge_status="NOT_ATTEMPTED_DEPENDENCY_MISSING",
        picker_open_attempted=False,
    )


def _safe_click_from_edge_window(selected_window: dict[str, Any], *, x_ratio: float = 0.50, y_ratio: float = 0.34) -> tuple[bool, str, dict[str, int] | None]:
    rect = selected_window.get("rectangle") or {}
    try:
        left = int(rect.get("left"))
        top = int(rect.get("top"))
        right = int(rect.get("right"))
        bottom = int(rect.get("bottom"))
    except Exception:
        return False, "missing_edge_rectangle", None
    width = max(1, right - left)
    height = max(1, bottom - top)
    xr = min(0.90, max(0.10, float(x_ratio)))
    yr = min(0.80, max(0.18, float(y_ratio)))
    x = left + int(width * xr)
    y = top + int(height * yr)
    ok, why = _mouse_click(x, y)
    return ok, why, {"x": int(x), "y": int(y), "x_ratio_times_1000": int(xr * 1000), "y_ratio_times_1000": int(yr * 1000)}


def _finish_after_detection(
    *,
    index: int,
    edge_status: str,
    detection: PickerDetection,
    reason: str,
    safe_click_point: dict[str, int] | None,
    enter_count: int,
    stopped_before_second_enter: bool,
) -> UploadTriggerAttempt:
    if detection.ambiguous:
        return _attempt_result(
            index=index,
            status="BLOCKED_AMBIGUOUS_PICKERS",
            reason=reason,
            edge_status=edge_status,
            picker_detection=detection,
            picker_open_attempted=True,
            tab_enter_attempted=True,
            neutral_click_attempted=True,
            safe_click_attempted=True,
            safe_click_point=safe_click_point,
            tab_sent=True,
            enter_count=enter_count,
            stopped_before_second_enter=stopped_before_second_enter,
        )
    if detection.picker_detected:
        closed = close_single_detected_picker(detection)
        return _attempt_result(
            index=index,
            status="PASS_PICKER_OPENED_AND_CLOSED",
            reason=reason,
            edge_status=edge_status,
            picker_detection=detection,
            picker_closed=closed,
            picker_open_attempted=True,
            tab_enter_attempted=True,
            neutral_click_attempted=True,
            safe_click_attempted=True,
            safe_click_point=safe_click_point,
            tab_sent=True,
            enter_count=enter_count,
            stopped_before_second_enter=stopped_before_second_enter,
        )
    return _attempt_result(
        index=index,
        status="FAIL_PICKER_NOT_DETECTED",
        reason=reason,
        edge_status=edge_status,
        picker_detection=detection,
        picker_open_attempted=True,
        tab_enter_attempted=True,
        neutral_click_attempted=True,
        safe_click_attempted=True,
        safe_click_point=safe_click_point,
        tab_sent=True,
        enter_count=enter_count,
    )


def try_single_safe_click_tab_enter_trigger(
    *,
    index: int,
    edge_status: str,
    selected_window: dict[str, Any],
    x_ratio: float = 0.50,
    y_ratio: float = 0.34,
) -> UploadTriggerAttempt:
    ok, why, click_point = _safe_click_from_edge_window(selected_window, x_ratio=x_ratio, y_ratio=y_ratio)
    if not ok:
        return _attempt_result(
            index=index,
            status="FAIL_SAFE_CLICK",
            reason=why,
            edge_status=edge_status,
            picker_open_attempted=False,
            tab_enter_attempted=False,
            neutral_click_attempted=True,
            safe_click_attempted=True,
            safe_click_point=click_point,
        )
    time.sleep(0.30)

    ok, tab_reason = _send_keys("{TAB}")
    if not ok:
        return _attempt_result(
            index=index,
            status="FAIL_TAB_SEND",
            reason=f"{why};{tab_reason}",
            edge_status=edge_status,
            picker_open_attempted=True,
            tab_enter_attempted=True,
            neutral_click_attempted=True,
            safe_click_attempted=True,
            safe_click_point=click_point,
            tab_sent=False,
        )
    time.sleep(0.25)

    ok, enter1_reason = _send_keys("{ENTER}")
    time.sleep(0.75)
    first_detection = detect_file_picker(wait_seconds=1.0, poll_interval_seconds=0.25)
    if first_detection.picker_detected or first_detection.ambiguous:
        return _finish_after_detection(
            index=index,
            edge_status=edge_status,
            detection=first_detection,
            reason=f"{why};{tab_reason};enter1:{enter1_reason};picker detected after first Enter; second Enter skipped for safety",
            safe_click_point=click_point,
            enter_count=1,
            stopped_before_second_enter=True,
        )
    if not ok:
        return _attempt_result(
            index=index,
            status="FAIL_ENTER_SEND",
            reason=f"{why};{tab_reason};enter1:{enter1_reason}",
            edge_status=edge_status,
            picker_detection=first_detection,
            picker_open_attempted=True,
            tab_enter_attempted=True,
            neutral_click_attempted=True,
            safe_click_attempted=True,
            safe_click_point=click_point,
            tab_sent=True,
            enter_count=1,
        )

    ok, enter2_reason = _send_keys("{ENTER}")
    time.sleep(0.75)
    second_detection = detect_file_picker(wait_seconds=1.0, poll_interval_seconds=0.25)
    if second_detection.picker_detected or second_detection.ambiguous:
        return _finish_after_detection(
            index=index,
            edge_status=edge_status,
            detection=second_detection,
            reason=f"{why};{tab_reason};enter1:{enter1_reason};enter2:{enter2_reason};picker detected after second Enter",
            safe_click_point=click_point,
            enter_count=2,
            stopped_before_second_enter=False,
        )
    if not ok:
        return _attempt_result(
            index=index,
            status="FAIL_ENTER_SEND",
            reason=f"{why};{tab_reason};enter1:{enter1_reason};enter2:{enter2_reason}",
            edge_status=edge_status,
            picker_detection=second_detection,
            picker_open_attempted=True,
            tab_enter_attempted=True,
            neutral_click_attempted=True,
            safe_click_attempted=True,
            safe_click_point=click_point,
            tab_sent=True,
            enter_count=2,
        )
    return _finish_after_detection(
        index=index,
        edge_status=edge_status,
        detection=second_detection,
        reason=f"{why};{tab_reason};enter1:{enter1_reason};enter2:{enter2_reason};picker not detected",
        safe_click_point=click_point,
        enter_count=2,
        stopped_before_second_enter=False,
    )


def open_picker_once(
    *,
    target_config_path: str | Path,
    timeout_seconds: int = 10,
    allow_launch_target: bool = False,
    allow_open_configured_url: bool = False,
    attempt_index: int = 1,
    allow_keyboard_shortcut: bool = False,
    allow_tab_enter_sequence: bool = False,
    allow_neutral_click: bool = False,
    allow_single_safe_click_tab_enter: bool = False,
    safe_click_x_ratio: float = 0.50,
    safe_click_y_ratio: float = 0.34,
) -> UploadTriggerAttempt:
    # U2.4E ignores older noisy trigger flags. Only the explicit single-safe-click path can actuate.
    if not pywinauto_available():
        return blocked_missing_pywinauto_attempt(index=attempt_index)

    cfg = load_config(target_config_path)
    decision = decide_launch_permission(
        target_mode=cfg.mode,
        allow_launch_target_requested=allow_launch_target,
        allow_open_configured_url_requested=allow_open_configured_url,
    )
    edge_result = focus_chatgpt_edge_target(target_url=cfg.target_url, allow_launch=decision.allow_launch, timeout_seconds=timeout_seconds)
    edge_status = str(edge_result.get("status") or "UNKNOWN")
    if edge_status != "PASS":
        return _attempt_result(index=attempt_index, status="FAIL_EDGE_NOT_FOCUSED", reason=edge_status, edge_status=edge_status)
    selected = edge_result.get("selected_target_window") or {}
    if selected.get("handle") is None:
        return _attempt_result(index=attempt_index, status="FAIL_EDGE_HANDLE_MISSING", reason="selected target window handle missing", edge_status=edge_status)
    if not allow_single_safe_click_tab_enter:
        return _attempt_result(index=attempt_index, status="PASS_DRY_RUN_NO_PICKER_OPEN", reason="--allow-single-safe-click-tab-enter not provided", edge_status=edge_status)
    return try_single_safe_click_tab_enter_trigger(
        index=attempt_index,
        edge_status=edge_status,
        selected_window=selected,
        x_ratio=safe_click_x_ratio,
        y_ratio=safe_click_y_ratio,
    )


def run_open_picker_attempts(
    *,
    target_config_path: str | Path,
    attempts: int = 5,
    timeout_seconds: int = 10,
    allow_open_picker: bool = False,
    allow_keyboard_shortcut: bool = False,
    allow_tab_enter_sequence: bool = False,
    allow_neutral_click: bool = False,
    allow_single_safe_click_tab_enter: bool = False,
    safe_click_x_ratio: float = 0.50,
    safe_click_y_ratio: float = 0.34,
) -> UploadTriggerRun:
    requested = max(1, int(attempts))
    if not allow_open_picker:
        attempt = _attempt_result(index=1, status="PASS_DRY_RUN_NO_PICKER_OPEN", reason="--allow-open-picker not provided")
        return UploadTriggerRun(
            status="PASS_DRY_RUN_NO_PICKER_OPEN",
            attempts_requested=requested,
            attempts_completed=0,
            pass_count=0,
            attempts=[attempt.to_payload()],
            safety_flags=default_trigger_safety_flags(picker_open_attempted=False),
            created_at=utc_now_iso(),
        )
    if not pywinauto_available():
        attempt = blocked_missing_pywinauto_attempt(index=1)
        return UploadTriggerRun(
            status="BLOCKED_MISSING_PYWINAUTO",
            attempts_requested=requested,
            attempts_completed=0,
            pass_count=0,
            attempts=[attempt.to_payload()],
            safety_flags=default_trigger_safety_flags(picker_open_attempted=False),
            created_at=utc_now_iso(),
        )

    results: list[UploadTriggerAttempt] = []
    for index in range(1, requested + 1):
        results.append(
            open_picker_once(
                target_config_path=target_config_path,
                timeout_seconds=timeout_seconds,
                attempt_index=index,
                allow_keyboard_shortcut=allow_keyboard_shortcut,
                allow_tab_enter_sequence=allow_tab_enter_sequence,
                allow_neutral_click=allow_neutral_click,
                allow_single_safe_click_tab_enter=allow_single_safe_click_tab_enter,
                safe_click_x_ratio=safe_click_x_ratio,
                safe_click_y_ratio=safe_click_y_ratio,
            )
        )
        time.sleep(0.5)
    pass_count = sum(1 for item in results if item.status == "PASS_PICKER_OPENED_AND_CLOSED")
    status = "PASS" if pass_count == requested else "FAIL_OR_BLOCKED"
    return UploadTriggerRun(
        status=status,
        attempts_requested=requested,
        attempts_completed=len(results),
        pass_count=pass_count,
        attempts=[item.to_payload() for item in results],
        safety_flags=default_trigger_safety_flags(
            picker_open_attempted=True,
            keyboard_shortcut_attempted=False,
            tab_enter_attempted=allow_single_safe_click_tab_enter,
            neutral_click_attempted=allow_single_safe_click_tab_enter,
            safe_click_attempted=allow_single_safe_click_tab_enter,
        ),
        created_at=utc_now_iso(),
    )


def write_upload_trigger_evidence(run: UploadTriggerRun, evidence_dir: str | Path, *, basename: str = "u2_04_upload_trigger") -> tuple[Path, Path]:
    root = Path(evidence_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    safe_base = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in basename).strip("_") or "upload_trigger"
    json_path = root / f"{safe_base}.json"
    txt_path = root / f"{safe_base}.txt"
    payload = run.to_payload()
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    backend_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    stopped_before_second_enter = 0
    for attempt in run.attempts:
        backend = str(attempt.get("trigger_backend") or "none")
        status = str(attempt.get("status") or "unknown")
        backend_counts[backend] = backend_counts.get(backend, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
        if attempt.get("stopped_before_second_enter"):
            stopped_before_second_enter += 1
    lines = [
        "PATCHOPS CHATGPT UPLOADER UPLOAD TRIGGER",
        "==========================================",
        f"Status                 : {run.status}",
        f"AttemptsRequested      : {run.attempts_requested}",
        f"AttemptsCompleted      : {run.attempts_completed}",
        f"PassCount              : {run.pass_count}",
        f"BackendCounts          : {backend_counts}",
        f"StatusCounts           : {status_counts}",
        f"StoppedBeforeEnter2    : {stopped_before_second_enter}",
        f"FilePickerOpenAttempted: {str(run.safety_flags['file_picker_open_attempted']).lower()}",
        f"KeyboardShortcutAttempt : {str(run.safety_flags.get('keyboard_shortcut_attempted', False)).lower()}",
        f"TabEnterAttempted      : {str(run.safety_flags.get('tab_enter_attempted', False)).lower()}",
        f"NeutralClickAttempted  : {str(run.safety_flags.get('neutral_click_attempted', False)).lower()}",
        f"SafeClickAttempted     : {str(run.safety_flags.get('safe_click_attempted', False)).lower()}",
        f"PlusControlSearch      : {str(run.safety_flags.get('plus_control_search_attempted', False)).lower()}",
        f"MenuControlSearch      : {str(run.safety_flags.get('menu_control_search_attempted', False)).lower()}",
        f"CtrlUAttempted         : {str(run.safety_flags.get('ctrl_u_attempted', False)).lower()}",
        "FilePathWritten        : false",
        "FileSelected           : false",
        "OpenButtonPressed      : false",
        "AttachmentConfirmed    : false",
        "ChatGPTSubmitPerformed : false",
        "SeleniumUsed           : false",
        "WebDriverUsed          : false",
        "BrowserDomAutomation   : false",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path
