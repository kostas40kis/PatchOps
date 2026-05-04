from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pywinauto import keyboard  # type: ignore

from patchops.edge_rpa.edge_composer_focus_probe import _scan_focus_candidates, run_l26_07_focus_probe
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_08_chatgpt_composer_dry_run_text_gate"


@dataclass(frozen=True)
class ComposerDryRunTextGateResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    targeted_sequence_completed: bool = False
    classification: str = "unknown"
    chatgpt_accessible: bool = False
    focus_probe_completed: bool = False
    composer_focus_verified: bool = False
    candidate_not_browser_chrome: bool = False
    candidate_in_page_scope: bool = False
    dry_run_marker_built: bool = False
    dry_run_marker_hash: str = ""
    dry_run_marker_length: int = 0
    clipboard_backup_captured: bool = False
    clipboard_backup_hash: str = ""
    clipboard_dry_run_marker_set: bool = False
    paste_shortcut_sent: bool = False
    dry_run_text_observed: bool = False
    copied_text_hash: str = ""
    copied_text_length: int = 0
    clear_shortcut_sent: bool = False
    backspace_sent: bool = False
    dry_run_text_cleared: bool = False
    clipboard_restored: bool = False
    dry_run_report_path: str = ""
    focus_json_path: str = ""
    enter_key_sent: bool = False
    chatgpt_prompt_submitted: bool = False
    page_click_performed: bool = False
    download_click_performed: bool = False
    run_package_invoked: bool = False
    pasteback_or_send_performed: bool = False
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_dom_automation_used: bool = False
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _hash_text(value: object) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def _set_clipboard_text(text: str) -> None:
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
    finally:
        root.destroy()


def _get_clipboard_text() -> str:
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    try:
        try:
            value = root.clipboard_get()
        except Exception:
            value = ""
        root.update()
        return str(value)
    finally:
        root.destroy()


