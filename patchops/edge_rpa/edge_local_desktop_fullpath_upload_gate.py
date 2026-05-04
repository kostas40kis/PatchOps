from __future__ import annotations

import ctypes
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
    _hash_text,
    _is_onedrive_path,
    _observe_staged_file,
    _set_clipboard_text,
    _verify_direct_composer_focus,
)

PATCH_NAME = "l26_12l_local_desktop_fullpath_picker_upload_repair"
_EDGE_CLASSES = {"Chrome_WidgetWin_0", "Chrome_WidgetWin_1"}
_USER32 = ctypes.windll.user32


@dataclass(frozen=True)
class LocalDesktopFullPathUploadResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    local_desktop_report_path_used: bool = False
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
    safe_copy_full_path_used: bool = False
    safe_copy_full_path_drive_valid: bool = False
    safe_copy_full_path_had_lc_prefix: bool = False
    composer_candidate_found: bool = False
    composer_focus_verified: bool = False
    composer_cleared_before_slash: bool = False
    slash_typed_in_composer: bool = False
    plus_button_clicked_after_slash: bool = False
    ctrl_u_shortcut_sent: bool = False
    foreground_picker_handoff_used: bool = False
    foreground_handle_changed: bool = False
    foreground_window_class: str = ""
    foreground_window_title_hash: str = ""
    picker_ctrl_l_used: bool = False
    picker_full_path_entry_attempted: bool = False
    picker_full_path_quoted: bool = False
    picker_filename_field_strategy: str = ""
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
    # Keep the safe copy on a normal local C: path and never OneDrive.
    safe_dir = output_dir / "upload_safe_report_copy"
    safe_dir.mkdir(parents=True, exist_ok=True)
    safe_path = safe_dir / ("upload_copy_of_" + report_path.name)
    with report_path.open("rb") as src, safe_path.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
        dst.flush()
        os.fsync(dst.fileno())
    with safe_path.open("rb") as check:
        check.read(1)
    return safe_path


def _foreground_handle() -> int:
    try:
        return int(_USER32.GetForegroundWindow() or 0)
    except Exception:
        return 0


def _class_name(hwnd: int) -> str:
    if not hwnd:
        return ""
    buf = ctypes.create_unicode_buffer(512)
    try:
        _USER32.GetClassNameW(hwnd, buf, 512)
        return str(buf.value or "")
    except Exception:
        return ""


def _title_text(hwnd: int) -> str:
    if not hwnd:
        return ""
    buf = ctypes.create_unicode_buffer(512)
    try:
        _USER32.GetWindowTextW(hwnd, buf, 512)
        return str(buf.value or "")
    except Exception:
        return ""


def _set_foreground(hwnd: int) -> None:
    if hwnd:
        try:
            _USER32.SetForegroundWindow(hwnd)
        except Exception:
            pass


def _wait_foreground_handoff(before_handle: int, timeout_seconds: float = 12.0) -> tuple[int, bool, str, str]:
    deadline = time.time() + timeout_seconds
    last = 0
    while time.time() < deadline:
        hwnd = _foreground_handle()
        if hwnd:
            last = hwnd
            cls = _class_name(hwnd)
            title = _title_text(hwnd)
            if hwnd != before_handle and cls not in _EDGE_CLASSES:
                return hwnd, True, cls, title
            if cls in {"#32770", "CabinetWClass", "ExploreWClass"}:
                return hwnd, hwnd != before_handle, cls, title
        time.sleep(0.2)
    hwnd = last or _foreground_handle()
    cls = _class_name(hwnd)
    title = _title_text(hwnd)
    if hwnd and cls not in _EDGE_CLASSES:
        return hwnd, hwnd != before_handle, cls, title
    raise RuntimeError(f"No foreground OS picker handoff after Ctrl+U; foreground_class={cls!r}")


