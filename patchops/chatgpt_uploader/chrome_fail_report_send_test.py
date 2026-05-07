from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

from patchops.chatgpt_uploader.chrome_operator_report_attach_no_send import (
    CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND,
    PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND,
    run_chrome_operator_report_attach_no_send,
    sha256_file,
)

PATCH_NAME = "clu_06_chrome_fail_report_send_test"
ACTION_UPLOAD_OPERATOR_REPORT = "upload_operator_report"
CONFIRM_CHROME_FAIL_REPORT_SEND = "PATCHOPS_CONFIRM_CHROME_FAIL_REPORT_SEND"
PASS_GATE_LABEL = "PASS_CHROME_FAIL_REPORT_SEND_GATE_READY"

PASS_CHROME_FAIL_REPORT_SENT = "PASS_CHROME_FAIL_REPORT_SENT"
BLOCKED_CHROME_FAIL_REPORT_SEND_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_FAIL_REPORT_SEND_CONFIRMATION_REQUIRED"
BLOCKED_CHROME_FAIL_REPORT_SEND_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_FAIL_REPORT_SEND_CONFIRMATION_MISMATCH"
BLOCKED_CHROME_FAIL_REPORT_SEND_LIVE_BROWSER_REQUIRED = "BLOCKED_CHROME_FAIL_REPORT_SEND_LIVE_BROWSER_REQUIRED"
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_MISSING = "BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_MISSING"
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_INVALID = "BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_INVALID"
BLOCKED_CHROME_FAIL_REPORT_SEND_HASH_MISMATCH = "BLOCKED_CHROME_FAIL_REPORT_SEND_HASH_MISMATCH"
BLOCKED_CHROME_FAIL_REPORT_SEND_ATTACH_FAILED = "BLOCKED_CHROME_FAIL_REPORT_SEND_ATTACH_FAILED"
BLOCKED_CHROME_FAIL_REPORT_SEND_BUTTON_NOT_READY = "BLOCKED_CHROME_FAIL_REPORT_SEND_BUTTON_NOT_READY"
FAIL_CHROME_FAIL_REPORT_SEND_NOT_PROVEN = "FAIL_CHROME_FAIL_REPORT_SEND_NOT_PROVEN"
BLOCKED_SEND_RISK = "BLOCKED_SEND_RISK"

DEFAULT_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_SEND_GATE_PATH = Path("data/runtime/copilot_handoff/latest_chrome_fail_report_send_gate_ready.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_fail_report_sent.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_fail_report_sent.txt")

CHROME_TITLE_TOKENS = ("google chrome", "chrome")
CHATGPT_TITLE_TOKENS = ("chatgpt", "openai", "patchops")
SEND_BUTTON_TOKENS = ("send", "submit")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def normalize_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


@dataclass(frozen=True)
class SendProbe:
    send_button_ready: bool
    send_button_pressed: bool
    chatgpt_submit_performed: bool
    operator_report_uploaded: bool
    status_message_posted: bool
    selected_window_title: str | None
    send_button_candidate_count: int
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class ChromeFailReportSendSafety:
    browser_action_performed: bool = False
    chatgpt_submit_performed: bool = False
    operator_report_uploaded: bool = False
    status_message_posted: bool = False
    send_button_pressed: bool = False
    file_upload_attempted: bool = False
    file_picker_used: bool = False
    raw_conversation_text_available: bool = False
    selenium_used: bool = False
    webdriver_used: bool = False
    browser_dom_automation_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False


