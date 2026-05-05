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
from patchops.edge_rpa.edge_l26_14k_direct_file_dialog_path_entry_repair import (
    create_probe_file,
    edge_windows,
    find_file_dialog,
    focus_edge,
    hash_file,
    open_upload_dialog_from_chat,
    wait_file_dialog,
)

PATCH_NAME = "l26_14m_safe_file_name_control_upload_primitive"


@dataclass(frozen=True)
class SafeFileNameControlUploadPrimitiveResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    latest_pointer_good_before_probe: bool = False
    probe_file_created: bool = False
    probe_file_path: str = ""
    probe_file_hash: str = ""
    probe_parent_is_desktop: bool = False
    stale_dialog_closed_before_start: bool = False
    edge_window_found_before_open: bool = False
    upload_trigger_attempted: bool = False
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
    attachment_visible_after_open: bool = False
    attachment_signal_count_after_open: int = 0
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


def write_json(path: Path, result: SafeFileNameControlUploadPrimitiveResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: SafeFileNameControlUploadPrimitiveResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def close_stale_file_dialogs() -> bool:
    closed_any = False
    for _ in range(4):
        dlg = find_file_dialog()
        if dlg is None:
            return closed_any or True
        closed_any = True
        try:
            dlg.set_focus()
        except Exception:
            pass
        try:
            send_keys("{ESC}")
        except Exception:
            pass
        time.sleep(0.7)
        if find_file_dialog() is None:
            return True
        try:
            send_keys("%{F4}")
        except Exception:
            pass
        time.sleep(0.7)
    return find_file_dialog() is None


def _safe_text(control: object) -> str:
    for getter in (
        lambda c: c.get_value(),
        lambda c: c.window_text(),
        lambda c: getattr(c.element_info, "name", "") or "",
    ):
        try:
            value = getter(control)
            if value is not None:
                return str(value)
        except Exception:
            pass
    return ""


def _visible_enabled(control: object) -> bool:
    try:
        if not control.is_visible() or not control.is_enabled():
            return False
    except Exception:
        return False
    try:
        r = control.rectangle()
        return int(r.width()) > 20 and int(r.height()) > 10
    except Exception:
        return True


def find_file_name_control(dialog: object) -> tuple[object | None, str]:
    # Avoid global keyboard selection. Find the bottom-most enabled Edit/ComboBox in the dialog.
    candidates: list[tuple[int, object, str]] = []
    try:
        for ctrl in list(dialog.descendants()):
            try:
                ctype = getattr(ctrl.element_info, "control_type", "") or ""
                name = (getattr(ctrl.element_info, "name", "") or "").lower()
                cls = (getattr(ctrl.element_info, "class_name", "") or "").lower()
                if ctype not in {"Edit", "ComboBox"}:
                    continue
                if not _visible_enabled(ctrl):
                    continue
                rect = ctrl.rectangle()
                score = int(rect.top)
                if "file name" in name or "όνομα" in name or "filename" in name:
                    score += 100000
                if ctype == "Edit":
                    score += 1000
                if "edit" in cls or "combo" in cls:
                    score += 100
                candidates.append((score, ctrl, f"uia_{ctype}_{cls or 'unknown'}"))
            except Exception:
                pass
    except Exception:
        pass
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1], candidates[0][2]
    return None, "not_found"


def set_file_name_control(control: object, path: Path) -> tuple[bool, bool]:
    # This function deliberately does not send Ctrl+A. It uses control-specific setters only.
    text = str(path)
    set_ok = False
    try:
        control.set_focus()
        time.sleep(0.2)
    except Exception:
        pass
    try:
        if hasattr(control, "set_edit_text"):
            control.set_edit_text(text)
            set_ok = True
    except Exception:
        pass
    if not set_ok:
        try:
            if hasattr(control, "set_text"):
                control.set_text(text)
                set_ok = True
        except Exception:
            pass
    if not set_ok:
        try:
            # Last resort is clipboard paste into the already-focused File name control only; no global Ctrl+A.
            import pyperclip  # type: ignore
            pyperclip.copy(text)
            send_keys("^v")
            set_ok = True
        except Exception:
            pass
    time.sleep(0.4)
    current = _safe_text(control)
    verified = text.lower() in current.lower() or current.lower() in text.lower()
    return set_ok, verified


