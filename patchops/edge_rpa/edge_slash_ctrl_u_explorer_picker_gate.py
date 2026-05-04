from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from pywinauto import keyboard  # type: ignore

from patchops.edge_rpa.edge_soft_composer_edge_upload_gate import _hash_file
from patchops.edge_rpa.edge_upload_safe_report_copy_gate import (
    REQUESTED_CHAT_URL,
    _canonical_url,
    _click_control,
    _ensure_target_loaded,
    _find_plus_control,
    _hash_text,
    _is_onedrive_path,
    _make_upload_safe_copy,
    _observe_staged_file,
    _select_source_report,
    _set_clipboard_text,
    _verify_direct_composer_focus,
)
from patchops.edge_rpa.edge_window_inventory import edge_process_ids

PATCH_NAME = "l26_12i_slash_primed_ctrl_u_explorer_picker_repair"
_PICKER_CLASSES = ("#32770", "CabinetWClass", "ExploreWClass", "ApplicationFrameWindow")
_PICKER_TITLE_WORDS = ("open", "choose", "upload", "file", "explorer", "select")


@dataclass(frozen=True)
class SlashCtrlUExplorerPickerResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    target_url_is_requested_chat: bool = False
    current_url_matches_target: bool = False
    navigation_skipped_existing_target: bool = False
    navigation_attempted: bool = False
    target_page_ready: bool = False
    composer_candidate_found: bool = False
    composer_focus_verified: bool = False
    source_report_found: bool = False
    source_report_hash: str = ""
    source_report_size_bytes: int = 0
    source_report_is_text: bool = False
    upload_safe_copy_created: bool = False
    upload_safe_copy_name: str = ""
    upload_safe_copy_hash: str = ""
    upload_safe_copy_size_bytes: int = 0
    upload_safe_copy_closed: bool = False
    safe_copy_outside_onedrive: bool = False
    allow_report_upload_requested: bool = False
    slash_typed_in_composer: bool = False
    plus_button_found: bool = False
    plus_button_clicked: bool = False
    ctrl_u_shortcut_sent: bool = False
    picker_window_detected: bool = False
    picker_window_kind: str = ""
    picker_path_set_strategy: str = ""
    file_picker_opened: bool = False
    file_picker_path_entered: bool = False
    file_picker_confirmed: bool = False
    file_picker_enter_sent: bool = False
    upload_staging_observed: bool = False
    staged_file_name_hash: str = ""
    staging_observation_method: str = ""
    report_upload_attempted: bool = False
    file_attach_attempted: bool = False
    live_report_path: str = ""
    json_path: str = ""
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


