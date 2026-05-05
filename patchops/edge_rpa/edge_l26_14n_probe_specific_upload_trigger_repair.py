from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import pywinauto  # type: ignore
from pywinauto.keyboard import send_keys  # type: ignore

from patchops.edge_rpa.edge_l26_14d_visible_attachment_upload_gate_repair import _attachment_signals
from patchops.edge_rpa.edge_l26_14i_restore_good_canonical_and_strict_upload_gate import canonical_is_good
from patchops.edge_rpa.edge_l26_14m_safe_file_name_control_upload_primitive import (
    close_stale_file_dialogs,
    find_file_name_control,
    invoke_open_from_dialog,
    set_file_name_control,
)
from patchops.edge_rpa.edge_l26_14k_direct_file_dialog_path_entry_repair import (
    create_probe_file,
    edge_windows,
    find_file_dialog,
    focus_edge,
    hash_file,
    wait_file_dialog,
)
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_14n_probe_specific_upload_trigger_repair"


@dataclass(frozen=True)
class ProbeSpecificUploadTriggerRepairResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    latest_pointer_good_before_probe: bool = False
    probe_file_created: bool = False
    probe_file_path: str = ""
    probe_file_hash: str = ""
    probe_baseline_signal_count: int = 0
    probe_baseline_zero: bool = False
    stale_dialog_closed_before_start: bool = False
    edge_window_found_before_open: bool = False
    upload_trigger_attempted: bool = False
    upload_trigger_method: str = ""
    file_dialog_found: bool = False
    file_name_control_found: bool = False
    file_name_control_strategy: str = ""
    global_ctrl_a_sent: bool = False
    desktop_file_list_selection_detected: bool = False
    file_name_value_set: bool = False
    file_name_value_verified: bool = False
    open_button_invoked: bool = False
    enter_pressed_after_value_verified: bool = False
    file_dialog_remaining_after_open: bool = False
    edge_window_found_after_open: bool = False
    probe_specific_attachment_visible_after_open: bool = False
    probe_specific_attachment_signal_count_after_open: int = 0
    generic_attachment_signal_count_after_open: int = 0
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