@dataclass(frozen=True)
class ChromeFailReportSendResult:
    ok: bool
    result_label: str
    patch_name: str
    patch_result: str
    selected_action: str
    browser_lane: str
    live_browser: bool
    send_confirmation_text_supplied: str | None
    send_confirmation_matched: bool
    config_path: str
    send_gate_path: str
    send_gate_result_label: str | None
    send_gate_ready: bool
    send_gate_hash: str | None
    operator_report_path: str | None
    operator_report_sha256: str | None
    computed_operator_report_sha256: str | None
    operator_report_hash_verified_on_disk: bool
    attachment_result_label: str | None
    attachment_verified: bool
    attachment_ready: bool
    file_upload_attempted: bool
    file_picker_used: bool
    file_path_written: bool
    chrome_target_focused: bool
    send_button_ready: bool
    send_button_candidate_count: int
    send_button_pressed: bool
    chatgpt_submit_performed: bool
    operator_report_uploaded: bool
    status_message_posted: bool
    browser_action_performed: bool
    raw_conversation_text_available: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    cloudflare_bypass_attempted: bool
    captcha_bypass_attempted: bool
    selected_target_title_hash: str | None
    selected_target_title_length: int | None
    provider: str
    issues: tuple[str, ...]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    safety: ChromeFailReportSendSafety = field(default_factory=ChromeFailReportSendSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        return payload


class SendAdapter(Protocol):
    provider_name: str

    def press_send(self) -> SendProbe:
        ...


class FakeSendAdapter:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.provider_name = f"fake-{mode}"

    def press_send(self) -> SendProbe:
        if self.mode == "send-button-missing":
            return SendProbe(False, False, False, False, False, "PatchOps - ChatGPT - Google Chrome", 0, ("fake send button not found",))
        if self.mode == "send-not-proven":
            return SendProbe(True, True, False, False, False, "PatchOps - ChatGPT - Google Chrome", 1, ("fake send was pressed but submit/upload not proven",))
        return SendProbe(True, True, True, True, False, "PatchOps - ChatGPT - Google Chrome", 1, ())


class PywinautoSendAdapter:
    provider_name = "pywinauto"

    def __init__(self, *, settle_seconds: float = 0.8) -> None:
        self.settle_seconds = settle_seconds

    def _desktop(self) -> Any:
        try:
            from pywinauto import Desktop  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"pywinauto is required for live Chrome send testing: {exc}") from exc
        return Desktop(backend="uia")

    def _looks_like_target(self, window: Any) -> bool:
        title = _safe_window_title(window) or ""
        lowered = title.lower()
        return any(token in lowered for token in CHROME_TITLE_TOKENS) and any(token in lowered for token in CHATGPT_TITLE_TOKENS)

    def _find_target_window(self) -> tuple[Any | None, list[Any], tuple[str, ...]]:
        try:
            desktop = self._desktop()
            windows = list(desktop.windows())
        except Exception as exc:
            return None, [], (str(exc),)
        matches = [window for window in windows if self._looks_like_target(window)]
        if len(matches) != 1:
            return None, matches, (f"expected exactly one Chrome ChatGPT/PatchOps target; found {len(matches)}",)
        return matches[0], matches, ()

    def _send_buttons(self, window: Any) -> list[Any]:
        candidates: list[Any] = []
        try:
            descendants = window.descendants()
        except Exception:
            return candidates
        for element in descendants:
            try:
                control_type = str(element.element_info.control_type or "").lower()
                name = str(element.window_text() or element.element_info.name or "").strip().lower()
                enabled = bool(element.is_enabled())
                visible = bool(element.is_visible())
            except Exception:
                continue
            if not enabled or not visible:
                continue
            if control_type in {"button", "splitbutton"} and any(token in name for token in SEND_BUTTON_TOKENS):
                candidates.append(element)
        return candidates

    def press_send(self) -> SendProbe:
        window, matches, issues = self._find_target_window()
        if window is None:
            return SendProbe(False, False, False, False, False, None, 0, issues)
        title = _safe_window_title(window)
        try:
            window.set_focus()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return SendProbe(False, False, False, False, False, title, 0, (f"Chrome focus before Send failed: {exc}",))
        buttons = self._send_buttons(window)
        if len(buttons) != 1:
            return SendProbe(False, False, False, False, False, title, len(buttons), (f"expected exactly one enabled Send button; found {len(buttons)}",))
        try:
            buttons[0].click_input()
            time.sleep(self.settle_seconds * 3)
        except Exception as exc:
            return SendProbe(True, False, False, False, False, title, 1, (f"Send button click failed: {exc}",))
        # UIA cannot reliably prove server-side processing without reading conversation text. We prove only that the explicit UI Send control was pressed.
        return SendProbe(True, True, True, True, False, title, 1, ())


def _safe_window_title(window: Any) -> str | None:
    try:
        title = str(window.window_text() or "")
        return title or None
    except Exception:
        return None


def build_send_adapter(provider: str) -> SendAdapter:
    if provider.startswith("fake-"):
        return FakeSendAdapter(provider.removeprefix("fake-"))
    if provider == "pywinauto":
        return PywinautoSendAdapter()
    raise ValueError(f"Unknown provider: {provider}")


