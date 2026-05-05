from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import pywinauto  # type: ignore

from patchops.edge_rpa.edge_l26_12u_short_safe_inner_patchops_report_upload import upload_short_safe_copy
from patchops.edge_rpa.edge_l26_14d_visible_attachment_upload_gate_repair import _attachment_signals
from patchops.edge_rpa.edge_l26_14i_restore_good_canonical_and_strict_upload_gate import canonical_is_good, find_last_good_canonical, hash_file
from patchops.edge_rpa.edge_upload_safe_report_copy_gate import _hash_text
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_14j_upload_primitive_diagnostic_freeze"


@dataclass(frozen=True)
class UploadPrimitiveDiagnosticFreezeResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    latest_restored_or_already_good: bool = False
    restored_source_path: str = ""
    probe_file_created: bool = False
    probe_file_path: str = ""
    probe_file_hash: str = ""
    picker_confirmed_upload_accepted: bool = False
    file_dialog_seen_before_confirm: bool = False
    file_dialog_seen_after_confirm: bool = False
    edge_window_found_after_picker: bool = False
    attachment_visible_after_picker: bool = False
    attachment_signal_count_after_picker: int = 0
    attachment_detector_method: str = "uia_filename_or_attachment_signal"
    upload_primitive_reliable: bool = False
    chatgpt_submit_performed: bool = False
    send_or_enter_performed: bool = False
    canonical_publish_performed: bool = False
    candidate_click_performed: bool = False
    download_click_performed: bool = False
    generated_file_click_performed: bool = False
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    prompt_text_logged: bool = False
    file_content_logged: bool = False
    run_package_invoked: bool = False
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_dom_automation_used: bool = False
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""
    recommended_next_patch: str = ""

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


def write_json(path: Path, result: UploadPrimitiveDiagnosticFreezeResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: UploadPrimitiveDiagnosticFreezeResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def restore_latest_to_good(latest_path: Path, desktop_path: Path) -> tuple[bool, str]:
    if canonical_is_good(latest_path):
        return True, str(latest_path)
    good = find_last_good_canonical(desktop_path)
    if good is None:
        raise RuntimeError("No known-good canonical report is available for pointer restore.")
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(good, latest_path)
    if not canonical_is_good(latest_path):
        raise RuntimeError("Latest canonical restore did not produce a good canonical pointer.")
    return True, str(good)


def create_probe_file(upload_bridge_dir: Path) -> Path:
    upload_bridge_dir.mkdir(parents=True, exist_ok=True)
    path = upload_bridge_dir / f"patchops_upload_probe_{int(time.time())}.txt"
    path.write_text(
        "PATCHOPS UPLOAD PRIMITIVE DIAGNOSTIC PROBE\n"
        f"patch_name: {PATCH_NAME}\n"
        "purpose: verify ChatGPT attachment staging only; do not submit\n",
        encoding="utf-8",
    )
    return path


def file_dialog_seen() -> bool:
    try:
        desktop = pywinauto.Desktop(backend="uia")
        for w in desktop.windows():
            try:
                info = w.element_info
                name = (getattr(info, "name", "") or "").lower()
                control_type = getattr(info, "control_type", "") or ""
                if control_type == "Window" and ("open" in name or "upload" in name or "choose" in name or "file" in name):
                    return True
            except Exception:
                pass
    except Exception:
        return False
    return False


def edge_window_seen() -> bool:
    try:
        desktop = pywinauto.Desktop(backend="uia")
        _windows, wrappers = discover_edge_windows(desktop, edge_process_ids())
        return bool(list(wrappers or []))
    except Exception:
        return False


def run_upload_primitive_diagnostic_freeze(
    short_live_root: Path,
    latest_canonical_path: Path,
    desktop_path: Path,
    upload_bridge_dir: Path,
    upload_probe_seconds: int,
    picker_wait_seconds: int,
) -> UploadPrimitiveDiagnosticFreezeResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14j_upload_primitive_diagnostic_freeze_result.json"
    live_report_path = short_live_root / "l26_14j_upload_primitive_diagnostic_freeze_live_report.txt"
    state: dict[str, object] = {}
    try:
        restored, restored_source = restore_latest_to_good(latest_canonical_path, desktop_path)
        probe = create_probe_file(upload_bridge_dir)
        state.update({
            "latest_restored_or_already_good": restored,
            "restored_source_path": restored_source,
            "probe_file_created": probe.exists(),
            "probe_file_path": str(probe),
            "probe_file_hash": hash_file(probe),
        })
        before_dialog = file_dialog_seen()
        upload_state = upload_short_safe_copy(probe)
        time.sleep(max(1, min(int(picker_wait_seconds), 20)))
        after_dialog = file_dialog_seen()
        attach = _attachment_signals(probe.name, upload_probe_seconds)
        edge_seen = edge_window_seen()
        picker_ok = bool(upload_state.get("picker_confirmed_upload_accepted"))
        attachment_ok = bool(attach.get("found"))
        reliable = picker_ok and attachment_ok and edge_seen and not after_dialog
        state.update({
            "picker_confirmed_upload_accepted": picker_ok,
            "file_dialog_seen_before_confirm": before_dialog,
            "file_dialog_seen_after_confirm": after_dialog,
            "edge_window_found_after_picker": edge_seen,
            "attachment_visible_after_picker": attachment_ok,
            "attachment_signal_count_after_picker": int(attach.get("signals") or 0),
            "upload_primitive_reliable": reliable,
            "recommended_next_patch": "L26.14K direct file-dialog path entry repair" if not reliable else "L26.14K strict upload-submit rerun from reliable primitive",
            "result": "PASS" if reliable else "FAIL",
            "failure_layer": "" if reliable else "upload_primitive_diagnostic_freeze",
            "error": "" if reliable else "Upload primitive is not reliable: picker accepted but attachment was not visible/staged. Do not submit or advance to candidate clicking.",
        })
    except Exception as exc:
        state.update({
            "result": "FAIL",
            "failure_layer": "upload_primitive_diagnostic_freeze",
            "error": f"{type(exc).__name__}: {exc}",
            "recommended_next_patch": "L26.14K direct file-dialog path entry repair",
        })
    result = UploadPrimitiveDiagnosticFreezeResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: UploadPrimitiveDiagnosticFreezeResult) -> None:
    p = result.to_payload()
    true_keys = [
        "latest_restored_or_already_good",
        "probe_file_created",
        "picker_confirmed_upload_accepted",
        "edge_window_found_after_picker",
        "attachment_visible_after_picker",
        "upload_primitive_reliable",
    ]
    false_keys = [
        "chatgpt_submit_performed",
        "send_or_enter_performed",
        "canonical_publish_performed",
        "candidate_click_performed",
        "download_click_performed",
        "generated_file_click_performed",
        "conversation_text_logged",
        "full_conversation_text_logged",
        "prompt_text_logged",
        "file_content_logged",
        "run_package_invoked",
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if int(p.get("attachment_signal_count_after_picker") or 0) <= 0:
        missing.append("attachment_signal_count_after_picker_positive")
    for key in ("restored_source_path", "probe_file_path", "probe_file_hash", "recommended_next_patch"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14J acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
