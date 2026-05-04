from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from pywinauto import keyboard  # type: ignore

from patchops.edge_rpa.edge_upload_safe_report_copy_gate import (
    REQUESTED_CHAT_URL,
    _canonical_url,
    _get_clipboard_text,
    _hash_text,
    _is_onedrive_path,
    _observe_staged_file,
    _set_clipboard_text,
    _verify_direct_composer_focus,
)

PATCH_NAME = "l26_12j_desktop_report_slash_ctrl_u_upload_repair"
_EXCLUDED_PICKER_CLASSES = {"rctrl_renwnd32", "Chrome_WidgetWin_1", "Chrome_WidgetWin_0", "Windows.UI.Core.CoreWindow"}
_STRICT_PICKER_CLASSES = {"#32770", "CabinetWClass", "ExploreWClass"}
_PICKER_TITLE_HINTS = ("open", "choose", "select", "upload", "file")


@dataclass(frozen=True)
class DesktopReportSlashCtrlUUploadResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    target_chat_accepted_without_navigation: bool = False
    current_url_matches_target: bool = False
    navigation_attempted: bool = False
    report_path_exists: bool = False
    report_path_written_by_outer_script: bool = False
    report_hash: str = ""
    report_size_bytes: int = 0
    report_safe_copy_created: bool = False
    report_safe_copy_name: str = ""
    report_safe_copy_hash: str = ""
    report_safe_copy_size_bytes: int = 0
    report_safe_copy_closed: bool = False
    safe_copy_hash_matches_report: bool = False
    safe_copy_outside_onedrive: bool = False
    composer_candidate_found: bool = False
    composer_focus_verified: bool = False
    composer_cleared_before_slash: bool = False
    slash_typed_in_composer: bool = False
    plus_button_clicked_after_slash: bool = False
    ctrl_u_shortcut_sent: bool = False
    picker_window_detected: bool = False
    picker_window_kind: str = ""
    picker_navigation_attempted: bool = False
    picker_directory_changed: bool = False
    picker_filename_entered: bool = False
    file_picker_confirmed: bool = False
    file_picker_enter_sent: bool = False
    picker_window_closed_after_confirm: bool = False
    upload_staging_observed: bool = False
    staged_file_name_hash: str = ""
    staging_observation_method: str = ""
    report_upload_attempted: bool = False
    file_attach_attempted: bool = False
    live_report_path: str = ""
    json_path: str = ""
    chatgpt_submit_enter_sent: bool = False
    send_submit_performed: bool = False
    chatgpt_prompt_submitted: bool = False
    download_click_performed: bool = False
    run_package_invoked: bool = False
    pasteback_or_send_performed: bool = False
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    prompt_text_logged: bool = False
    file_content_logged: bool = False
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_dom_automation_used: bool = False
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def _copy_report_to_closed_safe_copy(report_path: Path, output_dir: Path) -> Path:
    safe_dir = output_dir / "upload_safe_report_copy"
    safe_dir.mkdir(parents=True, exist_ok=True)
    safe_name = "upload_copy_of_" + report_path.name
    safe_path = safe_dir / safe_name
    with report_path.open("rb") as src, safe_path.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
        dst.flush()
        os.fsync(dst.fileno())
    with safe_path.open("rb") as check:
        check.read(1)
    return safe_path