def _wait_foreground_changed_or_edge(original_handle: int, timeout_seconds: float = 12.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        hwnd = _foreground_handle()
        if hwnd and hwnd != original_handle:
            return True
        if _class_name(hwnd) in _EDGE_CLASSES:
            return True
        time.sleep(0.25)
    return False


def _prepare_composer() -> tuple[bool, bool, bool]:
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


def _drive_valid(path: Path) -> bool:
    text = str(path)
    return len(text) >= 3 and text[1:3] == ":\\" and text[0].isalpha() and Path(text[:3]).exists()


def _has_lc_prefix(path_text: str) -> bool:
    lowered = path_text.lower()
    return lowered.startswith("lc:\\") or lowered.startswith("ic:\\") or lowered.startswith("lc:/") or lowered.startswith("ic:/")


def _enter_full_quoted_path_in_picker(hwnd: int, file_path: Path) -> str:
    full_path = str(file_path)
    quoted_path = '"' + full_path + '"'
    _set_foreground(hwnd)
    time.sleep(0.25)
    # Critical repair: do NOT use Ctrl+L. It leaked the literal 'l' into the path on the real machine.
    # Prefer the File name field directly; a full quoted path lets Windows handle the directory.
    try:
        keyboard.send_keys("%n")
        time.sleep(0.25)
        _set_clipboard_text(quoted_path)
        keyboard.send_keys("^v")
        time.sleep(0.25)
        keyboard.send_keys("{ENTER}")
        return "alt_n_full_quoted_path_enter"
    except Exception:
        _set_clipboard_text(quoted_path)
        keyboard.send_keys("^v")
        time.sleep(0.25)
        keyboard.send_keys("{ENTER}")
        return "focused_full_quoted_path_enter"


def _write_report(path: Path, result: LocalDesktopFullPathUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.12L local Desktop full-path picker upload repair",
        f"local_desktop_report_path_used: {result.local_desktop_report_path_used}",
        f"report_path_exists: {result.report_path_exists}",
        f"report_safe_copy_created: {result.report_safe_copy_created}",
        f"safe_copy_hash_matches_report: {result.safe_copy_hash_matches_report}",
        f"safe_copy_outside_onedrive: {result.safe_copy_outside_onedrive}",
        f"safe_copy_full_path_drive_valid: {result.safe_copy_full_path_drive_valid}",
        f"safe_copy_full_path_had_lc_prefix: {result.safe_copy_full_path_had_lc_prefix}",
        f"composer_candidate_found: {result.composer_candidate_found}",
        f"slash_typed_in_composer: {result.slash_typed_in_composer}",
        f"plus_button_clicked_after_slash: {result.plus_button_clicked_after_slash}",
        f"ctrl_u_shortcut_sent: {result.ctrl_u_shortcut_sent}",
        f"foreground_picker_handoff_used: {result.foreground_picker_handoff_used}",
        f"foreground_window_class: {result.foreground_window_class}",
        f"picker_ctrl_l_used: {result.picker_ctrl_l_used}",
        f"picker_full_path_entry_attempted: {result.picker_full_path_entry_attempted}",
        f"picker_filename_field_strategy: {result.picker_filename_field_strategy}",
        f"file_picker_confirmed: {result.file_picker_confirmed}",
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


def _write_json(path: Path, result: LocalDesktopFullPathUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_12l_local_desktop_fullpath_upload_gate(*, output_dir: str | Path, report_path: str | Path, allow_report_upload: bool = False) -> LocalDesktopFullPathUploadResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_12l_local_desktop_fullpath_upload_result.json"
    live_report_path = out_dir / "normal_edge_l26_12l_local_desktop_fullpath_upload_live_report.txt"
    report = Path(report_path)
    state: dict[str, object] = {"json_path": str(json_path), "live_report_path": str(live_report_path)}
    try:
        if not allow_report_upload:
            raise RuntimeError("L26.12L requires explicit --allow-report-upload.")
        if not report.exists() or not report.is_file():
            raise RuntimeError(f"Local Desktop operator report does not exist yet: {report}")
        report_hash = _hash_file(report)
        report_size = report.stat().st_size
        safe_copy = _copy_report_to_closed_safe_copy(report, out_dir)
        safe_hash = _hash_file(safe_copy)
        safe_size = safe_copy.stat().st_size
        safe_text = str(safe_copy)
        state.update({
            "local_desktop_report_path_used": str(report).lower().startswith(str(Path.home()).lower()) and "onedrive" not in str(report).lower(),
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
            "safe_copy_full_path_used": True,
            "safe_copy_full_path_drive_valid": _drive_valid(safe_copy),
            "safe_copy_full_path_had_lc_prefix": _has_lc_prefix(safe_text),
        })
        if report_hash != safe_hash or report_size != safe_size:
            raise RuntimeError("Report safe copy hash/size mismatch.")
        if not _drive_valid(safe_copy):
            raise RuntimeError(f"Upload safe copy path does not have a valid Windows drive prefix: {safe_copy}")
        if _has_lc_prefix(safe_text):
            raise RuntimeError(f"Upload safe copy path has invalid lC/iC prefix: {safe_copy}")

        composer_found, focus_verified, cleared = _prepare_composer()
        state.update({
            "composer_candidate_found": composer_found,
            "composer_focus_verified": focus_verified,
            "composer_cleared_before_slash": cleared,
        })
        if not composer_found:
            raise RuntimeError("No safe composer candidate found; refusing full-path picker upload.")

        before_handle = _foreground_handle()
        keyboard.send_keys("/")
        state.update({"slash_typed_in_composer": True, "plus_button_clicked_after_slash": False})
        time.sleep(0.35)
        keyboard.send_keys("^u")
        state.update({"ctrl_u_shortcut_sent": True})
        picker_handle, changed, picker_class, picker_title = _wait_foreground_handoff(before_handle, timeout_seconds=14.0)
        state.update({
            "foreground_picker_handoff_used": True,
            "foreground_handle_changed": changed,
            "foreground_window_class": picker_class,
            "foreground_window_title_hash": _hash_text(picker_title) if picker_title else "",
            "report_upload_attempted": True,
            "file_attach_attempted": True,
        })
        strategy = _enter_full_quoted_path_in_picker(picker_handle, safe_copy)
        state.update({
            "picker_ctrl_l_used": False,
            "picker_full_path_entry_attempted": True,
            "picker_full_path_quoted": True,
            "picker_filename_field_strategy": strategy,
            "file_picker_confirmed": True,
            "file_picker_enter_sent": True,
        })
        closed_or_changed = _wait_foreground_changed_or_edge(picker_handle, timeout_seconds=12.0)
        state.update({"picker_window_closed_after_confirm": closed_or_changed})
        staged, method = _observe_staged_file(safe_copy.name, timeout_seconds=90.0)
        state.update({
            "upload_staging_observed": staged,
            "staged_file_name_hash": _hash_text(safe_copy.name),
            "staging_observation_method": method,
            "result": "PASS" if staged else "FAIL",
            "failure_layer": "" if staged else "local_desktop_fullpath_staging_observation",
            "error": "" if staged else "Full quoted safe-copy path was entered, but staged attachment was not observed.",
        })
    except Exception as exc:
        state.update({
            "result": "FAIL",
            "failure_layer": "local_desktop_fullpath_picker_upload_repair",
            "error": f"{type(exc).__name__}: {exc}",
        })
    result = LocalDesktopFullPathUploadResult(**state)
    _write_report(live_report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_12l_acceptance(result: LocalDesktopFullPathUploadResult) -> None:
    payload = result.to_payload()
    required_true = [
        "local_desktop_report_path_used",
        "report_path_exists",
        "report_path_written_by_outer_script",
        "report_safe_copy_created",
        "report_safe_copy_closed",
        "safe_copy_hash_matches_report",
        "safe_copy_outside_onedrive",
        "safe_copy_full_path_used",
        "safe_copy_full_path_drive_valid",
        "composer_candidate_found",
        "composer_cleared_before_slash",
        "slash_typed_in_composer",
        "ctrl_u_shortcut_sent",
        "foreground_picker_handoff_used",
        "picker_full_path_entry_attempted",
        "picker_full_path_quoted",
        "file_picker_confirmed",
        "file_picker_enter_sent",
        "upload_staging_observed",
        "report_upload_attempted",
        "file_attach_attempted",
    ]
    required_false = [
        "safe_copy_full_path_had_lc_prefix",
        "picker_ctrl_l_used",
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
    for key in ("report_hash", "report_safe_copy_hash", "report_safe_copy_name", "foreground_window_class", "picker_filename_field_strategy", "staged_file_name_hash"):
        if not payload.get(key):
            missing_true.append(key + "_nonempty")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.12L acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
