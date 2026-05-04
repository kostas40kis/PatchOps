from __future__ import annotations

import ctypes
import hashlib
import json
import os
import shutil
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from pywinauto import keyboard  # type: ignore

from patchops.edge_rpa.edge_upload_safe_report_copy_gate import _hash_text, _is_onedrive_path, _observe_staged_file, _set_clipboard_text, _verify_direct_composer_focus

PATCH_NAME = "l26_12m_crash_safe_local_desktop_fullpath_upload_repair"
EDGE_CLASSES = {"Chrome_WidgetWin_0", "Chrome_WidgetWin_1"}
USER32 = ctypes.windll.user32


@dataclass(frozen=True)
class UploadResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    report_path_exists: bool = False
    report_path_local_desktop: bool = False
    report_hash: str = ""
    report_size_bytes: int = 0
    safe_copy_created: bool = False
    safe_copy_name: str = ""
    safe_copy_hash: str = ""
    safe_copy_size_bytes: int = 0
    safe_copy_closed: bool = False
    safe_copy_hash_matches_report: bool = False
    safe_copy_drive_valid: bool = False
    safe_copy_lc_prefix_detected: bool = False
    composer_candidate_found: bool = False
    composer_focus_verified: bool = False
    composer_cleared: bool = False
    slash_typed: bool = False
    plus_clicked_after_slash: bool = False
    ctrl_u_sent: bool = False
    foreground_picker_handoff_used: bool = False
    foreground_handle_changed: bool = False
    foreground_class: str = ""
    foreground_title_hash: str = ""
    ctrl_l_used: bool = False
    full_quoted_path_used: bool = False
    filename_field_strategy: str = ""
    picker_confirmed: bool = False
    picker_enter_sent: bool = False
    picker_returned_to_edge: bool = False
    upload_staging_observed: bool = False
    staged_file_name_hash: str = ""
    staging_observation_method: str = ""
    report_upload_attempted: bool = False
    file_attach_attempted: bool = False
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


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def split_drive(path: Path) -> str:
    return os.path.splitdrive(str(path))[0]


def drive_valid(path: Path) -> bool:
    drive = split_drive(path)
    if not drive or len(drive) != 2 or drive[1] != ":":
        return False
    return Path(drive + "\\").exists()


def has_bad_lc_prefix(path: Path) -> bool:
    text = str(path).lower().replace("/", "\\")
    return text.startswith("lc:") or text.startswith("ic:")


def foreground_handle() -> int:
    try:
        return int(USER32.GetForegroundWindow() or 0)
    except Exception:
        return 0


def window_class(hwnd: int) -> str:
    if not hwnd:
        return ""
    buf = ctypes.create_unicode_buffer(512)
    try:
        USER32.GetClassNameW(hwnd, buf, 512)
        return str(buf.value or "")
    except Exception:
        return ""


def window_title(hwnd: int) -> str:
    if not hwnd:
        return ""
    buf = ctypes.create_unicode_buffer(512)
    try:
        USER32.GetWindowTextW(hwnd, buf, 512)
        return str(buf.value or "")
    except Exception:
        return ""


def set_foreground(hwnd: int) -> None:
    if hwnd:
        try:
            USER32.SetForegroundWindow(hwnd)
        except Exception:
            pass


def wait_foreground_picker(before: int, timeout: float = 14.0) -> tuple[int, bool, str, str]:
    deadline = time.time() + timeout
    last = 0
    while time.time() < deadline:
        hwnd = foreground_handle()
        if hwnd:
            last = hwnd
            cls = window_class(hwnd)
            title = window_title(hwnd)
            if hwnd != before and cls not in EDGE_CLASSES:
                return hwnd, True, cls, title
            if cls in {"#32770", "CabinetWClass", "ExploreWClass"}:
                return hwnd, hwnd != before, cls, title
        time.sleep(0.2)
    hwnd = last or foreground_handle()
    cls = window_class(hwnd)
    title = window_title(hwnd)
    if hwnd and cls not in EDGE_CLASSES:
        return hwnd, hwnd != before, cls, title
    raise RuntimeError(f"No foreground OS picker handoff after Ctrl+U; foreground_class={cls!r}")


