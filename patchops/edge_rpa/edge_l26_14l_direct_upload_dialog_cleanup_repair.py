from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from pywinauto.keyboard import send_keys  # type: ignore

from patchops.edge_rpa.edge_l26_14d_visible_attachment_upload_gate_repair import _attachment_signals
from patchops.edge_rpa.edge_l26_14i_restore_good_canonical_and_strict_upload_gate import canonical_is_good
from patchops.edge_rpa.edge_l26_14k_direct_file_dialog_path_entry_repair import (
    create_probe_file,
    edge_windows,
    enter_full_path_and_open,
    find_file_dialog,
    focus_edge,
    hash_file,
    open_upload_dialog_from_chat,
    wait_file_dialog,
)

PATCH_NAME = "l26_14l_direct_upload_dialog_cleanup_repair"


@dataclass(frozen=True)
class DirectUploadDialogCleanupRepairResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    latest_pointer_good_before_probe: bool = False
    probe_file_created: bool = False
    probe_file_path: str = ""
    probe_file_hash: str = ""
    edge_window_found_before_open: bool = False
    upload_trigger_attempted: bool = False
    file_dialog_found: bool = False
    file_dialog_path_entered: bool = False
    file_dialog_open_invoked: bool = False
    attachment_visible_after_direct_open: bool = False
    attachment_signal_count_after_direct_open: int = 0
    file_dialog_seen_after_open: bool = False
    dialog_cleanup_attempted: bool = False
    dialog_cleanup_method: str = ""
    file_dialog_seen_after_cleanup: bool = False
    edge_window_found_after_cleanup: bool = False
    attachment_visible_after_cleanup: bool = False
    attachment_signal_count_after_cleanup: int = 0
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


