from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import pywinauto  # type: ignore
from pywinauto.keyboard import send_keys  # type: ignore

from patchops.edge_rpa.edge_l26_14d_visible_attachment_upload_gate_repair import _attachment_signals
from patchops.edge_rpa.edge_l26_14i_restore_good_canonical_and_strict_upload_gate import canonical_is_good
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_14k_direct_file_dialog_path_entry_repair"


@dataclass(frozen=True)
class DirectFileDialogPathEntryRepairResult:
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
    file_dialog_closed_after_open: bool = False
    edge_window_found_after_open: bool = False
    attachment_visible_after_direct_open: bool = False
    attachment_signal_count_after_direct_open: int = 0
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


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def write_json(path: Path, result: DirectFileDialogPathEntryRepairResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: DirectFileDialogPathEntryRepairResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def create_probe_file(upload_bridge_dir: Path) -> Path:
    upload_bridge_dir.mkdir(parents=True, exist_ok=True)
    path = upload_bridge_dir / f"patchops_direct_dialog_probe_{int(time.time())}.txt"
    path.write_text(
        "PATCHOPS DIRECT FILE DIALOG PATH ENTRY PROBE\n"
        f"patch_name: {PATCH_NAME}\n"
        "purpose: verify full-path file dialog upload only; do not submit\n",
        encoding="utf-8",
    )
    return path


def edge_windows() -> list[object]:
    desktop = pywinauto.Desktop(backend="uia")
    _windows, wrappers = discover_edge_windows(desktop, edge_process_ids())
    return list(wrappers or [])


def focus_edge() -> bool:
    try:
        windows = edge_windows()
        if not windows:
            return False
        w = windows[0]
        w.set_focus()
        time.sleep(0.5)
        return True
    except Exception:
        return False


def find_file_dialog() -> object | None:
    try:
        desktop = pywinauto.Desktop(backend="uia")
        for w in desktop.windows():
            try:
                info = w.element_info
                name = (getattr(info, "name", "") or "").lower()
                control_type = getattr(info, "control_type", "") or ""
                if control_type == "Window" and ("open" in name or "upload" in name or "choose" in name or "file" in name):
                    return w
            except Exception:
                pass
    except Exception:
        return None
    return None


def wait_file_dialog(timeout_seconds: int) -> object | None:
    deadline = time.time() + max(3, min(int(timeout_seconds), 40))
    while time.time() < deadline:
        dlg = find_file_dialog()
        if dlg is not None:
            return dlg
        time.sleep(0.5)
    return None


def open_upload_dialog_from_chat() -> bool:
    if not focus_edge():
        return False
    # Use the shortcut path the operator taught us: slash opens the menu, Ctrl+U opens Upload file.
    # We do not send Enter to the chat composer and do not submit a message.
    try:
        send_keys("/")
        time.sleep(0.35)
        send_keys("^u")
        time.sleep(1.0)
        if find_file_dialog() is not None:
            return True
    except Exception:
        pass
    # Fallback: Ctrl+U alone can open the upload picker if the menu is already active.
    try:
        focus_edge()
        send_keys("^u")
        time.sleep(1.0)
        return find_file_dialog() is not None
    except Exception:
        return False


def enter_full_path_and_open(dialog: object, probe_path: Path) -> tuple[bool, bool]:
    try:
        dialog.set_focus()
    except Exception:
        pass
    # Most reliable Windows picker method: focus File name using Alt+N, paste literal full path, press Enter.
    try:
        send_keys("%n")
        time.sleep(0.2)
        send_keys("^a")
        time.sleep(0.1)
        send_keys(str(probe_path), with_spaces=True)
        time.sleep(0.3)
        send_keys("{ENTER}")
        time.sleep(2.0)
        return True, True
    except Exception:
        pass
    # Fallback: set first Edit control if exposed, then Enter.
    try:
        edits = dialog.descendants(control_type="Edit")
        if edits:
            edits[0].set_edit_text(str(probe_path))
            time.sleep(0.3)
            send_keys("{ENTER}")
            time.sleep(2.0)
            return True, True
    except Exception:
        pass
    return False, False


def run_direct_file_dialog_path_entry_repair(
    short_live_root: Path,
    latest_canonical_path: Path,
    upload_bridge_dir: Path,
    dialog_open_seconds: int,
    attachment_probe_seconds: int,
) -> DirectFileDialogPathEntryRepairResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14k_direct_file_dialog_path_entry_repair_result.json"
    live_report_path = short_live_root / "l26_14k_direct_file_dialog_path_entry_repair_live_report.txt"
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
        # Wait for dialog to close after Open/Enter.
        deadline = time.time() + max(3, min(int(dialog_open_seconds), 40))
        closed = False
        while time.time() < deadline:
            if find_file_dialog() is None:
                closed = True
                break
            time.sleep(0.5)
        edge_after = bool(edge_windows())
        attach = _attachment_signals(probe.name, attachment_probe_seconds)
        visible = bool(attach.get("found"))
        reliable = bool(trigger_ok and found_dialog and entered and opened and closed and edge_after and visible)
        state.update({
            "upload_trigger_attempted": bool(trigger_ok),
            "file_dialog_found": found_dialog,
            "file_dialog_path_entered": entered,
            "file_dialog_open_invoked": opened,
            "file_dialog_closed_after_open": closed,
            "edge_window_found_after_open": edge_after,
            "attachment_visible_after_direct_open": visible,
            "attachment_signal_count_after_direct_open": int(attach.get("signals") or 0),
            "upload_primitive_reliable": reliable,
            "recommended_next_patch": "L26.14L strict upload-submit rerun using direct file-dialog path entry" if reliable else "L26.14L repair upload trigger/menu focus before path entry",
            "result": "PASS" if reliable else "FAIL",
            "failure_layer": "" if reliable else "direct_file_dialog_path_entry_repair",
            "error": "" if reliable else "Direct file-dialog path entry did not produce visible/staged attachment without leaving the dialog open.",
        })
    except Exception as exc:
        state.update({
            "result": "FAIL",
            "failure_layer": "direct_file_dialog_path_entry_repair",
            "error": f"{type(exc).__name__}: {exc}",
            "recommended_next_patch": "L26.14L repair upload trigger/menu focus before path entry",
        })
    result = DirectFileDialogPathEntryRepairResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: DirectFileDialogPathEntryRepairResult) -> None:
    p = result.to_payload()
    true_keys = [
        "latest_pointer_good_before_probe",
        "probe_file_created",
        "edge_window_found_before_open",
        "upload_trigger_attempted",
        "file_dialog_found",
        "file_dialog_path_entered",
        "file_dialog_open_invoked",
        "file_dialog_closed_after_open",
        "edge_window_found_after_open",
        "attachment_visible_after_direct_open",
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
    if int(p.get("attachment_signal_count_after_direct_open") or 0) <= 0:
        missing.append("attachment_signal_count_after_direct_open_positive")
    for key in ("probe_file_path", "probe_file_hash", "recommended_next_patch"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14K acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