def wait_return_to_edge(original_picker: int, timeout: float = 14.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        hwnd = foreground_handle()
        cls = window_class(hwnd)
        if hwnd and hwnd != original_picker:
            return True
        if cls in EDGE_CLASSES:
            return True
        time.sleep(0.25)
    return False


def copy_report(report: Path, output_dir: Path) -> Path:
    safe_dir = output_dir / "upload_safe_report_copy"
    safe_dir.mkdir(parents=True, exist_ok=True)
    safe_path = safe_dir / ("upload_copy_of_" + report.name)
    with report.open("rb") as src, safe_path.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
        dst.flush()
        os.fsync(dst.fileno())
    with safe_path.open("rb") as check:
        check.read(1)
    return safe_path


def prepare_composer() -> tuple[bool, bool, bool]:
    found, focused = _verify_direct_composer_focus()
    cleared = False
    if found:
        try:
            keyboard.send_keys("^a")
            time.sleep(0.1)
            keyboard.send_keys("{BACKSPACE}")
            cleared = True
        except Exception:
            cleared = False
    return found, focused, cleared


def enter_full_path_in_picker(hwnd: int, file_path: Path) -> str:
    quoted = '"' + str(file_path) + '"'
    set_foreground(hwnd)
    time.sleep(0.25)
    # Do not use Ctrl+L. The real machine produced lC:\\ path corruption from that step.
    try:
        keyboard.send_keys("%n")
        time.sleep(0.25)
        _set_clipboard_text(quoted)
        keyboard.send_keys("^v")
        time.sleep(0.25)
        keyboard.send_keys("{ENTER}")
        return "alt_n_full_quoted_path_enter"
    except Exception:
        _set_clipboard_text(quoted)
        keyboard.send_keys("^v")
        time.sleep(0.25)
        keyboard.send_keys("{ENTER}")
        return "focused_full_quoted_path_enter"


def write_json(path: Path, result: UploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: UploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for key, value in result.to_payload().items():
        if key in {"patch_name", "result", "failure_layer", "error"} or isinstance(value, (bool, int, str)):
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_upload(output_dir: Path, report_path: Path, allow_report_upload: bool) -> UploadResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "l26_12m_upload_result.json"
    live_report_path = output_dir / "l26_12m_upload_live_report.txt"
    state: dict[str, object] = {}
    try:
        if not allow_report_upload:
            raise RuntimeError("Missing explicit --allow-report-upload")
        if not report_path.exists() or not report_path.is_file():
            raise RuntimeError(f"Report path does not exist: {report_path}")
        report_hash = hash_file(report_path)
        report_size = report_path.stat().st_size
        safe_copy = copy_report(report_path, output_dir)
        safe_hash = hash_file(safe_copy)
        safe_size = safe_copy.stat().st_size
        state.update({
            "report_path_exists": True,
            "report_path_local_desktop": "onedrive" not in str(report_path).lower() and str(report_path).lower().endswith(".txt"),
            "report_hash": report_hash,
            "report_size_bytes": int(report_size),
            "safe_copy_created": True,
            "safe_copy_name": safe_copy.name,
            "safe_copy_hash": safe_hash,
            "safe_copy_size_bytes": int(safe_size),
            "safe_copy_closed": True,
            "safe_copy_hash_matches_report": report_hash == safe_hash and report_size == safe_size,
            "safe_copy_drive_valid": drive_valid(safe_copy),
            "safe_copy_lc_prefix_detected": has_bad_lc_prefix(safe_copy),
        })
        if report_hash != safe_hash or report_size != safe_size:
            raise RuntimeError("Safe copy hash or size does not match report")
        if not drive_valid(safe_copy):
            raise RuntimeError(f"Safe copy drive is not valid: {safe_copy}")
        if has_bad_lc_prefix(safe_copy):
            raise RuntimeError(f"Safe copy path has bad lC/iC prefix: {safe_copy}")

        found, focused, cleared = prepare_composer()
        state.update({"composer_candidate_found": found, "composer_focus_verified": focused, "composer_cleared": cleared})
        if not found:
            raise RuntimeError("Composer candidate was not found")

        before = foreground_handle()
        keyboard.send_keys("/")
        state.update({"slash_typed": True, "plus_clicked_after_slash": False})
        time.sleep(0.35)
        keyboard.send_keys("^u")
        state.update({"ctrl_u_sent": True})
        picker, changed, cls, title = wait_foreground_picker(before)
        state.update({
            "foreground_picker_handoff_used": True,
            "foreground_handle_changed": changed,
            "foreground_class": cls,
            "foreground_title_hash": _hash_text(title) if title else "",
            "report_upload_attempted": True,
            "file_attach_attempted": True,
        })
        strategy = enter_full_path_in_picker(picker, safe_copy)
        state.update({
            "ctrl_l_used": False,
            "full_quoted_path_used": True,
            "filename_field_strategy": strategy,
            "picker_confirmed": True,
            "picker_enter_sent": True,
        })
        returned = wait_return_to_edge(picker)
        state.update({"picker_returned_to_edge": returned})
        staged, method = _observe_staged_file(safe_copy.name, timeout_seconds=90.0)
        state.update({
            "upload_staging_observed": staged,
            "staged_file_name_hash": _hash_text(safe_copy.name),
            "staging_observation_method": method,
            "result": "PASS" if staged else "FAIL",
            "failure_layer": "" if staged else "staging_observation",
            "error": "" if staged else "Full quoted path was entered, but staged attachment was not observed",
        })
    except Exception as exc:
        state.update({
            "result": "FAIL",
            "failure_layer": "l26_12m_upload",
            "error": f"{type(exc).__name__}: {exc}",
        })
    result = UploadResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: UploadResult) -> None:
    p = result.to_payload()
    true_keys = [
        "report_path_exists", "report_path_local_desktop", "safe_copy_created", "safe_copy_closed",
        "safe_copy_hash_matches_report", "safe_copy_drive_valid", "composer_candidate_found",
        "composer_cleared", "slash_typed", "ctrl_u_sent", "foreground_picker_handoff_used",
        "full_quoted_path_used", "picker_confirmed", "picker_enter_sent", "upload_staging_observed",
        "report_upload_attempted", "file_attach_attempted",
    ]
    false_keys = [
        "safe_copy_lc_prefix_detected", "ctrl_l_used", "plus_clicked_after_slash", "chatgpt_submit_enter_sent",
        "send_submit_performed", "chatgpt_prompt_submitted", "download_click_performed", "run_package_invoked",
        "conversation_text_logged", "prompt_text_logged", "file_content_logged", "webdriver_used", "selenium_imported",
        "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    for k in ("report_hash", "safe_copy_hash", "safe_copy_name", "foreground_class", "filename_field_strategy", "staged_file_name_hash"):
        if not p.get(k):
            missing.append(k + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.12M acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