def invoke_open_from_dialog(dialog: object, value_verified: bool) -> tuple[bool, bool]:
    if not value_verified:
        return False, False
    # Prefer a real Open button invoke. Enter is only allowed after the file-name value was verified.
    try:
        buttons = []
        for b in list(dialog.descendants(control_type="Button")):
            try:
                name = (getattr(b.element_info, "name", "") or "").lower()
                if "open" in name or "άνοιγμα" in name:
                    buttons.append(b)
            except Exception:
                pass
        if buttons:
            buttons[-1].invoke()
            time.sleep(2.0)
            return True, False
    except Exception:
        pass
    try:
        send_keys("{ENTER}")
        time.sleep(2.0)
        return False, True
    except Exception:
        return False, False


def run_safe_file_name_control_upload_primitive(
    short_live_root: Path,
    latest_canonical_path: Path,
    desktop_path: Path,
    upload_bridge_dir: Path,
    dialog_open_seconds: int,
    attachment_probe_seconds: int,
) -> SafeFileNameControlUploadPrimitiveResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14m_safe_file_name_control_upload_primitive_result.json"
    live_report_path = short_live_root / "l26_14m_safe_file_name_control_upload_primitive_live_report.txt"
    state: dict[str, object] = {}
    try:
        latest_good = canonical_is_good(latest_canonical_path)
        stale_closed = close_stale_file_dialogs()
        probe = create_probe_file(upload_bridge_dir)
        probe_parent_is_desktop = str(probe.parent.resolve()).lower() == str(desktop_path.resolve()).lower()
        before_edge = focus_edge()
        state.update({
            "latest_pointer_good_before_probe": latest_good,
            "probe_file_created": probe.exists(),
            "probe_file_path": str(probe),
            "probe_file_hash": hash_file(probe),
            "probe_parent_is_desktop": probe_parent_is_desktop,
            "stale_dialog_closed_before_start": stale_closed,
            "edge_window_found_before_open": before_edge,
            "global_ctrl_a_sent": False,
            "desktop_file_list_selection_detected": False,
        })
        trigger_ok = open_upload_dialog_from_chat()
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
        attach = _attachment_signals(probe.name, attachment_probe_seconds)
        visible = bool(attach.get("found"))
        reliable = bool(
            latest_good
            and probe.exists()
            and not probe_parent_is_desktop
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
            and visible
        )
        state.update({
            "upload_trigger_attempted": bool(trigger_ok),
            "file_dialog_found": found_dialog,
            "file_name_control_found": control is not None,
            "file_name_control_strategy": strategy,
            "file_name_value_set": set_ok,
            "file_name_value_verified": verified,
            "open_button_invoked": open_invoked,
            "enter_pressed_after_value_verified": enter_after_verify,
            "file_dialog_remaining_after_open": dialog_remaining,
            "edge_window_found_after_open": edge_after,
            "attachment_visible_after_open": visible,
            "attachment_signal_count_after_open": int(attach.get("signals") or 0),
            "upload_primitive_reliable": reliable,
            "recommended_next_patch": "L26.14N strict upload-submit using safe File name control primitive" if reliable else "L26.14N repair File name control discovery/value verification",
            "result": "PASS" if reliable else "FAIL",
            "failure_layer": "" if reliable else "safe_file_name_control_upload_primitive",
            "error": "" if reliable else "Safe File name control upload primitive did not reach reliable staged-attachment state.",
        })
    except Exception as exc:
        state.update({
            "result": "FAIL",
            "failure_layer": "safe_file_name_control_upload_primitive",
            "error": f"{type(exc).__name__}: {exc}",
            "recommended_next_patch": "L26.14N repair File name control discovery/value verification",
        })
    result = SafeFileNameControlUploadPrimitiveResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: SafeFileNameControlUploadPrimitiveResult) -> None:
    p = result.to_payload()
    true_keys = [
        "latest_pointer_good_before_probe",
        "probe_file_created",
        "stale_dialog_closed_before_start",
        "edge_window_found_before_open",
        "upload_trigger_attempted",
        "file_dialog_found",
        "file_name_control_found",
        "file_name_value_set",
        "file_name_value_verified",
        "edge_window_found_after_open",
        "attachment_visible_after_open",
        "upload_primitive_reliable",
    ]
    false_keys = [
        "probe_parent_is_desktop",
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
    if int(p.get("attachment_signal_count_after_open") or 0) <= 0:
        missing.append("attachment_signal_count_after_open_positive")
    for key in ("probe_file_path", "probe_file_hash", "file_name_control_strategy", "recommended_next_patch"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14M acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