def write_json(path: Path, result: ProbeSpecificUploadTriggerRepairResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: ProbeSpecificUploadTriggerRepairResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def _info(control: object, name: str) -> str:
    try:
        return str(getattr(control.element_info, name, "") or "")
    except Exception:
        return ""


def _click_control(control: object) -> bool:
    try:
        control.set_focus()
    except Exception:
        pass
    try:
        control.invoke()
        time.sleep(0.7)
        return True
    except Exception:
        pass
    try:
        control.click_input()
        time.sleep(0.7)
        return True
    except Exception:
        return False


def trigger_upload_picker_with_evidence(timeout_seconds: int) -> tuple[bool, str]:
    if not focus_edge():
        return False, "edge_focus_failed"
    try:
        send_keys("{ESC}")
        time.sleep(0.2)
    except Exception:
        pass
    deadline = time.time() + max(5, min(int(timeout_seconds), 40))
    # First prefer real attach/add/upload buttons in the ChatGPT page/UIA tree.
    while time.time() < deadline:
        try:
            desktop = pywinauto.Desktop(backend="uia")
            _wins, wrappers = discover_edge_windows(desktop, edge_process_ids())
            for w in list(wrappers or [])[:2]:
                try:
                    descendants = list(w.descendants())[:3500]
                except Exception:
                    descendants = []
                ranked: list[tuple[int, object, str]] = []
                for c in descendants:
                    try:
                        ctype = _info(c, "control_type")
                        name = _info(c, "name")
                        aid = _info(c, "automation_id")
                        text = " ".join([ctype, name, aid]).lower()
                        if ctype not in {"Button", "MenuItem", "Hyperlink"}:
                            continue
                        score = 0
                        if "attach" in text or "upload" in text or "file" in text or "photo" in text:
                            score += 100
                        if "add" in text or "plus" in text or name.strip() == "+":
                            score += 50
                        if "send" in text or "voice" in text or "dictate" in text or "apps" in text:
                            score -= 200
                        if score > 0:
                            ranked.append((score, c, text[:80]))
                    except Exception:
                        pass
                ranked.sort(key=lambda x: x[0], reverse=True)
                for _score, control, label in ranked[:8]:
                    if _click_control(control):
                        # Some ChatGPT menus need Ctrl+U after +/attach menu opens.
                        for suffix, keys in [("click_only", None), ("plus_ctrl_u", "^u")]:
                            if keys:
                                try:
                                    send_keys(keys)
                                except Exception:
                                    pass
                                time.sleep(1.0)
                            if find_file_dialog() is not None:
                                return True, f"uia_attach_control_{suffix}"
                        try:
                            send_keys("{ESC}")
                        except Exception:
                            pass
            time.sleep(0.5)
        except Exception:
            break
    # Fallback to the operator-proven keyboard path, but only as a trigger, never as file selection.
    try:
        focus_edge()
        send_keys("/")
        time.sleep(0.35)
        send_keys("^u")
        time.sleep(1.2)
        if find_file_dialog() is not None:
            return True, "slash_ctrl_u_fallback"
    except Exception:
        pass
    return False, "no_picker_dialog_opened"


def run_probe_specific_upload_trigger_repair(
    short_live_root: Path,
    latest_canonical_path: Path,
    upload_bridge_dir: Path,
    dialog_open_seconds: int,
    attachment_probe_seconds: int,
) -> ProbeSpecificUploadTriggerRepairResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14n_probe_specific_upload_trigger_repair_result.json"
    live_report_path = short_live_root / "l26_14n_probe_specific_upload_trigger_repair_live_report.txt"
    state: dict[str, object] = {}
    try:
        latest_good = canonical_is_good(latest_canonical_path)
        stale_closed = close_stale_file_dialogs()
        probe = create_probe_file(upload_bridge_dir)
        baseline = _attachment_signals(probe.name, 3)
        baseline_count = int(baseline.get("signals") or 0)
        before_edge = focus_edge()
        state.update({
            "latest_pointer_good_before_probe": latest_good,
            "probe_file_created": probe.exists(),
            "probe_file_path": str(probe),
            "probe_file_hash": hash_file(probe),
            "probe_baseline_signal_count": baseline_count,
            "probe_baseline_zero": baseline_count == 0,
            "stale_dialog_closed_before_start": stale_closed,
            "edge_window_found_before_open": before_edge,
            "global_ctrl_a_sent": False,
            "desktop_file_list_selection_detected": False,
        })
        trigger_ok, trigger_method = trigger_upload_picker_with_evidence(dialog_open_seconds)
        dialog = wait_file_dialog(dialog_open_seconds)
        found_dialog = dialog is not None
        control = None
        strategy = "not_found"
        set_ok = verified = False
        open_invoked = enter_after_verify = False
        if found_dialog:
            control, strategy = find_file_name_control(dialog)
            if control is not None:
                set_ok, verified = set_file_name_control(control, probe)
                open_invoked, enter_after_verify = invoke_open_from_dialog(dialog, verified)
        deadline = time.time() + max(4, min(int(dialog_open_seconds), 30))
        while time.time() < deadline and find_file_dialog() is not None:
            time.sleep(0.5)
        dialog_remaining = find_file_dialog() is not None
        edge_after = bool(edge_windows())
        probe_attach = _attachment_signals(probe.name, attachment_probe_seconds)
        probe_count = int(probe_attach.get("signals") or 0)
        probe_visible = bool(probe_attach.get("found")) and probe_count > baseline_count
        generic = _attachment_signals(".txt", 3)
        generic_count = int(generic.get("signals") or 0)
        reliable = bool(
            latest_good
            and probe.exists()
            and baseline_count == 0
            and stale_closed
            and before_edge
            and trigger_ok
            and found_dialog
            and control is not None
            and set_ok
            and verified
            and (open_invoked or enter_after_verify)
            and not dialog_remaining
            and edge_after
            and probe_visible
        )
        state.update({
            "upload_trigger_attempted": bool(trigger_ok),
            "upload_trigger_method": trigger_method,
            "file_dialog_found": found_dialog,
            "file_name_control_found": control is not None,
            "file_name_control_strategy": strategy,
            "file_name_value_set": set_ok,
            "file_name_value_verified": verified,
            "open_button_invoked": open_invoked,
            "enter_pressed_after_value_verified": enter_after_verify,
            "file_dialog_remaining_after_open": dialog_remaining,
            "edge_window_found_after_open": edge_after,
            "probe_specific_attachment_visible_after_open": probe_visible,
            "probe_specific_attachment_signal_count_after_open": probe_count,
            "generic_attachment_signal_count_after_open": generic_count,
            "upload_primitive_reliable": reliable,
            "recommended_next_patch": "L26.14O strict upload-submit using probe-specific primitive" if reliable else "L26.14O repair upload trigger or probe-specific file-name control path",
            "result": "PASS" if reliable else "FAIL",
            "failure_layer": "" if reliable else "probe_specific_upload_trigger_repair",
            "error": "" if reliable else "Probe-specific upload trigger did not open and stage the current probe file reliably.",
        })
    except Exception as exc:
        state.update({
            "result": "FAIL",
            "failure_layer": "probe_specific_upload_trigger_repair",
            "error": f"{type(exc).__name__}: {exc}",
            "recommended_next_patch": "L26.14O repair upload trigger or probe-specific file-name control path",
        })
    result = ProbeSpecificUploadTriggerRepairResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: ProbeSpecificUploadTriggerRepairResult) -> None:
    p = result.to_payload()
    true_keys = [
        "latest_pointer_good_before_probe",
        "probe_file_created",
        "probe_baseline_zero",
        "stale_dialog_closed_before_start",
        "edge_window_found_before_open",
        "upload_trigger_attempted",
        "file_dialog_found",
        "file_name_control_found",
        "file_name_value_set",
        "file_name_value_verified",
        "edge_window_found_after_open",
        "probe_specific_attachment_visible_after_open",
        "upload_primitive_reliable",
    ]
    false_keys = [
        "global_ctrl_a_sent",
        "desktop_file_list_selection_detected",
        "file_dialog_remaining_after_open",
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
    if not (p.get("open_button_invoked") or p.get("enter_pressed_after_value_verified")):
        missing.append("open_or_verified_enter")
    if int(p.get("probe_specific_attachment_signal_count_after_open") or 0) <= int(p.get("probe_baseline_signal_count") or 0):
        missing.append("probe_specific_attachment_signal_count_increased")
    for key in ("probe_file_path", "probe_file_hash", "upload_trigger_method", "file_name_control_strategy", "recommended_next_patch"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14N acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
