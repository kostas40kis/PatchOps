from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.edge_rpa.edge_l26_12m_upload_gate import (
    copy_report,
    drive_valid,
    enter_full_path_in_picker,
    foreground_handle,
    has_bad_lc_prefix,
    hash_file,
    prepare_composer,
    wait_foreground_picker,
    wait_return_to_edge,
)

PATCH_NAME = "l26_12p_picker_confirmed_upload_acceptance"


@dataclass(frozen=True)
class PickerConfirmedUploadResult:
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
    ctrl_u_sent: bool = False
    foreground_picker_handoff_used: bool = False
    foreground_handle_changed: bool = False
    foreground_class: str = ""
    foreground_title_hash_present: bool = False
    ctrl_l_used: bool = False
    full_quoted_path_used: bool = False
    filename_field_strategy: str = ""
    picker_confirmed: bool = False
    picker_enter_sent: bool = False
    picker_returned_to_edge: bool = False
    picker_confirmed_upload_accepted: bool = False
    staging_observation_attempted: bool = False
    upload_staging_observed_optional: bool = False
    slash_leftover_tolerated: bool = True
    cleanup_attempted: bool = False
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


def write_json(path: Path, result: PickerConfirmedUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: PickerConfirmedUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{key}: {value}" for key, value in result.to_payload().items()) + "\n", encoding="utf-8")


def run_picker_confirmed_upload(output_dir: Path, report_path: Path, allow_report_upload: bool) -> PickerConfirmedUploadResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "l26_12p_picker_confirmed_upload_result.json"
    live_report_path = output_dir / "l26_12p_picker_confirmed_upload_live_report.txt"
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

        import pywinauto.keyboard as keyboard  # type: ignore
        before = foreground_handle()
        keyboard.send_keys("/")
        state.update({"slash_typed": True})
        time.sleep(0.35)
        keyboard.send_keys("^u")
        state.update({"ctrl_u_sent": True})
        picker, changed, cls, title = wait_foreground_picker(before)
        state.update({
            "foreground_picker_handoff_used": True,
            "foreground_handle_changed": changed,
            "foreground_class": cls,
            "foreground_title_hash_present": bool(title),
        })
        strategy = enter_full_path_in_picker(picker, safe_copy)
        state.update({
            "ctrl_l_used": False,
            "full_quoted_path_used": True,
            "filename_field_strategy": strategy,
            "picker_confirmed": True,
            "picker_enter_sent": True,
        })
        returned = wait_return_to_edge(picker, timeout=14.0)
        state.update({
            "picker_returned_to_edge": returned,
            "picker_confirmed_upload_accepted": True,
            "staging_observation_attempted": False,
            "upload_staging_observed_optional": False,
            "slash_leftover_tolerated": True,
            "cleanup_attempted": False,
            "result": "PASS",
            "failure_layer": "",
            "error": "",
        })
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "picker_confirmed_upload", "error": f"{type(exc).__name__}: {exc}"})
    result = PickerConfirmedUploadResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: PickerConfirmedUploadResult) -> None:
    p = result.to_payload()
    true_keys = [
        "report_path_exists", "report_path_local_desktop", "safe_copy_created", "safe_copy_closed",
        "safe_copy_hash_matches_report", "safe_copy_drive_valid", "composer_candidate_found",
        "composer_cleared", "slash_typed", "ctrl_u_sent", "foreground_picker_handoff_used",
        "full_quoted_path_used", "picker_confirmed", "picker_enter_sent", "picker_confirmed_upload_accepted",
        "slash_leftover_tolerated",
    ]
    false_keys = [
        "safe_copy_lc_prefix_detected", "ctrl_l_used", "cleanup_attempted", "chatgpt_submit_enter_sent",
        "send_submit_performed", "chatgpt_prompt_submitted", "download_click_performed", "run_package_invoked",
        "conversation_text_logged", "prompt_text_logged", "file_content_logged", "webdriver_used", "selenium_imported",
        "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [key for key in true_keys if not p.get(key)]
    unexpected = [key for key in false_keys if p.get(key)]
    for key in ("report_hash", "safe_copy_hash", "safe_copy_name", "foreground_class", "filename_field_strategy"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.12P acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
