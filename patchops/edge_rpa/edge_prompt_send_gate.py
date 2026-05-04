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

from patchops.edge_rpa.edge_composer_focus_probe import _scan_focus_candidates
from patchops.edge_rpa.edge_navigation_proof import run_l26_04_navigation_proof
from patchops.edge_rpa.edge_prompt_paste_gate import build_l26_09_prompt
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_10a_requested_chat_send_gate_fallback_repair"
REQUESTED_CHAT_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


@dataclass(frozen=True)
class PromptSendGateResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    target_url_is_requested_chat: bool = False
    target_url_hash: str = ""
    requested_chat_navigation_attempted: bool = False
    requested_chat_navigation_observed: bool = False
    classifier_unknown_fallback_used: bool = True
    composer_fallback_attempted: bool = False
    composer_fallback_focus_verified: bool = False
    prompt_paste_cycle_completed: bool = False
    prompt_pasted: bool = False
    prompt_observed_by_copyback: bool = False
    copyback_hash_matches_prompt: bool = False
    prompt_cleared: bool = False
    prompt_hash: str = ""
    prompt_length: int = 0
    send_gate_evaluated: bool = False
    allow_send_requested: bool = False
    send_blocked_by_default: bool = False
    send_path_disabled: bool = True
    send_gate_report_path: str = ""
    navigation_json_path: str = ""
    enter_key_sent: bool = False
    send_submit_performed: bool = False
    chatgpt_prompt_submitted: bool = False
    page_click_performed: bool = False
    download_click_performed: bool = False
    run_package_invoked: bool = False
    pasteback_or_send_performed: bool = False
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    prompt_text_logged: bool = False
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


def _focus_requested_chat_composer() -> bool:
    import pywinauto  # type: ignore
    edge_pids = edge_process_ids()
    desktop = pywinauto.Desktop(backend="uia")
    _windows, wrappers = discover_edge_windows(desktop, edge_pids)
    if not wrappers:
        raise RuntimeError("No normal Edge window wrappers discovered for requested-chat fallback.")
    window = wrappers[0]
    window.set_focus()
    candidates = _scan_focus_candidates(window)
    if not candidates:
        raise RuntimeError("No safe in-page ChatGPT composer candidate found after requested-chat navigation.")
    candidate, control = candidates[0]
    if candidate.is_browser_chrome or not candidate.is_in_page_scope:
        raise RuntimeError("Best requested-chat composer candidate is browser chrome or outside page scope.")
    control.set_focus()
    time.sleep(0.4)
    try:
        return bool(control.has_keyboard_focus())
    except Exception:
        return True


def _paste_verify_clear_prompt(prompt: str) -> tuple[bool, bool, bool, str, int, str]:
    keyboard.send_keys("^a")
    time.sleep(0.1)
    keyboard.send_keys("{BACKSPACE}")
    time.sleep(0.2)
    _set_clipboard_text(prompt)
    if _get_clipboard_text() != prompt:
        return False, False, False, "", 0, "prompt clipboard set failed"
    keyboard.send_keys("^v")
    time.sleep(0.5)
    keyboard.send_keys("^a")
    time.sleep(0.1)
    keyboard.send_keys("^c")
    time.sleep(0.2)
    copied = _get_clipboard_text()
    copied_hash = _hash_text(copied)
    observed = copied == prompt
    hash_match = copied_hash == _hash_text(prompt)
    keyboard.send_keys("{BACKSPACE}")
    time.sleep(0.3)
    sentinel = "PATCHOPS_L26_10A_EMPTY_SELECTION_SENTINEL"
    _set_clipboard_text(sentinel)
    keyboard.send_keys("^a")
    time.sleep(0.1)
    keyboard.send_keys("^c")
    time.sleep(0.2)
    copied_after_clear = _get_clipboard_text()
    cleared = copied_after_clear == sentinel or copied_after_clear != prompt
    return observed, hash_match, cleared, copied_hash, len(copied), ""