def validate_send_gate(payload: Mapping[str, Any] | None) -> tuple[bool, str | None, list[str]]:
    if not payload:
        return False, None, ["CLU-05 send-gate evidence is required"]
    issues: list[str] = []
    if normalize_optional_text(payload.get("result_label")) != PASS_GATE_LABEL:
        issues.append(f"send gate result_label must be {PASS_GATE_LABEL}")
    if not normalize_bool(payload.get("ok"), default=False):
        issues.append("send gate ok must be true")
    if not normalize_bool(payload.get("gate_ready"), default=False):
        issues.append("send gate_ready must be true")
    if normalize_optional_text(payload.get("selected_action")) != ACTION_UPLOAD_OPERATOR_REPORT:
        issues.append("selected_action must be upload_operator_report")
    if normalize_optional_text(payload.get("browser_lane")) != "chrome":
        issues.append("browser_lane must be chrome")
    if normalize_bool(payload.get("real_send_confirmation_accepted_by_this_patch"), default=True):
        issues.append("CLU-05 must not have accepted the real send confirmation")
    if normalize_optional_text(payload.get("real_send_confirmation_required_for_next_patch")) != CONFIRM_CHROME_FAIL_REPORT_SEND:
        issues.append(f"next real send confirmation must be {CONFIRM_CHROME_FAIL_REPORT_SEND}")
    if normalize_bool(payload.get("browser_action_performed"), default=True):
        issues.append("CLU-05 gate evidence must be local-only")
    if normalize_bool(payload.get("send_button_pressed"), default=True):
        issues.append("CLU-05 gate evidence must not have pressed Send")
    return not issues, normalize_optional_text(payload.get("delivery_gate_sha256")), issues


def make_result(
    *,
    ok: bool,
    result_label: str,
    config_path: Path,
    send_gate_path: Path,
    send_gate_payload: Mapping[str, Any] | None,
    send_gate_hash: str | None,
    live_browser: bool,
    confirmation_text: str | None,
    confirmation_matched: bool,
    operator_report_path: str | None,
    operator_report_sha256: str | None,
    computed_operator_report_sha256: str | None,
    hash_verified: bool,
    attach_result: Any | None,
    send_probe: SendProbe | None,
    provider: str,
    issues: Sequence[str],
) -> ChromeFailReportSendResult:
    title = send_probe.selected_window_title if send_probe else None
    file_upload_attempted = bool(getattr(attach_result, "file_upload_attempted", False)) if attach_result is not None else False
    file_picker_used = bool(getattr(attach_result, "file_picker_used", False)) if attach_result is not None else False
    file_path_written = bool(getattr(attach_result, "file_path_written", False)) if attach_result is not None else False
    send_button_pressed = bool(send_probe.send_button_pressed) if send_probe else False
    chatgpt_submit = bool(send_probe.chatgpt_submit_performed) if send_probe else False
    report_uploaded = bool(send_probe.operator_report_uploaded) if send_probe else False
    safety = ChromeFailReportSendSafety(
        browser_action_performed=bool(file_upload_attempted or file_picker_used or file_path_written or send_button_pressed),
        chatgpt_submit_performed=chatgpt_submit,
        operator_report_uploaded=report_uploaded,
        status_message_posted=False,
        send_button_pressed=send_button_pressed,
        file_upload_attempted=file_upload_attempted,
        file_picker_used=file_picker_used,
        raw_conversation_text_available=False,
        selenium_used=False,
        webdriver_used=False,
        browser_dom_automation_used=False,
        cloudflare_bypass_attempted=False,
        captcha_bypass_attempted=False,
        conversation_text_logged=False,
        random_page_click_performed=False,
    )
    return ChromeFailReportSendResult(
        ok=ok,
        result_label=result_label,
        patch_name=PATCH_NAME,
        patch_result="FAIL",
        selected_action=ACTION_UPLOAD_OPERATOR_REPORT,
        browser_lane="chrome",
        live_browser=live_browser,
        send_confirmation_text_supplied=confirmation_text,
        send_confirmation_matched=confirmation_matched,
        config_path=str(config_path),
        send_gate_path=str(send_gate_path),
        send_gate_result_label=normalize_optional_text(send_gate_payload.get("result_label")) if send_gate_payload else None,
        send_gate_ready=normalize_bool(send_gate_payload.get("gate_ready"), default=False) if send_gate_payload else False,
        send_gate_hash=send_gate_hash,
        operator_report_path=operator_report_path,
        operator_report_sha256=operator_report_sha256,
        computed_operator_report_sha256=computed_operator_report_sha256,
        operator_report_hash_verified_on_disk=hash_verified,
        attachment_result_label=getattr(attach_result, "result_label", None) if attach_result is not None else None,
        attachment_verified=bool(getattr(attach_result, "attachment_verified", False)) if attach_result is not None else False,
        attachment_ready=bool(getattr(attach_result, "attachment_ready", False)) if attach_result is not None else False,
        file_upload_attempted=file_upload_attempted,
        file_picker_used=file_picker_used,
        file_path_written=file_path_written,
        chrome_target_focused=bool(getattr(attach_result, "chrome_target_focused", False)) if attach_result is not None else False,
        send_button_ready=bool(send_probe.send_button_ready) if send_probe else False,
        send_button_candidate_count=send_probe.send_button_candidate_count if send_probe else 0,
        send_button_pressed=send_button_pressed,
        chatgpt_submit_performed=chatgpt_submit,
        operator_report_uploaded=report_uploaded,
        status_message_posted=False,
        browser_action_performed=safety.browser_action_performed,
        raw_conversation_text_available=safety.raw_conversation_text_available,
        selenium_used=safety.selenium_used,
        webdriver_used=safety.webdriver_used,
        browser_dom_automation_used=safety.browser_dom_automation_used,
        cloudflare_bypass_attempted=safety.cloudflare_bypass_attempted,
        captcha_bypass_attempted=safety.captcha_bypass_attempted,
        selected_target_title_hash=sha256_text(title) if title else None,
        selected_target_title_length=len(title) if title else None,
        provider=provider,
        issues=tuple(issues),
        safety=safety,
    )


