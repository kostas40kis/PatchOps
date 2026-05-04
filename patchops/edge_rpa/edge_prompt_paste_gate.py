from __future__ import annotations

import hashlib
import json
import sys
import textwrap
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pywinauto import keyboard  # type: ignore

from patchops.edge_rpa.edge_composer_dry_run_text_gate import _find_focused_composer_control, _get_clipboard_text, _set_clipboard_text
from patchops.edge_rpa.edge_composer_focus_probe import run_l26_07_focus_probe

PATCH_NAME = "l26_09_chatgpt_prompt_builder_paste_gate"


@dataclass(frozen=True)
class PromptPasteGateResult:
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
    prompt_built: bool = False
    prompt_hash_recorded: bool = False
    prompt_hash: str = ""
    prompt_length: int = 0
    allow_paste_gate_enabled: bool = False
    clipboard_backup_captured: bool = False
    clipboard_backup_hash: str = ""
    clipboard_prompt_set: bool = False
    prompt_pasted: bool = False
    prompt_observed_by_copyback: bool = False
    copyback_hash_matches_prompt: bool = False
    copyback_length: int = 0
    prompt_preview_logged: bool = False
    prompt_text_logged: bool = False
    prompt_cleared: bool = False
    clipboard_restored: bool = False
    prompt_report_path: str = ""
    focus_json_path: str = ""
    enter_key_sent: bool = False
    send_submit_performed: bool = False
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


def build_l26_09_prompt() -> str:
    return textwrap.dedent(
        """
        You are continuing the PatchOps normal Microsoft Edge pywinauto/UIA browser-runner stream.

        Current accepted frontier:
        - L26.7 accepted: focused the real in-page ChatGPT composer (`prompt-textarea`, `ProseMirror`) without text, clicks, send, downloads, run-package, WebDriver, or DOM automation.
        - L26.8 accepted: pasted one harmless dry-run marker into the focused composer, verified it by copyback, cleared it, restored the clipboard, and kept Enter/send/click/download/run-package false.

        Write the next narrow PatchOps direct-manifest PowerShell patch for L26.10.

        Required L26.10 scope:
        - Build the first gated prompt-send proof, but keep it disabled by default unless an explicit --allow-send gate is present.
        - Reuse the accepted focus/paste gates.
        - Record prompt hash and length only; do not log the full prompt or conversation text.
        - If --allow-send is absent, prove that the prompt can be built/pasted/cleared without sending.
        - If --allow-send is present in a later operator-controlled proof, send only a safe bounded prompt and record send timestamp/hash.

        Forbidden unless the phase explicitly enables it:
        - CAPTCHA/Cloudflare bypass.
        - Selenium/WebDriver or browser DOM automation.
        - unbounded clicking.
        - downloads.
        - archive extraction.
        - PatchOps run-package.
        - git commit or git push.
        - reading or logging full conversation text.

        Use PatchOps to patch PatchOps. Keep PowerShell thin and put reusable logic in Python. Include py_compile, focused pytest, and a real normal Edge live proof.
        """
    ).strip() + "\n"