def _write_report(path: Path, result: ComposerDryRunTextGateResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.8 ChatGPT composer dry-run text gate",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "enter_key_sent:false",
        "chatgpt_prompt_submitted:false",
        "page_click_performed:false",
        "download_click_performed:false",
        "run_package_invoked:false",
        "Only hashes/lengths of clipboard and dry-run text are reported.",
        "",
        f"classification: {result.classification}",
        f"chatgpt_accessible: {result.chatgpt_accessible}",
        f"composer_focus_verified: {result.composer_focus_verified}",
        f"dry_run_marker_hash: {result.dry_run_marker_hash}",
        f"dry_run_marker_length: {result.dry_run_marker_length}",
        f"clipboard_backup_captured: {result.clipboard_backup_captured}",
        f"clipboard_dry_run_marker_set: {result.clipboard_dry_run_marker_set}",
        f"paste_shortcut_sent: {result.paste_shortcut_sent}",
        f"dry_run_text_observed: {result.dry_run_text_observed}",
        f"copied_text_hash: {result.copied_text_hash}",
        f"copied_text_length: {result.copied_text_length}",
        f"clear_shortcut_sent: {result.clear_shortcut_sent}",
        f"backspace_sent: {result.backspace_sent}",
        f"dry_run_text_cleared: {result.dry_run_text_cleared}",
        f"clipboard_restored: {result.clipboard_restored}",
        f"failure_layer: {result.failure_layer}",
        f"error: {result.error}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: ComposerDryRunTextGateResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def _find_focused_composer_control() -> object:
    import pywinauto  # type: ignore
    edge_pids = edge_process_ids()
    desktop = pywinauto.Desktop(backend="uia")
    _windows, wrappers = discover_edge_windows(desktop, edge_pids)
    if not wrappers:
        raise RuntimeError("No normal Edge window wrappers discovered for dry-run text gate.")
    window = wrappers[0]
    window.set_focus()
    candidates = _scan_focus_candidates(window)
    if not candidates:
        raise RuntimeError("No in-page focusable ChatGPT composer candidate was found for dry-run text gate.")
    candidate, control = candidates[0]
    if candidate.is_browser_chrome or not candidate.is_in_page_scope:
        raise RuntimeError("Best composer focus candidate is not a safe in-page candidate.")
    control.set_focus()
    time.sleep(0.3)
    try:
        if not bool(control.has_keyboard_focus()):
            raise RuntimeError("Composer candidate did not keep keyboard focus before dry-run paste.")
    except Exception:
        pass
    return control


def run_l26_08_dry_run_text_gate(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 8.0) -> ComposerDryRunTextGateResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_08_dry_run_text_gate_result.json"
    report_path = out_dir / "normal_edge_l26_08_dry_run_text_gate_report.txt"
    focus_dir = out_dir / "focus_probe"
    focus_json = focus_dir / "normal_edge_l26_07_composer_focus_result.json"

    marker = "PATCHOPS_L26_08_DRY_RUN_MARKER_DO_NOT_SEND"
    marker_hash = _hash_text(marker)
    marker_len = len(marker)
    clipboard_backup = ""
    clipboard_restored = False

    try:
        focus_result = run_l26_07_focus_probe(output_dir=focus_dir, target_url=target_url, start_if_missing=start_if_missing, settle_seconds=settle_seconds)
        focus_payload = focus_result.to_payload()
        classification = str(focus_payload.get("classification", "unknown"))
        sequence_completed = bool(focus_payload.get("targeted_sequence_completed"))
        accessible = bool(focus_payload.get("chatgpt_accessible"))
        focus_completed = bool(focus_payload.get("result") == "PASS")
        focus_verified = bool(focus_payload.get("composer_focus_verified"))
        candidate_not_chrome = bool(focus_payload.get("candidate_not_browser_chrome"))
        candidate_page_scope = bool(focus_payload.get("candidate_in_page_scope"))

        if not (sequence_completed and accessible and focus_completed and focus_verified and candidate_not_chrome and candidate_page_scope):
            raise RuntimeError(f"L26.8 requires L26.7 focus PASS first; classification={classification!r} focus_verified={focus_verified}.")

        clipboard_backup = _get_clipboard_text()
        backup_captured = True
        backup_hash = _hash_text(clipboard_backup)

        _find_focused_composer_control()
        _set_clipboard_text(marker)
        marker_set = _get_clipboard_text() == marker
        if not marker_set:
            raise RuntimeError("Dry-run marker was not set on clipboard.")

        keyboard.send_keys("^v")
        paste_sent = True
        time.sleep(0.4)

        keyboard.send_keys("^a")
        time.sleep(0.1)
        keyboard.send_keys("^c")
        time.sleep(0.2)
        copied = _get_clipboard_text()
        observed = marker in copied

        sentinel_after_clear = "PATCHOPS_L26_08_EMPTY_SELECTION_SENTINEL"
        keyboard.send_keys("{BACKSPACE}")
        backspace_sent = True
        time.sleep(0.3)
        _set_clipboard_text(sentinel_after_clear)
        keyboard.send_keys("^a")
        clear_shortcut = True
        time.sleep(0.1)
        keyboard.send_keys("^c")
        time.sleep(0.2)
        copied_after_clear = _get_clipboard_text()
        cleared = (copied_after_clear == sentinel_after_clear) or (marker not in copied_after_clear)

        _set_clipboard_text(clipboard_backup)
        clipboard_restored = True

        error = ""
        failure_layer = ""
        result_pass = bool(observed and cleared)
        if not observed:
            failure_layer = "dry_run_text_observation"
            error = "Dry-run marker was pasted but was not observed through copyback."
        elif not cleared:
            failure_layer = "dry_run_text_clear"
            error = "Dry-run marker was observed but not proven cleared. Manually clear the composer before continuing."

        result = ComposerDryRunTextGateResult(
            targeted_sequence_completed=sequence_completed,
            classification=classification,
            chatgpt_accessible=accessible,
            focus_probe_completed=focus_completed,
            composer_focus_verified=focus_verified,
            candidate_not_browser_chrome=candidate_not_chrome,
            candidate_in_page_scope=candidate_page_scope,
            dry_run_marker_built=True,
            dry_run_marker_hash=marker_hash,
            dry_run_marker_length=marker_len,
            clipboard_backup_captured=backup_captured,
            clipboard_backup_hash=backup_hash,
            clipboard_dry_run_marker_set=marker_set,
            paste_shortcut_sent=paste_sent,
            dry_run_text_observed=observed,
            copied_text_hash=_hash_text(copied),
            copied_text_length=len(copied),
            clear_shortcut_sent=clear_shortcut,
            backspace_sent=backspace_sent,
            dry_run_text_cleared=cleared,
            clipboard_restored=clipboard_restored,
            dry_run_report_path=str(report_path),
            focus_json_path=str(focus_json),
            result="PASS" if result_pass else "FAIL",
            failure_layer=failure_layer,
            error=error,
        )
    except Exception as exc:
        try:
            if clipboard_backup:
                _set_clipboard_text(clipboard_backup)
                clipboard_restored = True
        except Exception:
            pass
        result = ComposerDryRunTextGateResult(
            dry_run_marker_built=True,
            dry_run_marker_hash=marker_hash,
            dry_run_marker_length=marker_len,
            clipboard_restored=clipboard_restored,
            dry_run_report_path=str(report_path),
            focus_json_path=str(focus_json),
            result="FAIL",
            failure_layer="dry_run_text_gate",
            error=f"{type(exc).__name__}: {exc}",
        )

    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_08_acceptance(result: ComposerDryRunTextGateResult) -> None:
    payload = result.to_payload()
    required_true = [
        "targeted_sequence_completed",
        "chatgpt_accessible",
        "focus_probe_completed",
        "composer_focus_verified",
        "candidate_not_browser_chrome",
        "candidate_in_page_scope",
        "dry_run_marker_built",
        "clipboard_backup_captured",
        "clipboard_dry_run_marker_set",
        "paste_shortcut_sent",
        "dry_run_text_observed",
        "clear_shortcut_sent",
        "backspace_sent",
        "dry_run_text_cleared",
        "clipboard_restored",
    ]
    required_false = [
        "enter_key_sent",
        "chatgpt_prompt_submitted",
        "page_click_performed",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
        "full_conversation_text_logged",
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if payload.get("classification") != "accessible":
        missing_true.append("classification_accessible")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.8 acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