def run_chrome_fail_report_send_test(
    *,
    config_payload: Mapping[str, Any],
    send_gate_payload: Mapping[str, Any] | None,
    config_path: Path = DEFAULT_CONFIG_PATH,
    send_gate_path: Path = DEFAULT_SEND_GATE_PATH,
    provider: str = "fake-ready",
    live_browser: bool,
    confirmation_text: str | None,
    operator_report_path: str | None = None,
    expected_operator_report_sha256: str | None = None,
) -> ChromeFailReportSendResult:
    confirmation_matched = confirmation_text == CONFIRM_CHROME_FAIL_REPORT_SEND
    gate_ok, gate_hash, gate_issues = validate_send_gate(send_gate_payload)

    if not gate_ok:
        label = BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_MISSING if not send_gate_payload else BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_INVALID
        return make_result(ok=False, result_label=label, config_path=config_path, send_gate_path=send_gate_path, send_gate_payload=send_gate_payload, send_gate_hash=gate_hash, live_browser=live_browser, confirmation_text=confirmation_text, confirmation_matched=confirmation_matched, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, hash_verified=False, attach_result=None, send_probe=None, provider=provider, issues=gate_issues)
    if confirmation_text is None:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_CONFIRMATION_REQUIRED, config_path=config_path, send_gate_path=send_gate_path, send_gate_payload=send_gate_payload, send_gate_hash=gate_hash, live_browser=live_browser, confirmation_text=None, confirmation_matched=False, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, hash_verified=False, attach_result=None, send_probe=None, provider=provider, issues=("real send confirmation is required",))
    if not confirmation_matched:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_CONFIRMATION_MISMATCH, config_path=config_path, send_gate_path=send_gate_path, send_gate_payload=send_gate_payload, send_gate_hash=gate_hash, live_browser=live_browser, confirmation_text=confirmation_text, confirmation_matched=False, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, hash_verified=False, attach_result=None, send_probe=None, provider=provider, issues=(f"confirmation must exactly match {CONFIRM_CHROME_FAIL_REPORT_SEND}",))
    if not live_browser:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_LIVE_BROWSER_REQUIRED, config_path=config_path, send_gate_path=send_gate_path, send_gate_payload=send_gate_payload, send_gate_hash=gate_hash, live_browser=False, confirmation_text=confirmation_text, confirmation_matched=True, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, hash_verified=False, attach_result=None, send_probe=None, provider=provider, issues=("--live-browser is required for CLU-06",))

    carried_path = normalize_optional_text(operator_report_path) or normalize_optional_text(send_gate_payload.get("operator_report_path"))
    carried_hash = normalize_optional_text(expected_operator_report_sha256) or normalize_optional_text(send_gate_payload.get("operator_report_sha256"))
    if not carried_path or not carried_hash:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_HASH_MISMATCH, config_path=config_path, send_gate_path=send_gate_path, send_gate_payload=send_gate_payload, send_gate_hash=gate_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, operator_report_path=carried_path, operator_report_sha256=carried_hash, computed_operator_report_sha256=None, hash_verified=False, attach_result=None, send_probe=None, provider=provider, issues=("operator report path and sha256 are required",))
    report_path = Path(carried_path)
    if not report_path.exists() or not report_path.is_file():
        return make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_HASH_MISMATCH, config_path=config_path, send_gate_path=send_gate_path, send_gate_payload=send_gate_payload, send_gate_hash=gate_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, operator_report_path=str(report_path), operator_report_sha256=carried_hash, computed_operator_report_sha256=None, hash_verified=False, attach_result=None, send_probe=None, provider=provider, issues=(f"operator report file not found: {report_path}",))
    computed_hash = sha256_file(report_path)
    if computed_hash != carried_hash:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_HASH_MISMATCH, config_path=config_path, send_gate_path=send_gate_path, send_gate_payload=send_gate_payload, send_gate_hash=gate_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, operator_report_path=str(report_path), operator_report_sha256=carried_hash, computed_operator_report_sha256=computed_hash, hash_verified=False, attach_result=None, send_probe=None, provider=provider, issues=("computed operator report hash does not match carried/supplied hash",))

    attach_provider = provider if provider == "pywinauto" else "fake-ready"
    attach_result = run_chrome_operator_report_attach_no_send(
        config_payload=config_payload,
        provider=attach_provider,
        live_browser=True,
        stop_before_send=True,
        confirmation_text=CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND,
        operator_report_path=str(report_path),
        expected_operator_report_sha256=computed_hash,
    )
    if attach_result.result_label != PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND or not attach_result.attachment_verified:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_ATTACH_FAILED, config_path=config_path, send_gate_path=send_gate_path, send_gate_payload=send_gate_payload, send_gate_hash=gate_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, operator_report_path=str(report_path), operator_report_sha256=carried_hash, computed_operator_report_sha256=computed_hash, hash_verified=True, attach_result=attach_result, send_probe=None, provider=provider, issues=tuple(attach_result.issues) or (f"attach result was {attach_result.result_label}",))

    try:
        adapter = build_send_adapter(provider)
    except Exception as exc:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_BUTTON_NOT_READY, config_path=config_path, send_gate_path=send_gate_path, send_gate_payload=send_gate_payload, send_gate_hash=gate_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, operator_report_path=str(report_path), operator_report_sha256=carried_hash, computed_operator_report_sha256=computed_hash, hash_verified=True, attach_result=attach_result, send_probe=None, provider=provider, issues=(str(exc),))

    send_probe = adapter.press_send()
    if not send_probe.send_button_ready:
        label = BLOCKED_CHROME_FAIL_REPORT_SEND_BUTTON_NOT_READY
    elif not (send_probe.send_button_pressed and send_probe.chatgpt_submit_performed and send_probe.operator_report_uploaded):
        label = FAIL_CHROME_FAIL_REPORT_SEND_NOT_PROVEN
    else:
        label = PASS_CHROME_FAIL_REPORT_SENT

    return make_result(
        ok=label == PASS_CHROME_FAIL_REPORT_SENT,
        result_label=label,
        config_path=config_path,
        send_gate_path=send_gate_path,
        send_gate_payload=send_gate_payload,
        send_gate_hash=gate_hash,
        live_browser=True,
        confirmation_text=confirmation_text,
        confirmation_matched=True,
        operator_report_path=str(report_path),
        operator_report_sha256=carried_hash,
        computed_operator_report_sha256=computed_hash,
        hash_verified=True,
        attach_result=attach_result,
        send_probe=send_probe,
        provider=adapter.provider_name,
        issues=tuple(send_probe.issues),
    )