def _write_report(path: Path, result: SlashCtrlUExplorerPickerResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.12I slash-primed Ctrl+U Explorer picker repair",
        f"current_url_matches_target: {result.current_url_matches_target}",
        f"navigation_skipped_existing_target: {result.navigation_skipped_existing_target}",
        f"composer_candidate_found: {result.composer_candidate_found}",
        f"composer_focus_verified: {result.composer_focus_verified}",
        f"upload_safe_copy_created: {result.upload_safe_copy_created}",
        f"upload_safe_copy_closed: {result.upload_safe_copy_closed}",
        f"safe_copy_outside_onedrive: {result.safe_copy_outside_onedrive}",
        f"slash_typed_in_composer: {result.slash_typed_in_composer}",
        f"plus_button_clicked: {result.plus_button_clicked}",
        f"ctrl_u_shortcut_sent: {result.ctrl_u_shortcut_sent}",
        f"picker_window_detected: {result.picker_window_detected}",
        f"picker_window_kind: {result.picker_window_kind}",
        f"picker_path_set_strategy: {result.picker_path_set_strategy}",
        f"file_picker_opened: {result.file_picker_opened}",
        f"file_picker_path_entered: {result.file_picker_path_entered}",
        f"file_picker_confirmed: {result.file_picker_confirmed}",
        f"upload_staging_observed: {result.upload_staging_observed}",
        "chatgpt_submit_enter_sent:false",
        "send_submit_performed:false",
        "chatgpt_prompt_submitted:false",
        "conversation_text_logged:false",
        "prompt_text_logged:false",
        "file_content_logged:false",
        f"failure_layer: {result.failure_layer}",
        f"error: {result.error}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: SlashCtrlUExplorerPickerResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def _known_top_windows() -> set[int]:
    import pywinauto  # type: ignore
    desktop = pywinauto.Desktop(backend="uia")
    handles: set[int] = set()
    try:
        for window in desktop.windows():
            try:
                handles.add(int(window.handle))
            except Exception:
                pass
    except Exception:
        pass
    return handles


def _looks_like_picker_window(window: object, known_handles: set[int]) -> tuple[bool, str]:
    try:
        handle = int(window.handle)
    except Exception:
        handle = 0
    try:
        title = str(window.window_text() or "")
    except Exception:
        title = ""
    try:
        class_name = str(window.element_info.class_name or "")
    except Exception:
        class_name = ""
    try:
        pid = int(window.element_info.process_id or 0)
    except Exception:
        pid = 0
    lower = " ".join([title, class_name]).lower()
    if class_name in _PICKER_CLASSES:
        return True, class_name
    if handle not in known_handles and any(word in lower for word in _PICKER_TITLE_WORDS):
        return True, class_name or "new-window"
    if handle not in known_handles and "explorer" in lower:
        return True, class_name or "explorer"
    # Some file dialogs belong to msedge.exe but expose Edit controls without a useful title.
    if pid not in edge_process_ids():
        try:
            edits = window.descendants(control_type="Edit")
            buttons = window.descendants(control_type="Button")
            if edits and buttons:
                return True, class_name or "edit-button-window"
        except Exception:
            pass
    return False, ""


def _find_broad_upload_picker(known_handles: set[int], timeout_seconds: float = 15.0) -> tuple[object, str]:
    import pywinauto  # type: ignore
    desktop = pywinauto.Desktop(backend="uia")
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            windows = list(desktop.windows())
        except Exception:
            windows = []
        # Prefer new windows, then picker-looking existing windows.
        windows.sort(key=lambda w: 0 if int(getattr(w, "handle", 0) or 0) not in known_handles else 1)
        for window in windows:
            try:
                ok, kind = _looks_like_picker_window(window, known_handles)
            except Exception:
                ok, kind = False, ""
            if ok:
                try:
                    window.set_focus()
                except Exception:
                    pass
                return window, kind
        time.sleep(0.25)
    raise RuntimeError("Slash + Ctrl+U opened no detectable OS picker/Explorer window.")


def _set_picker_path_broad(window: object, file_path: Path) -> str:
    path_text = str(file_path)
    try:
        window.set_focus()
    except Exception:
        pass
    time.sleep(0.2)
    # Best for classic Open dialog: Alt+N focuses File name.
    try:
        keyboard.send_keys("%n")
        time.sleep(0.2)
        _set_clipboard_text(path_text)
        keyboard.send_keys("^v")
        time.sleep(0.2)
        keyboard.send_keys("{ENTER}")
        return "alt_n_clipboard_enter"
    except Exception:
        pass
    # Best for Explorer-style window: address bar with full file path then Enter.
    try:
        window.set_focus()
    except Exception:
        pass
    keyboard.send_keys("^l")
    time.sleep(0.2)
    _set_clipboard_text(path_text)
    keyboard.send_keys("^v")
    time.sleep(0.2)
    keyboard.send_keys("{ENTER}")
    return "ctrl_l_clipboard_enter"


def run_l26_12i_slash_ctrl_u_explorer_picker_gate(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 10.0, allow_report_upload: bool = False) -> SlashCtrlUExplorerPickerResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_12i_slash_ctrl_u_explorer_picker_result.json"
    report_path = out_dir / "normal_edge_l26_12i_slash_ctrl_u_explorer_picker_report.txt"
    target_ok = _canonical_url(target_url) == _canonical_url(REQUESTED_CHAT_URL)
    state: dict[str, object] = {
        "target_url_is_requested_chat": target_ok,
        "allow_report_upload_requested": allow_report_upload,
        "live_report_path": str(report_path),
        "json_path": str(json_path),
    }
    try:
        if not allow_report_upload:
            raise RuntimeError("L26.12I requires explicit --allow-report-upload.")
        current_observed, page_ready, skipped_nav, attempted_nav, current_url = _ensure_target_loaded(out_dir, target_url, start_if_missing, settle_seconds)
        state.update({
            "current_url_matches_target": _canonical_url(current_url) == _canonical_url(target_url),
            "navigation_skipped_existing_target": skipped_nav,
            "navigation_attempted": attempted_nav,
            "target_page_ready": page_ready,
        })
        if not (target_ok and page_ready):
            raise RuntimeError("Target chat page is not ready.")

        source = _select_source_report()
        safe_copy = _make_upload_safe_copy(source, out_dir)
        source_hash = _hash_file(source)
        copy_hash = _hash_file(safe_copy)
        source_size = source.stat().st_size
        copy_size = safe_copy.stat().st_size
        state.update({
            "source_report_found": True,
            "source_report_hash": source_hash,
            "source_report_size_bytes": int(source_size),
            "source_report_is_text": source.suffix.lower() == ".txt",
            "upload_safe_copy_created": True,
            "upload_safe_copy_name": safe_copy.name,
            "upload_safe_copy_hash": copy_hash,
            "upload_safe_copy_size_bytes": int(copy_size),
            "upload_safe_copy_closed": True,
            "safe_copy_outside_onedrive": not _is_onedrive_path(safe_copy),
        })
        if source_hash != copy_hash or source_size != copy_size:
            raise RuntimeError("Upload-safe copy hash/size mismatch.")

        composer_found, focus_verified = _verify_direct_composer_focus()
        state.update({"composer_candidate_found": composer_found, "composer_focus_verified": focus_verified})
        if not composer_found:
            raise RuntimeError("No safe composer candidate found; refusing upload shortcut.")
        keyboard.send_keys("/")
        state.update({"slash_typed_in_composer": True})
        time.sleep(0.25)
        plus, plus_control = _find_plus_control()
        state.update({"plus_button_found": True})
        _click_control(plus_control)
        state.update({"plus_button_clicked": True})
        time.sleep(0.6)
        known_handles = _known_top_windows()
        keyboard.send_keys("^u")
        state.update({"ctrl_u_shortcut_sent": True})
        picker, picker_kind = _find_broad_upload_picker(known_handles, timeout_seconds=18.0)
        state.update({
            "picker_window_detected": True,
            "picker_window_kind": picker_kind,
            "file_picker_opened": True,
            "report_upload_attempted": True,
            "file_attach_attempted": True,
        })
        strategy = _set_picker_path_broad(picker, safe_copy)
        state.update({
            "picker_path_set_strategy": strategy,
            "file_picker_path_entered": True,
            "file_picker_confirmed": True,
            "file_picker_enter_sent": True,
        })
        staged, method = _observe_staged_file(safe_copy.name, timeout_seconds=60.0)
        state.update({
            "upload_staging_observed": staged,
            "staged_file_name_hash": _hash_text(safe_copy.name),
            "staging_observation_method": method,
            "result": "PASS" if staged else "FAIL",
            "failure_layer": "" if staged else "slash_ctrl_u_upload_staging_observation",
            "error": "" if staged else "Slash + Ctrl+U picker selected the safe copy, but staged attachment was not observed.",
        })
    except Exception as exc:
        state.update({
            "result": "FAIL",
            "failure_layer": "slash_primed_ctrl_u_explorer_picker_repair",
            "error": f"{type(exc).__name__}: {exc}",
        })
    result = SlashCtrlUExplorerPickerResult(**state)
    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_12i_acceptance(result: SlashCtrlUExplorerPickerResult) -> None:
    payload = result.to_payload()
    required_true = [
        "target_url_is_requested_chat",
        "current_url_matches_target",
        "navigation_skipped_existing_target",
        "target_page_ready",
        "composer_candidate_found",
        "source_report_found",
        "source_report_is_text",
        "upload_safe_copy_created",
        "upload_safe_copy_closed",
        "safe_copy_outside_onedrive",
        "allow_report_upload_requested",
        "slash_typed_in_composer",
        "plus_button_found",
        "plus_button_clicked",
        "ctrl_u_shortcut_sent",
        "picker_window_detected",
        "file_picker_opened",
        "file_picker_path_entered",
        "file_picker_confirmed",
        "file_picker_enter_sent",
        "upload_staging_observed",
        "report_upload_attempted",
        "file_attach_attempted",
    ]
    required_false = [
        "navigation_attempted",
        "chatgpt_submit_enter_sent",
        "send_submit_performed",
        "chatgpt_prompt_submitted",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
        "full_conversation_text_logged",
        "prompt_text_logged",
        "file_content_logged",
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    for key in ("source_report_hash", "upload_safe_copy_hash", "staged_file_name_hash", "picker_window_kind", "picker_path_set_strategy"):
        if not payload.get(key):
            missing_true.append(key + "_nonempty")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.12I acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
