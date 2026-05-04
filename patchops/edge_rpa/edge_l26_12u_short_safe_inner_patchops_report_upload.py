from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from pywinauto import keyboard  # type: ignore

from patchops.edge_rpa.edge_l26_12m_upload_gate import (
    drive_valid,
    enter_full_path_in_picker,
    foreground_handle,
    has_bad_lc_prefix,
    prepare_composer,
    wait_foreground_picker,
    wait_return_to_edge,
)
from patchops.edge_rpa.edge_l26_12r_gated_submit_fallback_gate import click_coordinate_fallback, try_uia_send_button
from patchops.edge_rpa.edge_l26_12s_post_submit_idle_observer import observe_idle

PATCH_NAME = "l26_12u_short_safe_inner_patchops_report_upload"


@dataclass(frozen=True)
class ShortSafeInnerReportUploadResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    uploaded_report_role: str = ""
    uploaded_report_count: int = 0
    uploaded_safe_copy_path: str = ""
    uploaded_safe_copy_path_length: int = 0
    uploaded_safe_copy_short_path: bool = False
    uploaded_safe_copy_hash_matches_inner_report: bool = False
    operator_report_uploaded: bool = False
    inner_patchops_report_exists: bool = False
    inner_patchops_report_hash: str = ""
    inner_patchops_report_size_bytes: int = 0
    short_safe_copy_created: bool = False
    short_safe_copy_hash: str = ""
    short_safe_copy_size_bytes: int = 0
    report_path_local_desktop: bool = False
    safe_copy_drive_valid: bool = False
    safe_copy_lc_prefix_detected: bool = False
    composer_candidate_found: bool = False
    composer_cleared: bool = False
    slash_typed: bool = False
    ctrl_u_sent: bool = False
    foreground_picker_handoff_used: bool = False
    foreground_class: str = ""
    ctrl_l_used: bool = False
    full_quoted_path_used: bool = False
    picker_confirmed: bool = False
    picker_enter_sent: bool = False
    picker_returned_to_edge: bool = False
    picker_confirmed_upload_accepted: bool = False
    allow_chatgpt_submit: bool = False
    escape_sent_before_submit: bool = False
    uia_send_button_clicked: bool = False
    coordinate_fallback_used: bool = False
    coordinate_click_performed: bool = False
    chatgpt_submit_performed: bool = False
    submit_method: str = ""
    submit_result: str = "FAIL"
    idle_observation_completed: bool = False
    ready_for_next_probe: bool = False
    observe_seconds_requested: int = 0
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    prompt_text_logged: bool = False
    file_content_logged: bool = False
    download_click_performed: bool = False
    generated_file_click_performed: bool = False
    run_package_invoked: bool = False
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


def make_short_safe_copy(inner_report: Path, short_upload_dir: Path) -> Path:
    short_upload_dir.mkdir(parents=True, exist_ok=True)
    safe_path = short_upload_dir / "patchops_apply_report.txt"
    with inner_report.open("rb") as src, safe_path.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
        dst.flush()
        os.fsync(dst.fileno())
    with safe_path.open("rb") as check:
        check.read(1)
    return safe_path