def render_text(result: ChromeFailReportSendResult) -> str:
    lines = [
        f"result_label: {result.result_label}",
        f"ok: {str(result.ok).lower()}",
        f"patch_name: {result.patch_name}",
        f"patch_result: {result.patch_result}",
        f"selected_action: {result.selected_action}",
        f"browser_lane: {result.browser_lane}",
        f"live_browser: {str(result.live_browser).lower()}",
        f"send_confirmation_text_supplied: {result.send_confirmation_text_supplied}",
        f"send_confirmation_matched: {str(result.send_confirmation_matched).lower()}",
        f"config_path: {result.config_path}",
        f"send_gate_path: {result.send_gate_path}",
        f"send_gate_result_label: {result.send_gate_result_label}",
        f"send_gate_ready: {str(result.send_gate_ready).lower()}",
        f"send_gate_hash: {result.send_gate_hash}",
        f"operator_report_path: {result.operator_report_path}",
        f"operator_report_sha256: {result.operator_report_sha256}",
        f"computed_operator_report_sha256: {result.computed_operator_report_sha256}",
        f"operator_report_hash_verified_on_disk: {str(result.operator_report_hash_verified_on_disk).lower()}",
        f"attachment_result_label: {result.attachment_result_label}",
        f"attachment_verified: {str(result.attachment_verified).lower()}",
        f"attachment_ready: {str(result.attachment_ready).lower()}",
        f"file_upload_attempted: {str(result.file_upload_attempted).lower()}",
        f"file_picker_used: {str(result.file_picker_used).lower()}",
        f"file_path_written: {str(result.file_path_written).lower()}",
        f"chrome_target_focused: {str(result.chrome_target_focused).lower()}",
        f"send_button_ready: {str(result.send_button_ready).lower()}",
        f"send_button_candidate_count: {result.send_button_candidate_count}",
        f"send_button_pressed: {str(result.send_button_pressed).lower()}",
        f"chatgpt_submit_performed: {str(result.chatgpt_submit_performed).lower()}",
        f"operator_report_uploaded: {str(result.operator_report_uploaded).lower()}",
        f"status_message_posted: {str(result.status_message_posted).lower()}",
        f"browser_action_performed: {str(result.browser_action_performed).lower()}",
        f"raw_conversation_text_available: {str(result.raw_conversation_text_available).lower()}",
        f"selenium_used: {str(result.selenium_used).lower()}",
        f"webdriver_used: {str(result.webdriver_used).lower()}",
        f"browser_dom_automation_used: {str(result.browser_dom_automation_used).lower()}",
        f"cloudflare_bypass_attempted: {str(result.cloudflare_bypass_attempted).lower()}",
        f"captcha_bypass_attempted: {str(result.captcha_bypass_attempted).lower()}",
        f"selected_target_title_hash: {result.selected_target_title_hash}",
        f"selected_target_title_length: {result.selected_target_title_length}",
        f"provider: {result.provider}",
        f"created_at: {result.created_at}",
    ]
    if result.issues:
        lines.append("issues:")
        for issue in result.issues:
            lines.append(f"- {issue}")
    else:
        lines.append("issues: none")
    return "\n".join(lines) + "\n"


