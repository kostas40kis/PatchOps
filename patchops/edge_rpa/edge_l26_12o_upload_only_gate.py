from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.edge_rpa.edge_l26_12m_upload_gate import UploadResult, run_upload
from patchops.edge_rpa.edge_upload_safe_report_copy_gate import _hash_text

PATCH_NAME = "l26_12o_upload_only_slash_tolerant_acceptance"


@dataclass(frozen=True)
class UploadOnlyResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    upload_result: str = "FAIL"
    upload_staging_observed: bool = False
    staged_file_name_hash: str = ""
    staging_observation_method: str = ""
    slash_leftover_tolerated: bool = True
    cleanup_attempted: bool = False
    report_path_local_desktop: bool = False
    safe_copy_created: bool = False
    safe_copy_closed: bool = False
    safe_copy_hash_matches_report: bool = False
    safe_copy_drive_valid: bool = False
    safe_copy_lc_prefix_detected: bool = False
    plus_clicked_after_slash: bool = False
    ctrl_l_used: bool = False
    full_quoted_path_used: bool = False
    picker_confirmed: bool = False
    picker_enter_sent: bool = False
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


def write_json(path: Path, result: UploadOnlyResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: UploadOnlyResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{key}: {value}" for key, value in result.to_payload().items()) + "\n", encoding="utf-8")


def run_upload_only(output_dir: Path, report_path: Path, allow_report_upload: bool) -> UploadOnlyResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "l26_12o_upload_only_result.json"
    live_report_path = output_dir / "l26_12o_upload_only_live_report.txt"
    state: dict[str, object] = {}
    try:
        upload: UploadResult = run_upload(output_dir / "upload_proof", report_path, allow_report_upload)
        p = upload.to_payload()
        safe_name = str(p.get("safe_copy_name") or "")
        staged = bool(p.get("upload_staging_observed"))
        state.update({
            "upload_result": str(p.get("result") or "FAIL"),
            "upload_staging_observed": staged,
            "staged_file_name_hash": _hash_text(safe_name) if safe_name else "",
            "staging_observation_method": str(p.get("staging_observation_method") or ""),
            "slash_leftover_tolerated": True,
            "cleanup_attempted": False,
            "report_path_local_desktop": bool(p.get("report_path_local_desktop")),
            "safe_copy_created": bool(p.get("safe_copy_created")),
            "safe_copy_closed": bool(p.get("safe_copy_closed")),
            "safe_copy_hash_matches_report": bool(p.get("safe_copy_hash_matches_report")),
            "safe_copy_drive_valid": bool(p.get("safe_copy_drive_valid")),
            "safe_copy_lc_prefix_detected": bool(p.get("safe_copy_lc_prefix_detected")),
            "plus_clicked_after_slash": bool(p.get("plus_clicked_after_slash")),
            "ctrl_l_used": bool(p.get("ctrl_l_used")),
            "full_quoted_path_used": bool(p.get("full_quoted_path_used")),
            "picker_confirmed": bool(p.get("picker_confirmed")),
            "picker_enter_sent": bool(p.get("picker_enter_sent")),
            "chatgpt_submit_enter_sent": bool(p.get("chatgpt_submit_enter_sent")),
            "send_submit_performed": bool(p.get("send_submit_performed")),
            "chatgpt_prompt_submitted": bool(p.get("chatgpt_prompt_submitted")),
            "download_click_performed": bool(p.get("download_click_performed")),
            "run_package_invoked": bool(p.get("run_package_invoked")),
            "conversation_text_logged": bool(p.get("conversation_text_logged")),
            "full_conversation_text_logged": bool(p.get("full_conversation_text_logged")),
            "prompt_text_logged": bool(p.get("prompt_text_logged")),
            "file_content_logged": bool(p.get("file_content_logged")),
            "webdriver_used": bool(p.get("webdriver_used")),
            "selenium_imported": bool(p.get("selenium_imported")),
            "cloudflare_bypass_attempted": bool(p.get("cloudflare_bypass_attempted")),
            "browser_dom_automation_used": bool(p.get("browser_dom_automation_used")),
            "result": "PASS" if staged else "FAIL",
            "failure_layer": "" if staged else "upload_only_staging",
            "error": "" if staged else f"Upload-only proof did not observe staging; upload_error={p.get('error')}",
        })
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "upload_only", "error": f"{type(exc).__name__}: {exc}"})
    result = UploadOnlyResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: UploadOnlyResult) -> None:
    p = result.to_payload()
    true_keys = [
        "upload_staging_observed", "slash_leftover_tolerated", "report_path_local_desktop",
        "safe_copy_created", "safe_copy_closed", "safe_copy_hash_matches_report", "safe_copy_drive_valid",
        "full_quoted_path_used", "picker_confirmed", "picker_enter_sent",
    ]
    false_keys = [
        "cleanup_attempted", "safe_copy_lc_prefix_detected", "plus_clicked_after_slash", "ctrl_l_used",
        "chatgpt_submit_enter_sent", "send_submit_performed", "chatgpt_prompt_submitted", "download_click_performed",
        "run_package_invoked", "conversation_text_logged", "prompt_text_logged", "file_content_logged", "webdriver_used",
        "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [key for key in true_keys if not p.get(key)]
    unexpected = [key for key in false_keys if p.get(key)]
    if not p.get("staged_file_name_hash"):
        missing.append("staged_file_name_hash_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.12O acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
