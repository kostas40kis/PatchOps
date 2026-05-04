from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from pywinauto import keyboard  # type: ignore

from patchops.edge_rpa.edge_l26_12m_upload_gate import UploadResult, run_upload
from patchops.edge_rpa.edge_upload_safe_report_copy_gate import _hash_text, _observe_staged_file, _verify_direct_composer_focus

PATCH_NAME = "l26_12n_post_upload_slash_cleanup_repair"


@dataclass(frozen=True)
class CleanupResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    upload_result: str = "FAIL"
    upload_staging_observed_before_cleanup: bool = False
    staged_file_name_hash: str = ""
    composer_refocused_for_cleanup: bool = False
    cleanup_ctrl_a_backspace_sent: bool = False
    cleanup_attempted: bool = False
    cleanup_preserved_staged_attachment: bool = False
    staging_observation_after_cleanup: str = ""
    chatgpt_submit_enter_sent: bool = False
    send_submit_performed: bool = False
    chatgpt_prompt_submitted: bool = False
    plus_clicked_after_slash: bool = False
    ctrl_l_used: bool = False
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


def write_json(path: Path, result: CleanupResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: CleanupResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {value}" for key, value in result.to_payload().items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cleanup_leftover_composer_text() -> tuple[bool, bool]:
    found, focused = _verify_direct_composer_focus()
    if not found:
        return False, False
    # Safe cleanup: the helper focuses the editable composer candidate first.
    # No Enter is sent here; this is only text cleanup for the leftover slash.
    keyboard.send_keys("^a")
    time.sleep(0.12)
    keyboard.send_keys("{BACKSPACE}")
    time.sleep(0.25)
    return True, True


def run_upload_then_cleanup(output_dir: Path, report_path: Path, allow_report_upload: bool) -> CleanupResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "l26_12n_cleanup_result.json"
    live_report_path = output_dir / "l26_12n_cleanup_live_report.txt"
    state: dict[str, object] = {}
    try:
        upload: UploadResult = run_upload(output_dir / "upload_proof", report_path, allow_report_upload)
        upload_payload = upload.to_payload()
        safe_name = str(upload_payload.get("safe_copy_name") or "")
        before_staged = bool(upload_payload.get("upload_staging_observed"))
        state.update({
            "upload_result": str(upload_payload.get("result") or "FAIL"),
            "upload_staging_observed_before_cleanup": before_staged,
            "staged_file_name_hash": _hash_text(safe_name) if safe_name else "",
            "plus_clicked_after_slash": bool(upload_payload.get("plus_clicked_after_slash")),
            "ctrl_l_used": bool(upload_payload.get("ctrl_l_used")),
        })
        if not before_staged or not safe_name:
            raise RuntimeError(f"Upload did not stage before cleanup; upload_result={upload_payload.get('result')}; error={upload_payload.get('error')}")
        refocused, cleaned = cleanup_leftover_composer_text()
        state.update({
            "composer_refocused_for_cleanup": refocused,
            "cleanup_ctrl_a_backspace_sent": cleaned,
            "cleanup_attempted": cleaned,
        })
        if not cleaned:
            raise RuntimeError("Composer cleanup could not focus the editable composer candidate")
        still_staged, method = _observe_staged_file(safe_name, timeout_seconds=30.0)
        state.update({
            "cleanup_preserved_staged_attachment": still_staged,
            "staging_observation_after_cleanup": method,
            "result": "PASS" if still_staged else "FAIL",
            "failure_layer": "" if still_staged else "cleanup_attachment_preservation",
            "error": "" if still_staged else "Attachment was staged before cleanup, but not observed after cleanup",
        })
    except Exception as exc:
        state.update({
            "result": "FAIL",
            "failure_layer": "post_upload_slash_cleanup",
            "error": f"{type(exc).__name__}: {exc}",
        })
    result = CleanupResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: CleanupResult) -> None:
    p = result.to_payload()
    true_keys = [
        "upload_staging_observed_before_cleanup",
        "composer_refocused_for_cleanup",
        "cleanup_ctrl_a_backspace_sent",
        "cleanup_attempted",
        "cleanup_preserved_staged_attachment",
    ]
    false_keys = [
        "chatgpt_submit_enter_sent",
        "send_submit_performed",
        "chatgpt_prompt_submitted",
        "plus_clicked_after_slash",
        "ctrl_l_used",
        "download_click_performed",
        "run_package_invoked",
        "conversation_text_logged",
        "prompt_text_logged",
        "file_content_logged",
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if not p.get("staged_file_name_hash"):
        missing.append("staged_file_name_hash_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.12N acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