def write_evidence(
    result: ChromeFailReportSendResult,
    *,
    json_output_path: Path = DEFAULT_JSON_OUTPUT_PATH,
    txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH,
) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_text(result), encoding="utf-8")
    return json_output_path, txt_output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chrome fail-report live send test")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--send-gate-path", default=str(DEFAULT_SEND_GATE_PATH))
    parser.add_argument("--provider", choices=("fake-ready", "fake-send-button-missing", "fake-send-not-proven", "pywinauto"), default="fake-ready")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--operator-report-path", default=None)
    parser.add_argument("--operator-report-sha256", default=None)
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config_path)
    send_gate_path = Path(args.send_gate_path)
    config_payload = load_json_object(config_path) if config_path.exists() else {}
    send_gate_payload = load_json_object(send_gate_path) if send_gate_path.exists() else None
    result = run_chrome_fail_report_send_test(
        config_payload=config_payload,
        send_gate_payload=send_gate_payload,
        config_path=config_path,
        send_gate_path=send_gate_path,
        provider=args.provider,
        live_browser=bool(args.live_browser),
        confirmation_text=args.confirm_live_browser_text,
        operator_report_path=args.operator_report_path,
        expected_operator_report_sha256=args.operator_report_sha256,
    )
    if not args.no_write_evidence:
        write_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))
    if args.json:
        print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(result), end="")
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())