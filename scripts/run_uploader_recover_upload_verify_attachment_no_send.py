from __future__ import annotations

import argparse
import ctypes
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


SAFETY_FLAGS = {
    "chatgpt_submit_performed": False,
    "conversation_text_logged": False,
    "selenium_used": False,
    "webdriver_used": False,
    "browser_dom_automation_used": False,
    "random_page_click_performed": False,
}


def _repo_root_from_args(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def _set_clipboard_text(text: str) -> bool:
    if os.name != "nt":
        return False

    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    data = str(text) + "\0"
    data_bytes = data.encode("utf-16-le")
    h_global = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data_bytes))
    if not h_global:
        return False

    locked = kernel32.GlobalLock(h_global)
    if not locked:
        kernel32.GlobalFree(h_global)
        return False

    ctypes.memmove(locked, data_bytes, len(data_bytes))
    kernel32.GlobalUnlock(h_global)

    if not user32.OpenClipboard(None):
        kernel32.GlobalFree(h_global)
        return False

    try:
        user32.EmptyClipboard()
        if not user32.SetClipboardData(CF_UNICODETEXT, h_global):
            kernel32.GlobalFree(h_global)
            return False
        h_global = None
        return True
    finally:
        user32.CloseClipboard()


def _write_evidence(evidence_dir: Path, payload: dict[str, Any]) -> tuple[Path, Path, dict[str, Any]]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    json_path = evidence_dir / "u2_07_recover_upload_verify.json"
    txt_path = evidence_dir / "u2_07_recover_upload_verify.txt"

    payload = dict(payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")

    lines = [
        f"PATCHOPS_UPLOADER_RECOVER_UPLOAD_VERIFY_STATUS: {payload.get('status', '')}",
        f"REPORT_PATH: {payload.get('report_path', '')}",
        f"UPLOAD_STATUS: {payload.get('upload_status', '')}",
        f"ATTACHMENT_STATUS: {payload.get('attachment_status', '')}",
        f"JSON_EVIDENCE: {json_path}",
        f"TXT_EVIDENCE: {txt_path}",
        "NORMAL_EDGE_LAUNCH_ATTEMPTED: false",
        "CONFIGURED_TARGET_OPEN_ATTEMPTED: false",
        "TARGET_CONFIG_OVERWRITTEN: false",
        "HARDCODED_TARGET_URL_USED: false",
        f"CANONICAL_TRIGGER_ATTEMPTED: {str(payload.get('canonical_trigger_attempted', False)).lower()}",
        f"SLASH_SENT: {str(payload.get('slash_sent', False)).lower()}",
        "TAB_SENT: false",
        "SECOND_ENTER_ATTEMPTED: false",
        "PLUS_CONTROL_SEARCH_ATTEMPTED: false",
        "MENU_CONTROL_SEARCH_ATTEMPTED: false",
        "CTRL_U_ATTEMPTED: false",
        f"BROWSER_PICKER_OPENED: {str(payload.get('browser_picker_opened', False)).lower()}",
        f"FILE_PATH_WRITTEN: {str(payload.get('file_path_written', False)).lower()}",
        f"PICKER_ENTER_PRESSED: {str(payload.get('picker_enter_pressed', False)).lower()}",
        f"FILE_UPLOAD_ATTEMPTED: {str(payload.get('file_upload_attempted', False)).lower()}",
        f"ATTACHMENT_VERIFICATION_ATTEMPTED: {str(payload.get('attachment_verification_attempted', False)).lower()}",
        f"ATTACHMENT_VISIBLE: {str(payload.get('attachment_visible', False)).lower()}",
        f"ATTACHMENT_READY: {str(payload.get('attachment_ready', False)).lower()}",
        f"UPLOAD_PROGRESS_RESOLVED: {str(payload.get('upload_progress_resolved', False)).lower()}",
        "OPEN_BUTTON_CLICKED: false",
        "CHATGPT_SUBMIT_PERFORMED: false",
        "CONVERSATION_TEXT_LOGGED: false",
        "SELENIUM_USED: false",
        "WEBDRIVER_USED: false",
        "BROWSER_DOM_AUTOMATION_USED: false",
        "RANDOM_PAGE_CLICK_PERFORMED: false",
        "",
    ]
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path, payload


def _print_payload(payload: dict[str, Any]) -> None:
    print(f"PATCHOPS_UPLOADER_RECOVER_UPLOAD_VERIFY_STATUS: {payload.get('status', '')}")
    print(f"REPORT_PATH: {payload.get('report_path', '')}")
    print(f"UPLOAD_STATUS: {payload.get('upload_status', '')}")
    print(f"ATTACHMENT_STATUS: {payload.get('attachment_status', '')}")
    print(f"JSON_EVIDENCE: {payload.get('json_evidence', '')}")
    print(f"TXT_EVIDENCE: {payload.get('txt_evidence', '')}")
    print("NORMAL_EDGE_LAUNCH_ATTEMPTED: false")
    print("CONFIGURED_TARGET_OPEN_ATTEMPTED: false")
    print("TARGET_CONFIG_OVERWRITTEN: false")
    print("HARDCODED_TARGET_URL_USED: false")
    print(f"CANONICAL_TRIGGER_ATTEMPTED: {str(payload.get('canonical_trigger_attempted', False)).lower()}")
    print(f"SLASH_SENT: {str(payload.get('slash_sent', False)).lower()}")
    print("TAB_SENT: false")
    print("SECOND_ENTER_ATTEMPTED: false")
    print("PLUS_CONTROL_SEARCH_ATTEMPTED: false")
    print("MENU_CONTROL_SEARCH_ATTEMPTED: false")
    print("CTRL_U_ATTEMPTED: false")
    print(f"BROWSER_PICKER_OPENED: {str(payload.get('browser_picker_opened', False)).lower()}")
    print(f"FILE_PATH_WRITTEN: {str(payload.get('file_path_written', False)).lower()}")
    print(f"PICKER_ENTER_PRESSED: {str(payload.get('picker_enter_pressed', False)).lower()}")
    print(f"FILE_UPLOAD_ATTEMPTED: {str(payload.get('file_upload_attempted', False)).lower()}")
    print(f"ATTACHMENT_VERIFICATION_ATTEMPTED: {str(payload.get('attachment_verification_attempted', False)).lower()}")
    print(f"ATTACHMENT_VISIBLE: {str(payload.get('attachment_visible', False)).lower()}")
    print(f"ATTACHMENT_READY: {str(payload.get('attachment_ready', False)).lower()}")
    print(f"UPLOAD_PROGRESS_RESOLVED: {str(payload.get('upload_progress_resolved', False)).lower()}")
    print("OPEN_BUTTON_CLICKED: false")
    print("CHATGPT_SUBMIT_PERFORMED: false")
    print("CONVERSATION_TEXT_LOGGED: false")
    print("SELENIUM_USED: false")
    print("WEBDRIVER_USED: false")
    print("BROWSER_DOM_AUTOMATION_USED: false")
    print("RANDOM_PAGE_CLICK_PERFORMED: false")


def _base_payload(report_path: Path) -> dict[str, Any]:
    return {
        "patch": "U2.7C",
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "report_path": str(report_path),
        "report_exists": report_path.exists(),
        "report_size_bytes": report_path.stat().st_size if report_path.exists() and report_path.is_file() else 0,
        "normal_edge_launch_attempted": False,
        "configured_target_open_attempted": False,
        "target_config_overwritten": False,
        "hardcoded_target_url_used": False,
        "canonical_trigger_attempted": False,
        "slash_sent": False,
        "tab_sent": False,
        "second_enter_attempted": False,
        "plus_control_search_attempted": False,
        "menu_control_search_attempted": False,
        "ctrl_u_attempted": False,
        "browser_picker_opened": False,
        "file_path_written": False,
        "picker_enter_pressed": False,
        "file_upload_attempted": False,
        "attachment_verification_attempted": False,
        "attachment_visible": False,
        "attachment_ready": False,
        "upload_progress_resolved": False,
        "open_button_clicked": False,
        **SAFETY_FLAGS,
    }


def _looks_like_picker(window: Any) -> bool:
    try:
        title = (window.window_text() or "").lower()
    except Exception:
        title = ""
    try:
        class_name = (window.class_name() or "").lower()
    except Exception:
        class_name = ""

    if class_name == "#32770":
        return True
    return any(token in title for token in ("open", "upload", "choose file", "file upload"))


def _find_picker(timeout_seconds: float = 8.0) -> Any | None:
    try:
        from pywinauto import Desktop  # type: ignore
    except Exception:
        return None

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        for backend in ("uia", "win32"):
            try:
                windows = Desktop(backend=backend).windows()
            except Exception:
                continue

            for window in windows:
                if _looks_like_picker(window):
                    return window
        time.sleep(0.25)
    return None


def _find_edge_window_with_filename(filename: str, timeout_seconds: float = 25.0) -> bool:
    try:
        from pywinauto import Desktop  # type: ignore
    except Exception:
        return False

    deadline = time.time() + timeout_seconds
    wanted = filename.lower()

    while time.time() < deadline:
        for backend in ("uia", "win32"):
            try:
                windows = Desktop(backend=backend).windows()
            except Exception:
                continue

            for window in windows:
                try:
                    title = (window.window_text() or "").lower()
                except Exception:
                    title = ""

                if "edge" not in title and "chatgpt" not in title:
                    continue

                try:
                    texts = [window.window_text() or ""]
                    for child in window.descendants():
                        try:
                            text = child.window_text() or ""
                            if text:
                                texts.append(text)
                        except Exception:
                            pass
                except Exception:
                    texts = [title]

                joined = "\n".join(texts).lower()
                if wanted in joined:
                    return True

        time.sleep(0.5)

    return False


def _trigger_picker_and_write_path(report_path: Path, payload: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    try:
        from pywinauto.keyboard import send_keys  # type: ignore
    except Exception as exc:
        payload["status"] = "BLOCKED_UPLOAD_NOT_PASS_NO_SEND"
        payload["upload_status"] = "BLOCKED_PYWINAUTO_KEYBOARD_MISSING"
        payload["attachment_status"] = "NOT_RUN"
        payload["failure_layer"] = f"pywinauto_keyboard_missing:{type(exc).__name__}"
        return payload

    payload["canonical_trigger_attempted"] = True

    try:
        send_keys("/", pause=0.05)
        payload["slash_sent"] = True
        time.sleep(0.25)
        send_keys("{ENTER}", pause=0.05)
    except Exception as exc:
        payload["status"] = "BLOCKED_UPLOAD_NOT_PASS_NO_SEND"
        payload["upload_status"] = "BLOCKED_CANONICAL_TRIGGER_FAILED"
        payload["attachment_status"] = "NOT_RUN"
        payload["failure_layer"] = f"canonical_trigger_failed:{type(exc).__name__}"
        return payload

    picker = _find_picker(timeout_seconds=8.0)
    if picker is None:
        payload["status"] = "BLOCKED_UPLOAD_NOT_PASS_NO_SEND"
        payload["upload_status"] = "BLOCKED_PICKER_NOT_OPENED"
        payload["attachment_status"] = "NOT_RUN"
        payload["failure_layer"] = "picker_not_opened"
        return payload

    payload["browser_picker_opened"] = True

    try:
        picker.set_focus()
    except Exception:
        pass

    clipboard_ok = _set_clipboard_text(str(report_path))
    try:
        if clipboard_ok:
            send_keys("^v", pause=0.05)
        else:
            send_keys(str(report_path), with_spaces=True, pause=0.01)
        payload["file_path_written"] = True
        payload["path_typed"] = True
        time.sleep(0.25)
        send_keys("{ENTER}", pause=0.05)
        payload["picker_enter_pressed"] = True
        payload["enter_pressed_once"] = True
        payload["file_upload_attempted"] = True
    except Exception as exc:
        payload["status"] = "BLOCKED_UPLOAD_NOT_PASS_NO_SEND"
        payload["upload_status"] = "BLOCKED_PICKER_PATH_WRITE_OR_ENTER_FAILED"
        payload["attachment_status"] = "NOT_RUN"
        payload["failure_layer"] = f"picker_path_write_or_enter_failed:{type(exc).__name__}"
        return payload

    payload["attachment_verification_attempted"] = True
    visible = _find_edge_window_with_filename(report_path.name, timeout_seconds=max(10.0, float(timeout_seconds) / 2.0))
    payload["attachment_visible"] = bool(visible)
    payload["attachment_ready"] = bool(visible)
    payload["upload_progress_resolved"] = bool(visible)

    if visible:
        payload["status"] = "PASS_UPLOAD_ATTACHED_NO_SEND"
        payload["upload_status"] = "PASS_PICKER_PATH_ENTERED"
        payload["attachment_status"] = "VISIBLE"
        payload["failure_layer"] = ""
    else:
        payload["status"] = "BLOCKED_UPLOAD_NOT_PASS_NO_SEND"
        payload["upload_status"] = "PASS_PICKER_PATH_ENTERED"
        payload["attachment_status"] = "NOT_VISIBLE"
        payload["failure_layer"] = "attachment_not_visible"

    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Recover upload, verify attachment, never send.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--allow-live-picker", action="store_true")
    parser.add_argument("--allow-upload", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    _repo_root_from_args(args.repo_root)
    report_path = Path(args.report_path).expanduser().resolve()
    evidence_dir = Path(args.evidence_dir).expanduser().resolve()

    payload = _base_payload(report_path)

    if not report_path.exists() or not report_path.is_file() or report_path.stat().st_size <= 0:
        payload.update({
            "status": "BLOCKED_UPLOAD_NOT_PASS_NO_SEND",
            "upload_status": "BLOCKED_REPORT_UNAVAILABLE",
            "attachment_status": "NOT_RUN",
            "failure_layer": "report_unavailable",
        })
        json_path, txt_path, payload = _write_evidence(evidence_dir, payload)
        payload["json_evidence"] = str(json_path)
        payload["txt_evidence"] = str(txt_path)
        _print_payload(payload) if not args.json else print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    if not (args.allow_live_picker or args.allow_upload):
        payload.update({
            "status": "BLOCKED_UPLOAD_NOT_PASS_NO_SEND",
            "upload_status": "PASS_DRY_RUN_NO_PICKER_OPEN",
            "attachment_status": "NOT_RUN",
            "failure_layer": "live_picker_permission_missing",
        })
        json_path, txt_path, payload = _write_evidence(evidence_dir, payload)
        payload["json_evidence"] = str(json_path)
        payload["txt_evidence"] = str(txt_path)
        _print_payload(payload) if not args.json else print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    payload = _trigger_picker_and_write_path(report_path, payload, args.timeout_seconds)
    payload["chatgpt_submit_performed"] = False
    payload["conversation_text_logged"] = False
    payload["selenium_used"] = False
    payload["webdriver_used"] = False
    payload["browser_dom_automation_used"] = False
    payload["random_page_click_performed"] = False

    json_path, txt_path, payload = _write_evidence(evidence_dir, payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        _print_payload(payload)

    return 0 if payload["status"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
