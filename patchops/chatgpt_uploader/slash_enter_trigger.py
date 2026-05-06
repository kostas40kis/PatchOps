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
DEFAULT_SAFE_CLICK_X_RATIO = 0.50
DEFAULT_SAFE_CLICK_Y_RATIO = 0.34
PASS_PICKER_STATUSES = {"PASS_PICKER_OPENED_AND_CLOSED", "PASS_PICKER_OPENED_LEFT_OPEN"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def pywinauto_available() -> bool:
    return importlib.util.find_spec("pywinauto") is not None


@dataclass(frozen=True)
class SlashEnterAttempt:
    index: int
    status: str
    reason: str
    edge_status: str
    trigger_backend: str
    picker_status: str
    picker_detected: bool
    picker_count: int
    picker_closed: bool
    safe_click_attempted: bool
    safe_click_point: dict[str, int] | None
    slash_sent: bool
    enter_count: int
    safety_flags: dict[str, bool]
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SlashEnterRun:
    status: str
    attempts_requested: int
    attempts_completed: int
    pass_count: int
    attempts: list[dict[str, Any]]
    safety_flags: dict[str, bool]
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def slash_enter_safety_flags(*, open_attempted: bool = False, safe_click_attempted: bool = False, slash_sent: bool = False) -> dict[str, bool]:
    return {
        "upload_trigger_attempted": bool(open_attempted),
        "file_picker_open_attempted": bool(open_attempted),
        "safe_click_attempted": bool(safe_click_attempted),
        "slash_sent": bool(slash_sent),
        "tab_sent": False,
        "second_enter_attempted": False,
        "keyboard_shortcut_attempted": False,
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


def _safe_click_from_edge_window(selected_window: dict[str, Any], *, x_ratio: float = DEFAULT_SAFE_CLICK_X_RATIO, y_ratio: float = DEFAULT_SAFE_CLICK_Y_RATIO) -> tuple[bool, str, dict[str, int] | None]:
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


def _attempt(
    *,
    index: int,
    status: str,
    reason: str,
    edge_status: str = "UNKNOWN",
    detection: PickerDetection | None = None,
    picker_closed: bool = False,
    open_attempted: bool = False,
    safe_click_attempted: bool = False,
    safe_click_point: dict[str, int] | None = None,
    slash_sent: bool = False,
    enter_count: int = 0,
) -> SlashEnterAttempt:
    return SlashEnterAttempt(
        index=index,
        status=status,
        reason=reason,
        edge_status=edge_status,
        trigger_backend="single_safe_click_slash_enter",
        picker_status=detection.status if detection else "NOT_CHECKED",
        picker_detected=detection.picker_detected if detection else False,
        picker_count=detection.picker_count if detection else 0,
        picker_closed=picker_closed,
        safe_click_attempted=safe_click_attempted,
        safe_click_point=safe_click_point,
        slash_sent=slash_sent,
        enter_count=int(enter_count),
        safety_flags=slash_enter_safety_flags(open_attempted=open_attempted, safe_click_attempted=safe_click_attempted, slash_sent=slash_sent),
        created_at=utc_now_iso(),
    )


def _finish_after_detection(
    *,
    index: int,
    edge_status: str,
    detection: PickerDetection,
    reason: str,
    safe_click_point: dict[str, int] | None,
    close_picker_on_detect: bool = True,
) -> SlashEnterAttempt:
    if detection.ambiguous:
        return _attempt(
            index=index,
            status="BLOCKED_AMBIGUOUS_PICKERS",
            reason=reason,
            edge_status=edge_status,
            detection=detection,
            open_attempted=True,
            safe_click_attempted=True,
            safe_click_point=safe_click_point,
            slash_sent=True,
            enter_count=1,
        )
    if detection.picker_detected:
        closed = close_single_detected_picker(detection) if close_picker_on_detect else False
        return _attempt(
            index=index,
            status="PASS_PICKER_OPENED_AND_CLOSED" if close_picker_on_detect else "PASS_PICKER_OPENED_LEFT_OPEN",
            reason=reason if close_picker_on_detect else reason + ";picker intentionally left open for composition",
            edge_status=edge_status,
            detection=detection,
            picker_closed=closed,
            open_attempted=True,
            safe_click_attempted=True,
            safe_click_point=safe_click_point,
            slash_sent=True,
            enter_count=1,
        )
    return _attempt(
        index=index,
        status="FAIL_PICKER_NOT_DETECTED",
        reason=reason,
        edge_status=edge_status,
        detection=detection,
        open_attempted=True,
        safe_click_attempted=True,
        safe_click_point=safe_click_point,
        slash_sent=True,
        enter_count=1,
    )


def run_single_slash_enter_attempt(
    *,
    target_config_path: str | Path,
    attempt_index: int = 1,
    timeout_seconds: int = 10,
    x_ratio: float = DEFAULT_SAFE_CLICK_X_RATIO,
    y_ratio: float = DEFAULT_SAFE_CLICK_Y_RATIO,
    close_picker_on_detect: bool = True,
) -> SlashEnterAttempt:
    if not pywinauto_available():
        return _attempt(index=attempt_index, status="BLOCKED_MISSING_PYWINAUTO", reason="pywinauto is required", edge_status="NOT_ATTEMPTED_DEPENDENCY_MISSING")

    cfg = load_config(target_config_path)
    decision = decide_launch_permission(target_mode=cfg.mode, allow_launch_target_requested=False, allow_open_configured_url_requested=False)
    edge_result = focus_chatgpt_edge_target(target_url=cfg.target_url, allow_launch=decision.allow_launch, timeout_seconds=max(1, int(timeout_seconds)))
    edge_status = str(edge_result.get("status") or "UNKNOWN")
    if edge_status != "PASS":
        return _attempt(index=attempt_index, status="FAIL_EDGE_NOT_FOCUSED", reason=edge_status, edge_status=edge_status)
    selected = edge_result.get("selected_target_window") or {}
    if selected.get("handle") is None:
        return _attempt(index=attempt_index, status="FAIL_EDGE_HANDLE_MISSING", reason="selected target window handle missing", edge_status=edge_status)

    ok, click_reason, click_point = _safe_click_from_edge_window(selected, x_ratio=x_ratio, y_ratio=y_ratio)
    if not ok:
        return _attempt(index=attempt_index, status="FAIL_SAFE_CLICK", reason=click_reason, edge_status=edge_status, safe_click_attempted=True, safe_click_point=click_point)
    time.sleep(0.25)

    ok, slash_reason = _send_keys("/")
    if not ok:
        return _attempt(index=attempt_index, status="FAIL_SLASH_SEND", reason=f"{click_reason};slash:{slash_reason}", edge_status=edge_status, open_attempted=True, safe_click_attempted=True, safe_click_point=click_point, slash_sent=False)
    time.sleep(0.25)

    ok, enter_reason = _send_keys("{ENTER}")
    time.sleep(0.85)
    detection = detect_file_picker(wait_seconds=1.25, poll_interval_seconds=0.25)
    if not ok:
        return _attempt(index=attempt_index, status="FAIL_ENTER_SEND", reason=f"{click_reason};slash:{slash_reason};enter:{enter_reason}", edge_status=edge_status, detection=detection, open_attempted=True, safe_click_attempted=True, safe_click_point=click_point, slash_sent=True, enter_count=1)

    return _finish_after_detection(
        index=attempt_index,
        edge_status=edge_status,
        detection=detection,
        reason=f"{click_reason};slash:{slash_reason};enter:{enter_reason}",
        safe_click_point=click_point,
        close_picker_on_detect=close_picker_on_detect,
    )


def run_slash_enter_trigger(
    *,
    target_config_path: str | Path,
    allow_open_picker: bool,
    attempts: int = 1,
    timeout_seconds: int = 10,
    x_ratio: float = DEFAULT_SAFE_CLICK_X_RATIO,
    y_ratio: float = DEFAULT_SAFE_CLICK_Y_RATIO,
    close_picker_on_detect: bool = True,
) -> SlashEnterRun:
    requested = max(1, int(attempts))
    if not allow_open_picker:
        attempt = _attempt(index=1, status="PASS_DRY_RUN_NO_PICKER_OPEN", reason="--allow-open-picker not provided")
        return SlashEnterRun(
            status="PASS_DRY_RUN_NO_PICKER_OPEN",
            attempts_requested=requested,
            attempts_completed=0,
            pass_count=0,
            attempts=[attempt.to_payload()],
            safety_flags=slash_enter_safety_flags(open_attempted=False),
            created_at=utc_now_iso(),
        )

    attempts_payload: list[SlashEnterAttempt] = []
    for index in range(1, requested + 1):
        attempts_payload.append(
            run_single_slash_enter_attempt(
                target_config_path=target_config_path,
                attempt_index=index,
                timeout_seconds=timeout_seconds,
                x_ratio=x_ratio,
                y_ratio=y_ratio,
                close_picker_on_detect=close_picker_on_detect,
            )
        )
        time.sleep(0.4)
    pass_count = sum(1 for item in attempts_payload if item.status in PASS_PICKER_STATUSES)
    status = "PASS" if pass_count == requested else "FAIL_OR_BLOCKED"
    return SlashEnterRun(
        status=status,
        attempts_requested=requested,
        attempts_completed=len(attempts_payload),
        pass_count=pass_count,
        attempts=[item.to_payload() for item in attempts_payload],
        safety_flags=slash_enter_safety_flags(open_attempted=True, safe_click_attempted=True, slash_sent=True),
        created_at=utc_now_iso(),
    )


def write_slash_enter_evidence(run: SlashEnterRun, evidence_dir: str | Path, *, basename: str = "u2_04g_slash_enter_trigger") -> tuple[Path, Path]:
    root = Path(evidence_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    safe_base = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in basename).strip("_") or "slash_enter_trigger"
    json_path = root / f"{safe_base}.json"
    txt_path = root / f"{safe_base}.txt"
    json_path.write_text(json.dumps(run.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "PATCHOPS CHATGPT UPLOADER SLASH ENTER TRIGGER",
        "===============================================",
        f"Status                 : {run.status}",
        f"AttemptsRequested      : {run.attempts_requested}",
        f"AttemptsCompleted      : {run.attempts_completed}",
        f"PassCount              : {run.pass_count}",
        f"FilePickerOpenAttempted: {str(run.safety_flags['file_picker_open_attempted']).lower()}",
        f"SafeClickAttempted     : {str(run.safety_flags['safe_click_attempted']).lower()}",
        f"SlashSent              : {str(run.safety_flags['slash_sent']).lower()}",
        f"TabSent                : {str(run.safety_flags['tab_sent']).lower()}",
        f"SecondEnterAttempted   : {str(run.safety_flags['second_enter_attempted']).lower()}",
        f"PlusControlSearch      : {str(run.safety_flags['plus_control_search_attempted']).lower()}",
        f"MenuControlSearch      : {str(run.safety_flags['menu_control_search_attempted']).lower()}",
        f"CtrlUAttempted         : {str(run.safety_flags['ctrl_u_attempted']).lower()}",
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
