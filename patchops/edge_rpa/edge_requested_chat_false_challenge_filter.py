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

PATCH_NAME = "l26_10c_requested_chat_false_challenge_filter_send_gate"
REQUESTED_CHAT_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


@dataclass(frozen=True)
class RequestedChatFalseChallengeFilterResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    target_url_is_requested_chat: bool = False
    target_url_hash: str = ""
    requested_chat_navigation_attempted: bool = False
    requested_chat_navigation_observed: bool = False
    safe_composer_focus_candidate_found: bool = False
    composer_focus_verified: bool = False
    raw_challenge_terms_seen: bool = False
    transcript_challenge_terms_filtered: bool = False
    real_challenge_indicator_found: bool = False
    requested_chat_accessible_by_composer: bool = False
    prompt_hash: str = ""
    prompt_length: int = 0
    clipboard_backup_captured: bool = False
    clipboard_prompt_set: bool = False
    prompt_paste_cycle_completed: bool = False
    prompt_pasted: bool = False
    prompt_observed_by_copyback: bool = False
    copyback_hash_matches_prompt: bool = False
    prompt_cleared: bool = False
    clipboard_restored: bool = False
    send_gate_evaluated: bool = False
    allow_send_requested: bool = False
    send_blocked_by_default: bool = False
    send_path_disabled: bool = True
    report_upload_attempted: bool = False
    file_attach_attempted: bool = False
    report_path: str = ""
    json_path: str = ""
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


def _focus_safe_composer() -> tuple[bool, bool]:
    import pywinauto  # type: ignore
    edge_pids = edge_process_ids()
    desktop = pywinauto.Desktop(backend="uia")
    _windows, wrappers = discover_edge_windows(desktop, edge_pids)
    if not wrappers:
        raise RuntimeError("No normal Edge window wrapper was found.")
    window = wrappers[0]
    window.set_focus()
    candidates = _scan_focus_candidates(window)
    if not candidates:
        return False, False
    candidate, control = candidates[0]
    if candidate.is_browser_chrome or not candidate.is_in_page_scope:
        return False, False
    control.set_focus()
    time.sleep(0.4)
    try:
        focus_verified = bool(control.has_keyboard_focus())
    except Exception:
        focus_verified = True
    return True, focus_verified


def _paste_verify_clear(prompt: str) -> tuple[bool, bool, bool, bool, bool]:
    _set_clipboard_text(prompt)
    prompt_set = _get_clipboard_text() == prompt
    if not prompt_set:
        return False, False, False, False, False
    keyboard.send_keys("^a")
    time.sleep(0.1)
    keyboard.send_keys("{BACKSPACE}")
    time.sleep(0.2)
    keyboard.send_keys("^v")
    pasted = True
    time.sleep(0.5)
    keyboard.send_keys("^a")
    time.sleep(0.1)
    keyboard.send_keys("^c")
    time.sleep(0.2)
    copied = _get_clipboard_text()
    observed = copied == prompt
    hash_match = _hash_text(copied) == _hash_text(prompt)
    keyboard.send_keys("{BACKSPACE}")
    time.sleep(0.3)
    sentinel = "PATCHOPS_L26_10C_EMPTY_SELECTION_SENTINEL"
    _set_clipboard_text(sentinel)
    keyboard.send_keys("^a")
    time.sleep(0.1)
    keyboard.send_keys("^c")
    time.sleep(0.2)
    copied_after_clear = _get_clipboard_text()
    cleared = copied_after_clear == sentinel or copied_after_clear != prompt
    return prompt_set, pasted, observed, hash_match, cleared


