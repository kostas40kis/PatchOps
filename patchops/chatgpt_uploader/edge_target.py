from __future__ import annotations

import ctypes
from ctypes import wintypes
import hashlib
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

CHATGPT_HOSTS = {"chatgpt.com", "chat.openai.com"}

SAFE_EDGE_PREFLIGHT_CAPABILITIES = {
    "normal_edge_only": True,
    "selenium_used": False,
    "webdriver_used": False,
    "browser_dom_automation_used": False,
    "file_upload_attempted": False,
    "chatgpt_submit_performed": False,
    "conversation_text_logged": False,
    "random_page_click_performed": False,
}


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def is_root_chatgpt_target(target_url: str) -> bool:
    try:
        parsed = urlparse(str(target_url).strip())
    except Exception:
        return False
    host = parsed.netloc.lower().split("@")[-1].split(":")[0]
    return parsed.scheme == "https" and host in CHATGPT_HOSTS and parsed.path in {"", "/"}


def edge_executable_candidates() -> list[Path]:
    return [
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path.home() / r"AppData\Local\Microsoft\Edge\Application\msedge.exe",
    ]


def start_normal_edge(target_url: str) -> dict[str, Any]:
    for candidate in edge_executable_candidates():
        if candidate.exists():
            proc = subprocess.Popen([str(candidate), target_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"normal_edge_started": True, "edge_executable": str(candidate), "pid": proc.pid}
    proc = subprocess.Popen(["cmd", "/c", "start", "", target_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {"normal_edge_started": True, "edge_executable": "cmd_start_default", "pid": proc.pid}


def _query_process_image_name(pid: int | None) -> str | None:
    if pid is None:
        return None
    try:
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
        kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL

        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if not handle:
            return None
        try:
            size = wintypes.DWORD(32768)
            buffer = ctypes.create_unicode_buffer(size.value)
            ok = kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size))
            if not ok:
                return None
            return buffer.value
        finally:
            kernel32.CloseHandle(handle)
    except Exception:
        return None


def _process_name_from_pid(pid: int | None) -> str | None:
    process_image = _query_process_image_name(pid)
    return Path(process_image).name.lower() if process_image else None


def _safe_window_summary(window: Any) -> dict[str, Any]:
    try:
        title = window.window_text() or ""
    except Exception:
        title = ""
    try:
        class_name = window.class_name() or ""
    except Exception:
        class_name = ""
    try:
        handle = int(window.handle)
    except Exception:
        handle = None
    try:
        pid = int(window.process_id())
    except Exception:
        pid = None
    process_name = _process_name_from_pid(pid)
    try:
        visible = bool(window.is_visible())
    except Exception:
        visible = None
    try:
        enabled = bool(window.is_enabled())
    except Exception:
        enabled = None
    try:
        rect = window.rectangle()
        rectangle = {
            "left": int(rect.left),
            "top": int(rect.top),
            "right": int(rect.right),
            "bottom": int(rect.bottom),
        }
    except Exception:
        rectangle = None
    title_lower = title.lower()
    class_lower = class_name.lower()
    return {
        "source": "uia",
        "handle": handle,
        "pid": pid,
        "process_name": process_name,
        "process_is_msedge": process_name == "msedge.exe",
        "class_name": class_name,
        "class_is_chromium_widget": class_lower == "chrome_widgetwin_1",
        "title_sha256": _sha256_text(title) if title else None,
        "title_length": len(title),
        "title_has_chatgpt": "chatgpt" in title_lower or "chat gpt" in title_lower,
        "title_has_openai": "openai" in title_lower,
        "title_has_edge": "edge" in title_lower or "microsoft edge" in title_lower,
        "visible": visible,
        "enabled": enabled,
        "rectangle": rectangle,
    }


def _summary_is_visible_enabled(summary: dict[str, Any]) -> bool:
    return summary.get("visible") is not False and summary.get("enabled") is not False


def _summary_is_msedge(summary: dict[str, Any]) -> bool:
    if summary.get("process_is_msedge") is True:
        return True
    if summary.get("title_has_edge") is True and summary.get("class_is_chromium_widget") is True:
        return True
    return False


def _with_reason(summary: dict[str, Any], reason: str) -> dict[str, Any]:
    copy = dict(summary)
    copy["candidate_reason"] = reason
    return copy


def select_candidate_summaries(summaries: list[dict[str, Any]], target_url: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Select safe Edge focus candidates from sanitized summaries."""
    visible_summaries = [s for s in summaries if _summary_is_visible_enabled(s)]
    chatgpt_candidates = [s for s in visible_summaries if _summary_is_msedge(s) and s.get("title_has_chatgpt") is True]
    if chatgpt_candidates:
        return [_with_reason(s, "msedge_title_has_chatgpt") for s in chatgpt_candidates], {
            "selection_mode": "chatgpt_title",
            "chatgpt_candidate_count": len(chatgpt_candidates),
            "edge_candidate_count": len([s for s in visible_summaries if _summary_is_msedge(s)]),
            "ambiguous": False,
        }

    edge_candidates = [s for s in visible_summaries if _summary_is_msedge(s)]
    if is_root_chatgpt_target(target_url) and len(edge_candidates) == 1:
        return [_with_reason(edge_candidates[0], "root_target_single_msedge_window")], {
            "selection_mode": "root_target_single_edge_window",
            "chatgpt_candidate_count": 0,
            "edge_candidate_count": 1,
            "ambiguous": False,
        }

    if is_root_chatgpt_target(target_url) and len(edge_candidates) > 1:
        return [], {
            "selection_mode": "root_target_ambiguous_edge_windows",
            "chatgpt_candidate_count": 0,
            "edge_candidate_count": len(edge_candidates),
            "ambiguous": True,
        }

    return [], {
        "selection_mode": "no_matching_chatgpt_edge_window",
        "chatgpt_candidate_count": 0,
        "edge_candidate_count": len(edge_candidates),
        "ambiguous": False,
    }


def _load_pywinauto_desktop() -> Any:
    try:
        from pywinauto import Desktop  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"pywinauto is not available: {exc}") from exc
    return Desktop


def _uia_candidate_windows(target_url: str) -> tuple[list[Any], list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    Desktop = _load_pywinauto_desktop()
    desktop = Desktop(backend="uia")
    windows = desktop.windows()
    summaries = [_safe_window_summary(window) for window in windows]
    selected_summaries, selection = select_candidate_summaries(summaries, target_url)
    selected_handles = {summary.get("handle") for summary in selected_summaries}
    candidates = []
    for window, summary in zip(windows, summaries):
        if summary.get("handle") in selected_handles:
            candidates.append(window)
    return candidates, selected_summaries, selection, summaries[:25]


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


def _get_window_rect(hwnd: int) -> dict[str, int] | None:
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        rect = wintypes.RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return None
        return {"left": int(rect.left), "top": int(rect.top), "right": int(rect.right), "bottom": int(rect.bottom)}
    except Exception:
        return None


def _win32_visible_top_level_summaries() -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def callback(hwnd: int, lparam: int) -> bool:
        try:
            if not user32.IsWindowVisible(hwnd):
                return True
            pid = wintypes.DWORD(0)
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            pid_value = int(pid.value) if pid.value else None
            process_name = _process_name_from_pid(pid_value)
            title = _get_window_text(hwnd)
            title_lower = title.lower()
            rectangle = _get_window_rect(hwnd)
            summaries.append(
                {
                    "source": "win32",
                    "handle": int(hwnd),
                    "pid": pid_value,
                    "process_name": process_name,
                    "process_is_msedge": process_name == "msedge.exe",
                    "class_name": None,
                    "class_is_chromium_widget": None,
                    "title_sha256": _sha256_text(title) if title else None,
                    "title_length": len(title),
                    "title_has_chatgpt": "chatgpt" in title_lower or "chat gpt" in title_lower,
                    "title_has_openai": "openai" in title_lower,
                    "title_has_edge": "edge" in title_lower or "microsoft edge" in title_lower,
                    "visible": True,
                    "enabled": True,
                    "rectangle": rectangle,
                }
            )
        except Exception:
            return True
        return True

    user32.EnumWindows(EnumWindowsProc(callback), 0)
    return summaries


def _focus_win32_handle(hwnd: int) -> tuple[bool, str]:
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        SW_RESTORE = 9
        user32.ShowWindow(int(hwnd), SW_RESTORE)
        time.sleep(0.1)
        ok = bool(user32.SetForegroundWindow(int(hwnd)))
        if ok:
            return True, "win32_set_foreground_window_succeeded"
        return False, "win32_set_foreground_window_returned_false"
    except Exception as exc:
        return False, f"win32_focus_exception:{exc}"


def _try_uia_focus(target_url: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    detail: dict[str, Any] = {}
    try:
        candidates, selected_summaries, selection, observed = _uia_candidate_windows(target_url)
        detail = {
            "selection": selection,
            "candidate_count": len(selected_summaries),
            "observed_windows_sample": observed,
        }
    except Exception as exc:
        detail = {"error": str(exc), "selection": {"selection_mode": "uia_exception", "ambiguous": False}}
        return None, detail

    if (detail.get("selection") or {}).get("ambiguous"):
        return {
            "status": "FAIL_OR_BLOCKED",
            "error": "ambiguous_edge_window_candidates",
            "focus_backend": "uia",
            **detail,
        }, detail

    if not candidates:
        return None, detail

    selected = candidates[0]
    selected_summary = selected_summaries[0]
    try:
        selected.set_focus()
        return {
            "status": "PASS",
            "normal_edge_attached": True,
            "edge_focused": True,
            "focus_backend": "uia",
            "selected_target_window": selected_summary,
            **detail,
        }, detail
    except Exception as exc:
        return {
            "status": "FAIL_OR_BLOCKED",
            "normal_edge_attached": True,
            "edge_focused": False,
            "focus_backend": "uia",
            "selected_target_window": selected_summary,
            "error": f"focus_failed:{exc}",
            **detail,
        }, detail


def _try_win32_focus(target_url: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    try:
        summaries = _win32_visible_top_level_summaries()
        selected_summaries, selection = select_candidate_summaries(summaries, target_url)
    except Exception as exc:
        detail = {"error": str(exc), "selection": {"selection_mode": "win32_exception", "ambiguous": False}}
        return None, detail

    detail = {
        "selection": selection,
        "candidate_count": len(selected_summaries),
        "observed_windows_sample": summaries[:25],
    }
    if selection.get("ambiguous"):
        return {
            "status": "FAIL_OR_BLOCKED",
            "error": "ambiguous_edge_window_candidates",
            "focus_backend": "win32",
            **detail,
        }, detail
    if not selected_summaries:
        return None, detail

    selected_summary = selected_summaries[0]
    hwnd = selected_summary.get("handle")
    ok, reason = _focus_win32_handle(int(hwnd)) if hwnd is not None else (False, "missing_window_handle")
    if ok:
        return {
            "status": "PASS",
            "normal_edge_attached": True,
            "edge_focused": True,
            "focus_backend": "win32",
            "selected_target_window": selected_summary,
            **detail,
        }, detail
    return {
        "status": "FAIL_OR_BLOCKED",
        "normal_edge_attached": True,
        "edge_focused": False,
        "focus_backend": "win32",
        "selected_target_window": selected_summary,
        "error": reason,
        **detail,
    }, detail


def focus_chatgpt_edge_target(*, target_url: str, allow_launch: bool = False, timeout_seconds: int = 30) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "FAIL_OR_BLOCKED",
        "normal_edge_started": False,
        "normal_edge_attached": False,
        "edge_focused": False,
        "candidate_count": 0,
        "selected_target_window": None,
        "selection": None,
        "uia_detail": None,
        "win32_detail": None,
        "observed_windows_sample": [],
        **SAFE_EDGE_PREFLIGHT_CAPABILITIES,
    }

    launch_info: dict[str, Any] | None = None
    deadline = time.time() + max(1, timeout_seconds)
    last_uia_detail: dict[str, Any] | None = None
    last_win32_detail: dict[str, Any] | None = None
    first_error: str | None = None

    while time.time() <= deadline:
        uia_outcome, uia_detail = _try_uia_focus(target_url)
        last_uia_detail = uia_detail
        if uia_outcome is not None:
            result.update(uia_outcome)
            result["uia_detail"] = uia_detail
            result["win32_detail"] = last_win32_detail
            return result

        win32_outcome, win32_detail = _try_win32_focus(target_url)
        last_win32_detail = win32_detail
        if win32_outcome is not None:
            result.update(win32_outcome)
            result["uia_detail"] = uia_detail
            result["win32_detail"] = win32_detail
            return result

        if first_error is None:
            first_error = str(uia_detail.get("error") or win32_detail.get("error") or "no_focus_candidate")

        if allow_launch and launch_info is None:
            try:
                launch_info = start_normal_edge(target_url)
                result.update(launch_info)
            except Exception as exc:
                result["error"] = f"edge_launch_failed:{exc}"
                result["uia_detail"] = last_uia_detail
                result["win32_detail"] = last_win32_detail
                return result
        time.sleep(1.0)

    result["uia_detail"] = last_uia_detail
    result["win32_detail"] = last_win32_detail
    result["selection"] = (last_win32_detail or last_uia_detail or {}).get("selection")
    result["observed_windows_sample"] = (last_win32_detail or last_uia_detail or {}).get("observed_windows_sample", [])
    result["candidate_count"] = int((last_win32_detail or last_uia_detail or {}).get("candidate_count") or 0)
    result["error"] = f"chatgpt_edge_window_not_found:{first_error or 'no_focus_candidate'}"
    return result