def _write_report(path: Path, result: PromptPasteGateResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.9 ChatGPT prompt-builder paste gate",
        "prompt_preview_logged:false",
        "prompt_text_logged:false",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "enter_key_sent:false",
        "send_submit_performed:false",
        "chatgpt_prompt_submitted:false",
        "page_click_performed:false",
        "download_click_performed:false",
        "run_package_invoked:false",
        "Only prompt hashes and lengths are reported.",
        "",
        f"classification: {result.classification}",
        f"chatgpt_accessible: {result.chatgpt_accessible}",
        f"composer_focus_verified: {result.composer_focus_verified}",
        f"prompt_built: {result.prompt_built}",
        f"prompt_hash: {result.prompt_hash}",
        f"prompt_length: {result.prompt_length}",
        f"allow_paste_gate_enabled: {result.allow_paste_gate_enabled}",
        f"clipboard_prompt_set: {result.clipboard_prompt_set}",
        f"prompt_pasted: {result.prompt_pasted}",
        f"prompt_observed_by_copyback: {result.prompt_observed_by_copyback}",
        f"copyback_hash_matches_prompt: {result.copyback_hash_matches_prompt}",
        f"copyback_length: {result.copyback_length}",
        f"prompt_cleared: {result.prompt_cleared}",
        f"clipboard_restored: {result.clipboard_restored}",
        f"failure_layer: {result.failure_layer}",
        f"error: {result.error}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: PromptPasteGateResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_09_prompt_paste_gate(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 8.0, allow_paste: bool = False) -> PromptPasteGateResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_09_prompt_paste_gate_result.json"
    report_path = out_dir / "normal_edge_l26_09_prompt_paste_gate_report.txt"
    focus_dir = out_dir / "focus_probe"
    focus_json = focus_dir / "normal_edge_l26_07_composer_focus_result.json"

    prompt = build_l26_09_prompt()
    prompt_hash = _hash_text(prompt)
    prompt_len = len(prompt)
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

        if not allow_paste:
            raise RuntimeError("L26.9 requires explicit --allow-paste for the live paste proof.")
        if not (sequence_completed and accessible and focus_completed and focus_verified and candidate_not_chrome and candidate_page_scope):
            raise RuntimeError(f"L26.9 requires L26.7 focus PASS first; classification={classification!r} focus_verified={focus_verified}.")

        clipboard_backup = _get_clipboard_text()
        backup_captured = True
        backup_hash = _hash_text(clipboard_backup)

        _find_focused_composer_control()
        keyboard.send_keys("^a")
        time.sleep(0.1)
        keyboard.send_keys("{BACKSPACE}")
        time.sleep(0.2)
        _set_clipboard_text(prompt)
        prompt_set = _get_clipboard_text() == prompt
        if not prompt_set:
            raise RuntimeError("Prompt was not set on clipboard.")

        keyboard.send_keys("^v")
        pasted = True
        time.sleep(0.5)
        keyboard.send_keys("^a")
        time.sleep(0.1)
        keyboard.send_keys("^c")
        time.sleep(0.2)
        copied = _get_clipboard_text()
        copied_hash = _hash_text(copied)
        observed = copied == prompt
        hash_match = copied_hash == prompt_hash

        keyboard.send_keys("{BACKSPACE}")
        time.sleep(0.3)
        sentinel = "PATCHOPS_L26_09_EMPTY_SELECTION_SENTINEL"
        _set_clipboard_text(sentinel)
        keyboard.send_keys("^a")
        time.sleep(0.1)
        keyboard.send_keys("^c")
        time.sleep(0.2)
        copied_after_clear = _get_clipboard_text()
        cleared = copied_after_clear == sentinel or copied_after_clear != prompt

        _set_clipboard_text(clipboard_backup)
        clipboard_restored = True

        result_pass = bool(observed and hash_match and cleared)
        failure_layer = ""
        error = ""
        if not observed or not hash_match:
            failure_layer = "prompt_paste_copyback"
            error = "Prompt was pasted but copyback did not exactly match prompt hash."
        elif not cleared:
            failure_layer = "prompt_clear"
            error = "Prompt was observed but not proven cleared. Manually clear composer before continuing."

        result = PromptPasteGateResult(
            targeted_sequence_completed=sequence_completed,
            classification=classification,
            chatgpt_accessible=accessible,
            focus_probe_completed=focus_completed,
            composer_focus_verified=focus_verified,
            candidate_not_browser_chrome=candidate_not_chrome,
            candidate_in_page_scope=candidate_page_scope,
            prompt_built=True,
            prompt_hash_recorded=True,
            prompt_hash=prompt_hash,
            prompt_length=prompt_len,
            allow_paste_gate_enabled=allow_paste,
            clipboard_backup_captured=backup_captured,
            clipboard_backup_hash=backup_hash,
            clipboard_prompt_set=prompt_set,
            prompt_pasted=pasted,
            prompt_observed_by_copyback=observed,
            copyback_hash_matches_prompt=hash_match,
            copyback_length=len(copied),
            prompt_cleared=cleared,
            clipboard_restored=clipboard_restored,
            prompt_report_path=str(report_path),
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
        result = PromptPasteGateResult(
            prompt_built=True,
            prompt_hash_recorded=True,
            prompt_hash=prompt_hash,
            prompt_length=prompt_len,
            allow_paste_gate_enabled=allow_paste,
            clipboard_restored=clipboard_restored,
            prompt_report_path=str(report_path),
            focus_json_path=str(focus_json),
            result="FAIL",
            failure_layer="prompt_paste_gate",
            error=f"{type(exc).__name__}: {exc}",
        )

    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_09_acceptance(result: PromptPasteGateResult) -> None:
    payload = result.to_payload()
    required_true = [
        "targeted_sequence_completed",
        "chatgpt_accessible",
        "focus_probe_completed",
        "composer_focus_verified",
        "candidate_not_browser_chrome",
        "candidate_in_page_scope",
        "prompt_built",
        "prompt_hash_recorded",
        "allow_paste_gate_enabled",
        "clipboard_backup_captured",
        "clipboard_prompt_set",
        "prompt_pasted",
        "prompt_observed_by_copyback",
        "copyback_hash_matches_prompt",
        "prompt_cleared",
        "clipboard_restored",
    ]
    required_false = [
        "prompt_preview_logged",
        "prompt_text_logged",
        "enter_key_sent",
        "send_submit_performed",
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
    if payload.get("prompt_length", 0) < 200:
        missing_true.append("prompt_length>=200")
    if not payload.get("prompt_hash"):
        missing_true.append("prompt_hash_nonempty")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.9 acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