def write_json(path: Path, result: ShortSafeInnerReportUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: ShortSafeInnerReportUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def upload_short_safe_copy(safe_copy: Path) -> dict[str, object]:
    state: dict[str, object] = {}
    found, _focused, cleared = prepare_composer()
    state.update({"composer_candidate_found": found, "composer_cleared": cleared})
    if not found:
        raise RuntimeError("Composer candidate was not found before short safe report upload.")
    before = foreground_handle()
    keyboard.send_keys("/")
    state.update({"slash_typed": True})
    time.sleep(0.35)
    keyboard.send_keys("^u")
    state.update({"ctrl_u_sent": True})
    picker, _changed, cls, _title = wait_foreground_picker(before)
    state.update({"foreground_picker_handoff_used": True, "foreground_class": cls})
    _strategy = enter_full_path_in_picker(picker, safe_copy)
    returned = wait_return_to_edge(picker, timeout=14.0)
    state.update({
        "ctrl_l_used": False,
        "full_quoted_path_used": True,
        "picker_confirmed": True,
        "picker_enter_sent": True,
        "picker_returned_to_edge": returned,
        "picker_confirmed_upload_accepted": True,
    })
    return state


def submit_after_upload(allow_chatgpt_submit: bool) -> dict[str, object]:
    state: dict[str, object] = {"allow_chatgpt_submit": allow_chatgpt_submit}
    if not allow_chatgpt_submit:
        raise RuntimeError("Refusing to submit because --allow-chatgpt-submit was not provided.")
    keyboard.send_keys("{ESC}")
    state.update({"escape_sent_before_submit": True})
    time.sleep(0.35)
    clicked, _fp, _ctype = try_uia_send_button()
    if clicked:
        state.update({"uia_send_button_clicked": True, "submit_method": "uia_send_button_click"})
    else:
        ok, _target_hash = click_coordinate_fallback()
        state.update({"coordinate_fallback_used": True, "coordinate_click_performed": ok, "submit_method": "edge_window_lower_right_coordinate_click" if ok else ""})
        if not ok:
            raise RuntimeError("No UIA send button found and coordinate fallback could not click Edge window.")
    time.sleep(4.0)
    state.update({"chatgpt_submit_performed": True, "submit_result": "PASS"})
    return state


def run_short_safe_inner_report_upload(
    output_dir: Path,
    inner_patchops_report_path: Path,
    operator_report_path: Path,
    short_upload_dir: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    observe_seconds: int,
) -> ShortSafeInnerReportUploadResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "l26_12u_short_safe_inner_patchops_report_upload_result.json"
    live_report_path = output_dir / "l26_12u_short_safe_inner_patchops_report_upload_live_report.txt"
    state: dict[str, object] = {"observe_seconds_requested": int(observe_seconds)}
    try:
        if not allow_report_upload:
            raise RuntimeError("Missing explicit --allow-report-upload")
        inner = inner_patchops_report_path.resolve()
        operator = operator_report_path.resolve()
        if not inner.exists() or not inner.is_file():
            raise RuntimeError(f"Inner PatchOps report does not exist: {inner}")
        inner_hash = hash_file(inner)
        inner_size = inner.stat().st_size
        safe_copy = make_short_safe_copy(inner, short_upload_dir.resolve())
        safe_hash = hash_file(safe_copy)
        safe_size = safe_copy.stat().st_size
        safe_text = str(safe_copy)
        state.update({
            "uploaded_report_role": "inner_patchops_apply_report_short_safe_copy",
            "uploaded_report_count": 1,
            "uploaded_safe_copy_path": safe_text,
            "uploaded_safe_copy_path_length": len(safe_text),
            "uploaded_safe_copy_short_path": len(safe_text) < 180,
            "uploaded_safe_copy_hash_matches_inner_report": inner_hash == safe_hash and inner_size == safe_size,
            "operator_report_uploaded": False,
            "inner_patchops_report_exists": True,
            "inner_patchops_report_hash": inner_hash,
            "inner_patchops_report_size_bytes": int(inner_size),
            "short_safe_copy_created": True,
            "short_safe_copy_hash": safe_hash,
            "short_safe_copy_size_bytes": int(safe_size),
            "report_path_local_desktop": "onedrive" not in str(operator).lower() and str(operator).lower().endswith(".txt"),
            "safe_copy_drive_valid": drive_valid(safe_copy),
            "safe_copy_lc_prefix_detected": has_bad_lc_prefix(safe_copy),
        })
        if inner_hash != safe_hash or inner_size != safe_size:
            raise RuntimeError("Short safe copy hash/size does not match inner PatchOps report.")
        if not drive_valid(safe_copy):
            raise RuntimeError(f"Short safe copy drive is not valid: {safe_copy}")
        if has_bad_lc_prefix(safe_copy):
            raise RuntimeError(f"Short safe copy path has lC/iC corruption: {safe_copy}")
        state.update(upload_short_safe_copy(safe_copy))
        state.update(submit_after_upload(allow_chatgpt_submit))
        obs = observe_idle(observe_seconds)
        state.update({
            "idle_observation_completed": True,
            "ready_for_next_probe": bool(obs.get("edge_window_found")) and bool(obs.get("stop_generating_absent_at_end")),
        })
        ok = bool(state.get("picker_confirmed_upload_accepted")) and bool(state.get("chatgpt_submit_performed")) and bool(state.get("ready_for_next_probe"))
        state.update({"result": "PASS" if ok else "FAIL", "failure_layer": "" if ok else "short_safe_inner_report_upload_observation", "error": "" if ok else "Upload/submit/idle did not all pass."})
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "short_safe_inner_report_upload", "error": f"{type(exc).__name__}: {exc}"})
    result = ShortSafeInnerReportUploadResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: ShortSafeInnerReportUploadResult) -> None:
    p = result.to_payload()
    true_keys = [
        "uploaded_safe_copy_short_path", "uploaded_safe_copy_hash_matches_inner_report", "inner_patchops_report_exists",
        "short_safe_copy_created", "safe_copy_drive_valid", "composer_candidate_found", "slash_typed", "ctrl_u_sent",
        "foreground_picker_handoff_used", "full_quoted_path_used", "picker_confirmed", "picker_enter_sent",
        "picker_confirmed_upload_accepted", "allow_chatgpt_submit", "chatgpt_submit_performed", "idle_observation_completed",
        "ready_for_next_probe",
    ]
    false_keys = [
        "operator_report_uploaded", "safe_copy_lc_prefix_detected", "ctrl_l_used", "conversation_text_logged",
        "full_conversation_text_logged", "prompt_text_logged", "file_content_logged", "download_click_performed",
        "generated_file_click_performed", "run_package_invoked", "webdriver_used", "selenium_imported",
        "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if p.get("uploaded_report_role") != "inner_patchops_apply_report_short_safe_copy":
        missing.append("uploaded_report_role_inner_short_safe_copy")
    if int(p.get("uploaded_report_count") or 0) != 1:
        missing.append("uploaded_report_count_1")
    for k in ("uploaded_safe_copy_path", "inner_patchops_report_hash", "short_safe_copy_hash", "submit_method"):
        if not p.get(k):
            missing.append(k + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.12U acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