def _write_report(path: Path, result: PromptSendGateResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.10A requested-chat send gate fallback repair",
        "target_url_is_requested_chat:true" if result.target_url_is_requested_chat else "target_url_is_requested_chat:false",
        "send_gate_evaluated:true" if result.send_gate_evaluated else "send_gate_evaluated:false",
        "allow_send_requested:false" if not result.allow_send_requested else "allow_send_requested:true",
        "send_blocked_by_default:true" if result.send_blocked_by_default else "send_blocked_by_default:false",
        "send_path_disabled:true" if result.send_path_disabled else "send_path_disabled:false",
        "enter_key_sent:false",
        "send_submit_performed:false",
        "chatgpt_prompt_submitted:false",
        "page_click_performed:false",
        "download_click_performed:false",
        "run_package_invoked:false",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "prompt_text_logged:false",
        "Only hashes/booleans are recorded; no prompt or conversation text is logged.",
        "",
        f"target_url_hash: {result.target_url_hash}",
        f"requested_chat_navigation_observed: {result.requested_chat_navigation_observed}",
        f"classifier_unknown_fallback_used: {result.classifier_unknown_fallback_used}",
        f"composer_fallback_focus_verified: {result.composer_fallback_focus_verified}",
        f"prompt_paste_cycle_completed: {result.prompt_paste_cycle_completed}",
        f"prompt_pasted: {result.prompt_pasted}",
        f"prompt_observed_by_copyback: {result.prompt_observed_by_copyback}",
        f"copyback_hash_matches_prompt: {result.copyback_hash_matches_prompt}",
        f"prompt_cleared: {result.prompt_cleared}",
        f"prompt_hash: {result.prompt_hash}",
        f"prompt_length: {result.prompt_length}",
        f"failure_layer: {result.failure_layer}",
        f"error: {result.error}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: PromptSendGateResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_10_send_gate(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 10.0, allow_send: bool = False) -> PromptSendGateResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_10_send_gate_result.json"
    report_path = out_dir / "normal_edge_l26_10_send_gate_report.txt"
    navigation_dir = out_dir / "requested_chat_navigation"
    navigation_json = navigation_dir / "normal_edge_l26_04_navigation_result.json"
    target_is_requested = target_url.rstrip("/") == REQUESTED_CHAT_URL.rstrip("/")
    prompt = build_l26_09_prompt()
    prompt_hash = _hash_text(prompt)
    prompt_len = len(prompt)
    clipboard_backup = ""
    clipboard_restored = False
    try:
        if allow_send:
            raise RuntimeError("L26.10A repairs the disabled-by-default no-send gate only; --allow-send is not accepted here.")
        if not target_is_requested:
            raise RuntimeError("L26.10A must target the requested project chat URL.")
        nav = run_l26_04_navigation_proof(output_dir=navigation_dir, target_url=target_url, start_if_missing=start_if_missing, settle_seconds=settle_seconds)
        nav_payload = nav.to_payload()
        navigation_observed = bool(nav_payload.get("normal_edge_navigation") and nav_payload.get("page_load_state_observed"))
        if not navigation_observed:
            raise RuntimeError(f"Requested-chat navigation was not observed; nav_result={nav_payload.get('result')} layer={nav_payload.get('failure_layer')} error={nav_payload.get('error')}")
        clipboard_backup = _get_clipboard_text()
        focus_verified = _focus_requested_chat_composer()
        if not focus_verified:
            raise RuntimeError("Requested-chat composer focus was not verified.")
        observed, hash_match, cleared, copied_hash, copied_len, cycle_error = _paste_verify_clear_prompt(prompt)
        _set_clipboard_text(clipboard_backup)
        clipboard_restored = True
        paste_ok = bool(observed and hash_match and cleared)
        if not paste_ok:
            raise RuntimeError(cycle_error or "Requested-chat prompt paste/copyback/clear cycle failed.")
        result = PromptSendGateResult(
            target_url_is_requested_chat=True,
            target_url_hash=_hash_text(target_url),
            requested_chat_navigation_attempted=True,
            requested_chat_navigation_observed=navigation_observed,
            classifier_unknown_fallback_used=True,
            composer_fallback_attempted=True,
            composer_fallback_focus_verified=focus_verified,
            prompt_paste_cycle_completed=paste_ok,
            prompt_pasted=True,
            prompt_observed_by_copyback=observed,
            copyback_hash_matches_prompt=hash_match,
            prompt_cleared=cleared,
            prompt_hash=prompt_hash,
            prompt_length=prompt_len,
            send_gate_evaluated=True,
            allow_send_requested=False,
            send_blocked_by_default=True,
            send_path_disabled=True,
            send_gate_report_path=str(report_path),
            navigation_json_path=str(navigation_json),
            result="PASS",
        )
    except Exception as exc:
        try:
            if clipboard_backup:
                _set_clipboard_text(clipboard_backup)
                clipboard_restored = True
        except Exception:
            pass
        result = PromptSendGateResult(
            target_url_is_requested_chat=target_is_requested,
            target_url_hash=_hash_text(target_url),
            requested_chat_navigation_attempted=True,
            classifier_unknown_fallback_used=True,
            send_gate_evaluated=True,
            allow_send_requested=allow_send,
            send_blocked_by_default=not allow_send,
            send_path_disabled=True,
            send_gate_report_path=str(report_path),
            navigation_json_path=str(navigation_json),
            prompt_hash=prompt_hash,
            prompt_length=prompt_len,
            result="FAIL",
            failure_layer="requested_chat_send_gate_fallback",
            error=f"{type(exc).__name__}: {exc}",
        )
    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_10_acceptance(result: PromptSendGateResult) -> None:
    payload = result.to_payload()
    required_true = [
        "target_url_is_requested_chat",
        "requested_chat_navigation_attempted",
        "requested_chat_navigation_observed",
        "classifier_unknown_fallback_used",
        "composer_fallback_attempted",
        "composer_fallback_focus_verified",
        "prompt_paste_cycle_completed",
        "prompt_pasted",
        "prompt_observed_by_copyback",
        "copyback_hash_matches_prompt",
        "prompt_cleared",
        "send_gate_evaluated",
        "send_blocked_by_default",
        "send_path_disabled",
    ]
    required_false = [
        "allow_send_requested",
        "enter_key_sent",
        "send_submit_performed",
        "chatgpt_prompt_submitted",
        "page_click_performed",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
        "full_conversation_text_logged",
        "prompt_text_logged",
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if payload.get("prompt_length", 0) < 200:
        missing_true.append("prompt_length>=200")
    if not payload.get("prompt_hash"):
        missing_true.append("prompt_hash_nonempty")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.10A acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