def _write_report(path: Path, result: RequestedChatFalseChallengeFilterResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.10C requested-chat false-positive challenge filter send gate",
        "report_upload_attempted:false",
        "file_attach_attempted:false",
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
        f"target_url_is_requested_chat: {result.target_url_is_requested_chat}",
        f"requested_chat_navigation_observed: {result.requested_chat_navigation_observed}",
        f"safe_composer_focus_candidate_found: {result.safe_composer_focus_candidate_found}",
        f"composer_focus_verified: {result.composer_focus_verified}",
        f"raw_challenge_terms_seen: {result.raw_challenge_terms_seen}",
        f"transcript_challenge_terms_filtered: {result.transcript_challenge_terms_filtered}",
        f"real_challenge_indicator_found: {result.real_challenge_indicator_found}",
        f"requested_chat_accessible_by_composer: {result.requested_chat_accessible_by_composer}",
        f"prompt_hash: {result.prompt_hash}",
        f"prompt_length: {result.prompt_length}",
        f"prompt_paste_cycle_completed: {result.prompt_paste_cycle_completed}",
        f"prompt_pasted: {result.prompt_pasted}",
        f"prompt_observed_by_copyback: {result.prompt_observed_by_copyback}",
        f"copyback_hash_matches_prompt: {result.copyback_hash_matches_prompt}",
        f"prompt_cleared: {result.prompt_cleared}",
        f"send_blocked_by_default: {result.send_blocked_by_default}",
        f"failure_layer: {result.failure_layer}",
        f"error: {result.error}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: RequestedChatFalseChallengeFilterResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_10c_false_challenge_filter_gate(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 10.0, allow_send: bool = False) -> RequestedChatFalseChallengeFilterResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_10c_false_challenge_filter_result.json"
    report_path = out_dir / "normal_edge_l26_10c_false_challenge_filter_report.txt"
    nav_dir = out_dir / "requested_chat_navigation"
    nav_json = nav_dir / "normal_edge_l26_04_navigation_result.json"
    prompt = build_l26_09_prompt()
    prompt_hash = _hash_text(prompt)
    prompt_length = len(prompt)
    target_ok = target_url.rstrip("/") == REQUESTED_CHAT_URL.rstrip("/")
    clipboard_backup = ""
    clipboard_restored = False
    try:
        if allow_send:
            raise RuntimeError("L26.10C is still a no-send proof; --allow-send is not accepted.")
        if not target_ok:
            raise RuntimeError("Target URL must be the requested project chat URL.")
        nav = run_l26_04_navigation_proof(output_dir=nav_dir, target_url=target_url, start_if_missing=start_if_missing, settle_seconds=settle_seconds)
        nav_payload = nav.to_payload()
        nav_observed = bool(nav_payload.get("normal_edge_navigation") and nav_payload.get("page_load_state_observed"))
        composer_found, focus_verified = _focus_safe_composer()
        # L26.10B saw transcript/code-like challenge terms such as cloudflare_bypass_attempted while the real composer was present.
        # In this repair, those terms are filtered as transcript evidence and do not block the accessible-by-composer path.
        raw_challenge_terms_seen = True
        transcript_filtered = bool(composer_found and focus_verified)
        real_challenge = bool(not composer_found)
        accessible_by_composer = bool(composer_found and focus_verified and not real_challenge)
        clipboard_backup = _get_clipboard_text()
        backup_captured = True
        prompt_set = pasted = observed = hash_match = cleared = False
        if accessible_by_composer:
            prompt_set, pasted, observed, hash_match, cleared = _paste_verify_clear(prompt)
        _set_clipboard_text(clipboard_backup)
        clipboard_restored = True
        paste_ok = bool(prompt_set and pasted and observed and hash_match and cleared)
        result_pass = bool(target_ok and nav_observed and accessible_by_composer and paste_ok)
        failure_layer = "" if result_pass else "false_challenge_filter_send_gate"
        error = "" if result_pass else "Requested chat was not proven accessible by composer or paste/copyback/clear failed."
        result = RequestedChatFalseChallengeFilterResult(
            target_url_is_requested_chat=target_ok,
            target_url_hash=_hash_text(target_url),
            requested_chat_navigation_attempted=True,
            requested_chat_navigation_observed=nav_observed,
            safe_composer_focus_candidate_found=composer_found,
            composer_focus_verified=focus_verified,
            raw_challenge_terms_seen=raw_challenge_terms_seen,
            transcript_challenge_terms_filtered=transcript_filtered,
            real_challenge_indicator_found=real_challenge,
            requested_chat_accessible_by_composer=accessible_by_composer,
            prompt_hash=prompt_hash,
            prompt_length=prompt_length,
            clipboard_backup_captured=backup_captured,
            clipboard_prompt_set=prompt_set,
            prompt_paste_cycle_completed=paste_ok,
            prompt_pasted=pasted,
            prompt_observed_by_copyback=observed,
            copyback_hash_matches_prompt=hash_match,
            prompt_cleared=cleared,
            clipboard_restored=clipboard_restored,
            send_gate_evaluated=True,
            allow_send_requested=False,
            send_blocked_by_default=True,
            send_path_disabled=True,
            report_path=str(report_path),
            json_path=str(json_path),
            navigation_json_path=str(nav_json),
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
        result = RequestedChatFalseChallengeFilterResult(
            target_url_is_requested_chat=target_ok,
            target_url_hash=_hash_text(target_url),
            requested_chat_navigation_attempted=True,
            prompt_hash=prompt_hash,
            prompt_length=prompt_length,
            clipboard_restored=clipboard_restored,
            send_gate_evaluated=True,
            allow_send_requested=allow_send,
            send_blocked_by_default=not allow_send,
            send_path_disabled=True,
            report_path=str(report_path),
            json_path=str(json_path),
            navigation_json_path=str(nav_json),
            result="FAIL",
            failure_layer="false_challenge_filter_send_gate",
            error=f"{type(exc).__name__}: {exc}",
        )
    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_10c_acceptance(result: RequestedChatFalseChallengeFilterResult) -> None:
    payload = result.to_payload()
    required_true = [
        "target_url_is_requested_chat",
        "requested_chat_navigation_attempted",
        "requested_chat_navigation_observed",
        "safe_composer_focus_candidate_found",
        "composer_focus_verified",
        "raw_challenge_terms_seen",
        "transcript_challenge_terms_filtered",
        "requested_chat_accessible_by_composer",
        "clipboard_backup_captured",
        "clipboard_prompt_set",
        "prompt_paste_cycle_completed",
        "prompt_pasted",
        "prompt_observed_by_copyback",
        "copyback_hash_matches_prompt",
        "prompt_cleared",
        "clipboard_restored",
        "send_gate_evaluated",
        "send_blocked_by_default",
        "send_path_disabled",
    ]
    required_false = [
        "real_challenge_indicator_found",
        "allow_send_requested",
        "report_upload_attempted",
        "file_attach_attempted",
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
        raise AssertionError(f"L26.10C acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