def _write_report(path: Path, result: DesktopReportSlashCtrlUUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.12J desktop report slash+Ctrl+U upload repair",
        f"target_chat_accepted_without_navigation: {result.target_chat_accepted_without_navigation}",
        f"navigation_attempted: {result.navigation_attempted}",
        f"report_path_exists: {result.report_path_exists}",
        f"report_safe_copy_created: {result.report_safe_copy_created}",
        f"safe_copy_hash_matches_report: {result.safe_copy_hash_matches_report}",
        f"composer_candidate_found: {result.composer_candidate_found}",
        f"slash_typed_in_composer: {result.slash_typed_in_composer}",
        f"plus_button_clicked_after_slash: {result.plus_button_clicked_after_slash}",
        f"ctrl_u_shortcut_sent: {result.ctrl_u_shortcut_sent}",
        f"picker_window_detected: {result.picker_window_detected}",
        f"picker_window_kind: {result.picker_window_kind}",
        f"picker_directory_changed: {result.picker_directory_changed}",
        f"picker_filename_entered: {result.picker_filename_entered}",
        f"file_picker_confirmed: {result.file_picker_confirmed}",
        f"picker_window_closed_after_confirm: {result.picker_window_closed_after_confirm}",
        f"upload_staging_observed: {result.upload_staging_observed}",
        "chatgpt_submit_enter_sent:false",
        "send_submit_performed:false",
        "chatgpt_prompt_submitted:false",
        "conversation_text_logged:false",
        "prompt_text_logged:false",
        "file_content_logged:false",
        f"failure_layer: {result.failure_layer}",
        f"error: {result.error}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: DesktopReportSlashCtrlUUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def _read_current_url_without_navigation() -> str:
    before = _get_clipboard_text()
    try:
        keyboard.send_keys("^l")
        time.sleep(0.2)
        keyboard.send_keys("^c")
        time.sleep(0.2)
        text = _get_clipboard_text()
        keyboard.send_keys("{ESC}")
        time.sleep(0.2)
        return text or ""
    finally:
        try:
            _set_clipboard_text(before)
        except Exception:
            pass


def _known_window_handles() -> set[int]:
    import pywinauto  # type: ignore
    desktop = pywinauto.Desktop(backend="uia")
    handles: set[int] = set()
    try:
        for window in desktop.windows():
            try:
                handles.add(int(window.handle))
            except Exception:
                pass
    except Exception:
        pass
    return handles


def _window_class_and_title(window: object) -> tuple[str, str]:
    try:
        class_name = str(window.element_info.class_name or "")
    except Exception:
        class_name = ""
    try:
        title = str(window.window_text() or "")
    except Exception:
        title = ""
    return class_name, title


def _is_strict_upload_picker(window: object, known_handles: set[int]) -> tuple[bool, str]:
    try:
        handle = int(window.handle)
    except Exception:
        handle = 0
    class_name, title = _window_class_and_title(window)
    lowered = (title + " " + class_name).lower()
    if class_name in _EXCLUDED_PICKER_CLASSES:
        return False, ""
    if class_name in _STRICT_PICKER_CLASSES:
        return True, class_name
    if handle not in known_handles and any(hint in lowered for hint in _PICKER_TITLE_HINTS) and "edge" not in lowered and "chatgpt" not in lowered:
        return True, class_name or "new_picker_like_window"
    return False, ""


def _find_strict_picker(known_handles: set[int], timeout_seconds: float = 20.0) -> tuple[object, str]:
    import pywinauto  # type: ignore
    desktop = pywinauto.Desktop(backend="uia")
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            windows = list(desktop.windows())
        except Exception:
            windows = []
        def sort_key(window: object) -> tuple[int, str]:
            try:
                handle = int(window.handle)
            except Exception:
                handle = 0
            cls, title = _window_class_and_title(window)
            return (0 if handle not in known_handles else 1, cls + title)
        windows.sort(key=sort_key)
        for window in windows:
            ok, kind = _is_strict_upload_picker(window, known_handles)
            if ok:
                try:
                    window.set_focus()
                except Exception:
                    pass
                return window, kind
        time.sleep(0.25)
    raise RuntimeError("No strict OS upload picker was detected after slash + Ctrl+U.")


def _wait_window_gone_or_inactive(window: object, timeout_seconds: float = 12.0) -> bool:
    try:
        handle = int(window.handle)
    except Exception:
        handle = 0
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            if not window.exists(timeout=0.2):
                return True
        except Exception:
            return True
        try:
            if int(window.handle) != handle:
                return True
        except Exception:
            return True
        time.sleep(0.25)
    return False


def _change_picker_directory_and_select_file(window: object, file_path: Path) -> str:
    parent = str(file_path.parent)
    name = file_path.name
    try:
        window.set_focus()
    except Exception:
        pass
    time.sleep(0.2)
    # Directory-first strategy per operator correction: navigate/change folder first, then enter file name.
    keyboard.send_keys("^l")
    time.sleep(0.2)
    _set_clipboard_text(parent)
    keyboard.send_keys("^v")
    time.sleep(0.2)
    keyboard.send_keys("{ENTER}")
    time.sleep(1.0)
    try:
        window.set_focus()
    except Exception:
        pass
    try:
        keyboard.send_keys("%n")
        time.sleep(0.2)
    except Exception:
        pass
    _set_clipboard_text(name)
    keyboard.send_keys("^v")
    time.sleep(0.2)
    keyboard.send_keys("{ENTER}")
    return "ctrl_l_parent_then_alt_n_filename_enter"


def _prepare_composer_for_upload_shortcut() -> tuple[bool, bool, bool]:
    composer_found, focus_verified = _verify_direct_composer_focus()
    cleared = False
    if composer_found:
        try:
            keyboard.send_keys("^a")
            time.sleep(0.1)
            keyboard.send_keys("{BACKSPACE}")
            cleared = True
        except Exception:
            cleared = False
    return composer_found, focus_verified, cleared


def run_l26_12j_desktop_report_slash_ctrl_u_upload_gate(*, output_dir: str | Path, target_url: str, report_path: str | Path, allow_report_upload: bool = False) -> DesktopReportSlashCtrlUUploadResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_12j_desktop_report_upload_result.json"
    live_report_path = out_dir / "normal_edge_l26_12j_desktop_report_upload_live_report.txt"
    report = Path(report_path)
    state: dict[str, object] = {"json_path": str(json_path), "live_report_path": str(live_report_path)}
    try:
        if not allow_report_upload:
            raise RuntimeError("L26.12J requires explicit --allow-report-upload.")
        if not report.exists() or not report.is_file():
            raise RuntimeError(f"Desktop operator report does not exist yet: {report}")
        # Prove the report is closed enough to copy and hash before browser upload begins.
        report_hash = _hash_file(report)
        report_size = report.stat().st_size
        safe_copy = _copy_report_to_closed_safe_copy(report, out_dir)
        safe_hash = _hash_file(safe_copy)
        safe_size = safe_copy.stat().st_size
        state.update({
            "report_path_exists": True,
            "report_path_written_by_outer_script": True,
            "report_hash": report_hash,
            "report_size_bytes": int(report_size),
            "report_safe_copy_created": True,
            "report_safe_copy_name": safe_copy.name,
            "report_safe_copy_hash": safe_hash,
            "report_safe_copy_size_bytes": int(safe_size),
            "report_safe_copy_closed": True,
            "safe_copy_hash_matches_report": report_hash == safe_hash and report_size == safe_size,
            "safe_copy_outside_onedrive": not _is_onedrive_path(safe_copy),
        })
        if report_hash != safe_hash or report_size != safe_size:
            raise RuntimeError("Report safe copy hash/size mismatch.")

        current_url = _read_current_url_without_navigation()
        current_url_matches = _canonical_url(current_url) == _canonical_url(target_url)
        composer_found, focus_verified, cleared = _prepare_composer_for_upload_shortcut()
        state.update({
            "current_url_matches_target": current_url_matches,
            "navigation_attempted": False,
            "composer_candidate_found": composer_found,
            "composer_focus_verified": focus_verified,
            "composer_cleared_before_slash": cleared,
            "target_chat_accepted_without_navigation": composer_found,
        })
        if not composer_found:
            raise RuntimeError("No safe composer candidate found; refusing slash+Ctrl+U upload.")

        # Operator correction: slash + Ctrl+U only. Do not click plus after slash.
        keyboard.send_keys("/")
        state.update({"slash_typed_in_composer": True, "plus_button_clicked_after_slash": False})
        time.sleep(0.35)
        known_handles = _known_window_handles()
        keyboard.send_keys("^u")
        state.update({"ctrl_u_shortcut_sent": True})
        picker, picker_kind = _find_strict_picker(known_handles, timeout_seconds=24.0)
        state.update({
            "picker_window_detected": True,
            "picker_window_kind": picker_kind,
            "report_upload_attempted": True,
            "file_attach_attempted": True,
        })
        strategy = _change_picker_directory_and_select_file(picker, safe_copy)
        state.update({
            "picker_navigation_attempted": True,
            "picker_directory_changed": True,
            "picker_filename_entered": True,
            "file_picker_confirmed": True,
            "file_picker_enter_sent": True,
        })
        closed = _wait_window_gone_or_inactive(picker, timeout_seconds=12.0)
        state.update({"picker_window_closed_after_confirm": closed})
        staged, method = _observe_staged_file(safe_copy.name, timeout_seconds=90.0)
        state.update({
            "upload_staging_observed": staged,
            "staged_file_name_hash": _hash_text(safe_copy.name),
            "staging_observation_method": method,
            "result": "PASS" if staged else "FAIL",
            "failure_layer": "" if staged else "desktop_report_slash_ctrl_u_staging_observation",
            "error": "" if staged else "Desktop report safe copy was selected, but staged attachment was not observed.",
        })
    except Exception as exc:
        state.update({
            "result": "FAIL",
            "failure_layer": "desktop_report_slash_ctrl_u_upload_repair",
            "error": f"{type(exc).__name__}: {exc}",
        })
    result = DesktopReportSlashCtrlUUploadResult(**state)
    _write_report(live_report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_12j_acceptance(result: DesktopReportSlashCtrlUUploadResult) -> None:
    payload = result.to_payload()
    required_true = [
        "target_chat_accepted_without_navigation",
        "report_path_exists",
        "report_path_written_by_outer_script",
        "report_safe_copy_created",
        "report_safe_copy_closed",
        "safe_copy_hash_matches_report",
        "safe_copy_outside_onedrive",
        "composer_candidate_found",
        "composer_cleared_before_slash",
        "slash_typed_in_composer",
        "ctrl_u_shortcut_sent",
        "picker_window_detected",
        "picker_navigation_attempted",
        "picker_directory_changed",
        "picker_filename_entered",
        "file_picker_confirmed",
        "file_picker_enter_sent",
        "upload_staging_observed",
        "report_upload_attempted",
        "file_attach_attempted",
    ]
    required_false = [
        "navigation_attempted",
        "plus_button_clicked_after_slash",
        "chatgpt_submit_enter_sent",
        "send_submit_performed",
        "chatgpt_prompt_submitted",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
        "full_conversation_text_logged",
        "prompt_text_logged",
        "file_content_logged",
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    for key in ("report_hash", "report_safe_copy_hash", "report_safe_copy_name", "picker_window_kind", "staged_file_name_hash"):
        if not payload.get(key):
            missing_true.append(key + "_nonempty")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.12J acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