def write_json(path: Path, result: DirectUploadDialogCleanupRepairResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: DirectUploadDialogCleanupRepairResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def wait_until_no_file_dialog(timeout_seconds: int) -> bool:
    deadline = time.time() + max(2, min(int(timeout_seconds), 40))
    while time.time() < deadline:
        if find_file_dialog() is None:
            return True
        time.sleep(0.5)
    return find_file_dialog() is None


def cleanup_stale_dialog_or_menu(timeout_seconds: int) -> tuple[bool, str, bool]:
    attempted = False
    methods: list[str] = []
    # If an actual file dialog remains, do not leave it blocking future runs. Use Esc first, then Alt+F4.
    for method, keys in [("esc", "{ESC}"), ("alt_f4", "%{F4}"), ("esc_again", "{ESC}")]:
        dlg = find_file_dialog()
        if dlg is None:
            break
        attempted = True
        methods.append(method)
        try:
            dlg.set_focus()
        except Exception:
            pass
        try:
            send_keys(keys)
        except Exception:
            pass
        time.sleep(1.0)
        if wait_until_no_file_dialog(max(2, min(timeout_seconds, 8))):
            break
    # Also close leftover slash/menu UI in Edge without sending a message.
    try:
        focus_edge()
        send_keys("{ESC}")
        time.sleep(0.5)
        methods.append("edge_escape")
        attempted = True
    except Exception:
        pass
    remaining = find_file_dialog() is not None
    return attempted, "+".join(methods), remaining


def run_direct_upload_dialog_cleanup_repair(
    short_live_root: Path,
    latest_canonical_path: Path,
    upload_bridge_dir: Path,
    dialog_open_seconds: int,
    attachment_probe_seconds: int,
    dialog_cleanup_seconds: int,
) -> DirectUploadDialogCleanupRepairResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14l_direct_upload_dialog_cleanup_repair_result.json"
    live_report_path = short_live_root / "l26_14l_direct_upload_dialog_cleanup_repair_live_report.txt"
    state: dict[str, object] = {}
    try:
        latest_good = canonical_is_good(latest_canonical_path)
        probe = create_probe_file(upload_bridge_dir)
        before_edge = focus_edge()
        state.update({
            "latest_pointer_good_before_probe": latest_good,
            "probe_file_created": probe.exists(),
            "probe_file_path": str(probe),
            "probe_file_hash": hash_file(probe),
            "edge_window_found_before_open": before_edge,
        })
        trigger_ok = open_upload_dialog_from_chat()
        dialog = wait_file_dialog(dialog_open_seconds)
        found_dialog = dialog is not None
        entered = opened = False
        if found_dialog:
            entered, opened = enter_full_path_and_open(dialog, probe)
        # First observe whether attachment staged; L26.14K already proved this can happen even when stale dialog detection remains true.
        attach1 = _attachment_signals(probe.name, attachment_probe_seconds)
        visible1 = bool(attach1.get("found"))
        dialog_after_open = find_file_dialog() is not None
        cleanup_attempted, cleanup_method, dialog_after_cleanup = cleanup_stale_dialog_or_menu(dialog_cleanup_seconds)
        edge_after_cleanup = bool(edge_windows())
        attach2 = _attachment_signals(probe.name, max(5, min(int(attachment_probe_seconds), 45)))
        visible2 = bool(attach2.get("found"))
        reliable = bool(
            latest_good
            and probe.exists()
            and before_edge
            and trigger_ok
            and found_dialog
            and entered
            and opened
            and (visible1 or visible2)
            and edge_after_cleanup
            and not dialog_after_cleanup
        )
        state.update({
            "upload_trigger_attempted": bool(trigger_ok),
            "file_dialog_found": found_dialog,
            "file_dialog_path_entered": entered,
            "file_dialog_open_invoked": opened,
            "attachment_visible_after_direct_open": visible1,
            "attachment_signal_count_after_direct_open": int(attach1.get("signals") or 0),
            "file_dialog_seen_after_open": dialog_after_open,
            "dialog_cleanup_attempted": cleanup_attempted,
            "dialog_cleanup_method": cleanup_method,
            "file_dialog_seen_after_cleanup": dialog_after_cleanup,
            "edge_window_found_after_cleanup": edge_after_cleanup,
            "attachment_visible_after_cleanup": visible2,
            "attachment_signal_count_after_cleanup": int(attach2.get("signals") or 0),
            "upload_primitive_reliable": reliable,
            "recommended_next_patch": "L26.14M strict upload-submit using direct path entry cleanup primitive" if reliable else "L26.14M repair upload menu focus or file-dialog cleanup detection",
            "result": "PASS" if reliable else "FAIL",
            "failure_layer": "" if reliable else "direct_upload_dialog_cleanup_repair",
            "error": "" if reliable else "Direct upload primitive did not reach reliable state after cleanup.",
        })
    except Exception as exc:
        state.update({
            "result": "FAIL",
            "failure_layer": "direct_upload_dialog_cleanup_repair",
            "error": f"{type(exc).__name__}: {exc}",
            "recommended_next_patch": "L26.14M repair upload menu focus or file-dialog cleanup detection",
        })
    result = DirectUploadDialogCleanupRepairResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: DirectUploadDialogCleanupRepairResult) -> None:
    p = result.to_payload()
    true_keys = [
        "latest_pointer_good_before_probe",
        "probe_file_created",
        "edge_window_found_before_open",
        "upload_trigger_attempted",
        "file_dialog_found",
        "file_dialog_path_entered",
        "file_dialog_open_invoked",
        "dialog_cleanup_attempted",
        "edge_window_found_after_cleanup",
        "attachment_visible_after_cleanup",
        "upload_primitive_reliable",
    ]
    false_keys = [
        "file_dialog_seen_after_cleanup",
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
    if not (p.get("attachment_visible_after_direct_open") or p.get("attachment_visible_after_cleanup")):
        missing.append("attachment_visible_after_direct_open_or_cleanup")
    if int(p.get("attachment_signal_count_after_cleanup") or 0) <= 0:
        missing.append("attachment_signal_count_after_cleanup_positive")
    for key in ("probe_file_path", "probe_file_hash", "dialog_cleanup_method", "recommended_next_patch"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14L acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
