from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence
from urllib.parse import urlparse

PATCH_NAME = "clu_02_chrome_file_picker_ready_no_attach"
CONFIRM_CHROME_FILE_PICKER_READY_NO_ATTACH = "PATCHOPS_CONFIRM_CHROME_FILE_PICKER_READY_NO_ATTACH"

PASS_CHROME_FILE_PICKER_READY_NO_ATTACH = "PASS_CHROME_FILE_PICKER_READY_NO_ATTACH"
BLOCKED_CHROME_FILE_PICKER_CONFIG_MISSING = "BLOCKED_CHROME_FILE_PICKER_CONFIG_MISSING"
BLOCKED_CHROME_FILE_PICKER_BROWSER_MISMATCH = "BLOCKED_CHROME_FILE_PICKER_BROWSER_MISMATCH"
BLOCKED_CHROME_FILE_PICKER_URL_INVALID = "BLOCKED_CHROME_FILE_PICKER_URL_INVALID"
BLOCKED_CHROME_FILE_PICKER_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_FILE_PICKER_CONFIRMATION_REQUIRED"
BLOCKED_CHROME_FILE_PICKER_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_FILE_PICKER_CONFIRMATION_MISMATCH"
BLOCKED_CHROME_FILE_PICKER_TARGET_NOT_READY = "BLOCKED_CHROME_FILE_PICKER_TARGET_NOT_READY"
BLOCKED_CHROME_FILE_PICKER_AMBIGUOUS_TARGET = "BLOCKED_CHROME_FILE_PICKER_AMBIGUOUS_TARGET"
BLOCKED_CHROME_FILE_PICKER_ATTACHMENT_CONTROL_NOT_FOUND = "BLOCKED_CHROME_FILE_PICKER_ATTACHMENT_CONTROL_NOT_FOUND"
BLOCKED_CHROME_FILE_PICKER_NOT_FOUND = "BLOCKED_CHROME_FILE_PICKER_NOT_FOUND"
BLOCKED_CHROME_FILE_PICKER_PATH_EDIT_NOT_FOUND = "BLOCKED_CHROME_FILE_PICKER_PATH_EDIT_NOT_FOUND"
BLOCKED_CHROME_FILE_PICKER_CANCEL_NOT_PROVEN = "BLOCKED_CHROME_FILE_PICKER_CANCEL_NOT_PROVEN"
BLOCKED_SEND_RISK = "BLOCKED_SEND_RISK"

DEFAULT_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_file_picker_ready_no_attach.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_file_picker_ready_no_attach.txt")

CHROME_TITLE_TOKENS = ("google chrome", "chrome")
CHATGPT_TITLE_TOKENS = ("chatgpt", "openai", "patchops")
ATTACH_BUTTON_NAME_TOKENS = ("attach", "upload", "add files", "add photos", "paperclip")
FILE_DIALOG_TITLE_TOKENS = ("open", "upload", "choose file", "file upload")
CANCEL_BUTTON_NAME_TOKENS = ("cancel", "close")


@dataclass(frozen=True)
class ChromeFilePickerSafety:
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
class ChromeFilePickerReadyNoAttachResult:
    ok: bool
    result_label: str
    patch_name: str
    selected_action: str
    browser_lane: str | None
    status_chat_configured: bool
    status_chat_url_hash_or_redacted: str | None
    target_url_sha256: str | None
    live_browser: bool
    confirmation_text_supplied: str | None
    confirmation_matched: bool
    chrome_target_ready: bool
    chrome_target_focused: bool
    attachment_control_found: bool
    attachment_candidate_count: int
    target_window_count: int
    matching_target_count: int
    selected_target_title_hash: str | None
    selected_target_title_length: int | None
    attachment_trigger_attempted: bool
    file_picker_used: bool
    file_picker_opened: bool
    file_path_edit_found: bool
    picker_cancelled: bool
    send_risk_detected: bool
    browser_action_performed: bool
    file_upload_attempted: bool
    operator_report_uploaded: bool
    chatgpt_submit_performed: bool
    status_message_posted: bool
    send_button_pressed: bool
    raw_conversation_text_available: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    cloudflare_bypass_attempted: bool
    captcha_bypass_attempted: bool
    provider: str
    issues: tuple[str, ...]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    safety: ChromeFilePickerSafety = field(default_factory=ChromeFilePickerSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        return payload


@dataclass(frozen=True)
class StatusTargetConfig:
    enabled: bool
    browser_lane: str | None
    target_url: str | None
    target_url_sha256: str | None


@dataclass(frozen=True)
class ChromeTargetProbe:
    ready: bool
    focused: bool
    target_window_count: int
    matching_target_count: int
    selected_target_title: str | None
    attachment_candidate_count: int
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class FilePickerProbe:
    attachment_trigger_attempted: bool
    file_picker_opened: bool
    file_path_edit_found: bool
    picker_cancelled: bool
    send_risk_detected: bool
    issues: tuple[str, ...] = ()


class ChromeFilePickerAdapter(Protocol):
    provider_name: str

    def focus_target(self, target: StatusTargetConfig) -> ChromeTargetProbe:
        ...

    def open_picker_and_cancel(self) -> FilePickerProbe:
        ...


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


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
    if text in {"1", "true", "yes", "y", "on", "enabled", "configured"}:
        return True
    if text in {"0", "false", "no", "n", "off", "disabled"}:
        return False
    return default


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def valid_chatgpt_status_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
    except Exception:
        return False
    host = parsed.netloc.lower()
    path = parsed.path or ""
    if parsed.scheme != "https":
        return False
    if host not in {"chatgpt.com", "www.chatgpt.com"}:
        return False
    return bool(re.search(r"(^|/)c/[A-Za-z0-9_-]+", path))


def redact_url(value: str | None) -> str | None:
    if not value:
        return None
    return f"sha256:{sha256_text(value)}"


def extract_status_target(payload: Mapping[str, Any]) -> StatusTargetConfig:
    status_chat = payload.get("status_chat")
    source: Mapping[str, Any]
    if isinstance(status_chat, Mapping):
        source = status_chat
    else:
        source = payload
    enabled = normalize_bool(source.get("enabled"), default=normalize_bool(source.get("status_chat_configured"), default=False))
    lane = normalize_optional_text(source.get("browser_lane"))
    if lane:
        lane = lane.lower()
    target_url = normalize_optional_text(source.get("target_url")) or normalize_optional_text(source.get("status_chat_url"))
    target_url_sha256 = normalize_optional_text(source.get("target_url_sha256")) or normalize_optional_text(source.get("status_chat_url_hash_or_redacted"))
    if target_url_sha256 and target_url_sha256.startswith("sha256:"):
        target_url_sha256 = target_url_sha256.removeprefix("sha256:")
    return StatusTargetConfig(enabled=enabled, browser_lane=lane, target_url=target_url, target_url_sha256=target_url_sha256)


class FakeChromeFilePickerAdapter:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.provider_name = f"fake-{mode}"
        self.focused = False

    def focus_target(self, target: StatusTargetConfig) -> ChromeTargetProbe:
        if self.mode == "no-target":
            return ChromeTargetProbe(False, False, 0, 0, None, 0, ("no fake Chrome ChatGPT target",))
        if self.mode == "ambiguous-target":
            return ChromeTargetProbe(False, False, 2, 2, None, 0, ("multiple fake Chrome ChatGPT targets",))
        if self.mode == "no-attachment-control":
            self.focused = True
            return ChromeTargetProbe(False, True, 1, 1, "PatchOps - ChatGPT - Google Chrome", 0, ("no fake attachment control",))
        self.focused = True
        return ChromeTargetProbe(True, True, 1, 1, "PatchOps - ChatGPT - Google Chrome", 1, ())

    def open_picker_and_cancel(self) -> FilePickerProbe:
        if not self.focused:
            return FilePickerProbe(False, False, False, False, True, ("target not focused before picker open",))
        if self.mode == "send-risk":
            return FilePickerProbe(False, False, False, False, True, ("fake send risk before picker",))
        if self.mode == "no-dialog":
            return FilePickerProbe(True, False, False, False, False, ("fake file picker did not open",))
        if self.mode == "no-path-edit":
            return FilePickerProbe(True, True, False, True, False, ("fake file picker path edit not found",))
        if self.mode == "cancel-fails":
            return FilePickerProbe(True, True, True, False, False, ("fake file picker cancel not proven",))
        return FilePickerProbe(True, True, True, True, False, ())


class PywinautoChromeFilePickerAdapter:
    provider_name = "pywinauto"

    def __init__(self, *, settle_seconds: float = 0.5) -> None:
        self.settle_seconds = settle_seconds
        self._selected_window: Any | None = None

    def _desktop(self) -> Any:
        try:
            from pywinauto import Desktop  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"pywinauto is required for live Chrome file picker probing: {exc}") from exc
        return Desktop(backend="uia")

    def _looks_like_chrome_chatgpt_window(self, window: Any) -> bool:
        title = _safe_window_title(window) or ""
        lowered = title.lower()
        return any(token in lowered for token in CHROME_TITLE_TOKENS) and any(token in lowered for token in CHATGPT_TITLE_TOKENS)

    def focus_target(self, target: StatusTargetConfig) -> ChromeTargetProbe:
        try:
            desktop = self._desktop()
            windows = list(desktop.windows())
        except Exception as exc:
            return ChromeTargetProbe(False, False, 0, 0, None, 0, (str(exc),))
        matches = [window for window in windows if self._looks_like_chrome_chatgpt_window(window)]
        if not matches:
            return ChromeTargetProbe(False, False, len(windows), 0, None, 0, ("no visible Chrome ChatGPT/PatchOps target window",))
        if len(matches) > 1:
            return ChromeTargetProbe(False, False, len(windows), len(matches), None, 0, ("multiple Chrome ChatGPT/PatchOps target windows",))
        selected = matches[0]
        try:
            selected.set_focus()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return ChromeTargetProbe(False, False, len(windows), 1, _safe_window_title(selected), 0, (f"Chrome focus failed: {exc}",))
        self._selected_window = selected
        candidates = self._find_attachment_controls(selected)
        if not candidates:
            return ChromeTargetProbe(False, True, len(windows), 1, _safe_window_title(selected), 0, ("no safe Chrome attachment control candidate",))
        if len(candidates) > 1:
            return ChromeTargetProbe(False, True, len(windows), 1, _safe_window_title(selected), len(candidates), ("multiple Chrome attachment control candidates",))
        return ChromeTargetProbe(True, True, len(windows), 1, _safe_window_title(selected), len(candidates), ())

    def _find_attachment_controls(self, window: Any) -> list[Any]:
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
            if control_type in {"button", "splitbutton", "menuitem"} and any(token in name for token in ATTACH_BUTTON_NAME_TOKENS):
                candidates.append(element)
        return candidates

    def _find_file_dialog(self) -> Any | None:
        try:
            desktop = self._desktop()
            windows = list(desktop.windows())
        except Exception:
            return None
        for window in windows:
            title = (_safe_window_title(window) or "").lower()
            if any(token in title for token in FILE_DIALOG_TITLE_TOKENS):
                return window
        return None

    def _find_path_edit(self, dialog: Any) -> Any | None:
        try:
            descendants = dialog.descendants()
        except Exception:
            return None
        edits = []
        for element in descendants:
            try:
                control_type = str(element.element_info.control_type or "").lower()
                enabled = bool(element.is_enabled())
                visible = bool(element.is_visible())
            except Exception:
                continue
            if enabled and visible and control_type == "edit":
                edits.append(element)
        return edits[-1] if edits else None

    def _find_cancel_button(self, dialog: Any) -> Any | None:
        try:
            descendants = dialog.descendants()
        except Exception:
            return None
        for element in descendants:
            try:
                control_type = str(element.element_info.control_type or "").lower()
                name = str(element.window_text() or element.element_info.name or "").strip().lower()
                enabled = bool(element.is_enabled())
                visible = bool(element.is_visible())
            except Exception:
                continue
            if enabled and visible and control_type == "button" and any(token == name or token in name for token in CANCEL_BUTTON_NAME_TOKENS):
                return element
        return None

    def open_picker_and_cancel(self) -> FilePickerProbe:
        if self._selected_window is None:
            return FilePickerProbe(False, False, False, False, True, ("Chrome target was not focused first",))
        buttons = self._find_attachment_controls(self._selected_window)
        if not buttons:
            return FilePickerProbe(False, False, False, False, False, ("no safe Chrome attachment control candidate",))
        if len(buttons) > 1:
            return FilePickerProbe(False, False, False, False, True, ("multiple Chrome attachment controls; refusing to choose",))
        try:
            buttons[0].click_input()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return FilePickerProbe(True, False, False, False, False, (f"Chrome attachment control click failed: {exc}",))
        dialog = self._find_file_dialog()
        if dialog is None:
            return FilePickerProbe(True, False, False, False, False, ("Chrome file picker did not appear",))
        edit = self._find_path_edit(dialog)
        edit_found = edit is not None
        try:
            cancel = self._find_cancel_button(dialog)
            if cancel is not None:
                cancel.click_input()
            else:
                try:
                    from pywinauto.keyboard import send_keys  # type: ignore
                except Exception as exc:  # pragma: no cover
                    raise RuntimeError(f"pywinauto keyboard helper unavailable: {exc}") from exc
                dialog.set_focus()
                send_keys("{ESC}", pause=0.05)
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return FilePickerProbe(True, True, edit_found, False, False, (f"Chrome file picker cancel failed: {exc}",))
        cancelled = self._find_file_dialog() is None
        if not cancelled:
            return FilePickerProbe(True, True, edit_found, False, False, ("Chrome file picker still appears open after cancel",))
        return FilePickerProbe(True, True, edit_found, True, False, ())


def _safe_window_title(window: Any) -> str | None:
    try:
        title = str(window.window_text() or "")
        return title or None
    except Exception:
        return None


def build_adapter(provider: str) -> ChromeFilePickerAdapter:
    if provider.startswith("fake-"):
        return FakeChromeFilePickerAdapter(provider.removeprefix("fake-"))
    if provider == "pywinauto":
        return PywinautoChromeFilePickerAdapter()
    raise ValueError(f"Unknown provider: {provider}")


def make_result(
    *,
    ok: bool,
    result_label: str,
    selected_action: str,
    target: StatusTargetConfig,
    live_browser: bool,
    confirmation_text_supplied: str | None,
    confirmation_matched: bool,
    target_probe: ChromeTargetProbe | None,
    picker_probe: FilePickerProbe | None,
    provider: str,
    issues: Sequence[str],
) -> ChromeFilePickerReadyNoAttachResult:
    focused = bool(target_probe.focused) if target_probe else False
    trigger_attempted = bool(picker_probe.attachment_trigger_attempted) if picker_probe else False
    picker_opened = bool(picker_probe.file_picker_opened) if picker_probe else False
    safety = ChromeFilePickerSafety(
        browser_action_performed=bool(focused or trigger_attempted or picker_opened),
        chatgpt_submit_performed=False,
        operator_report_uploaded=False,
        status_message_posted=False,
        send_button_pressed=False,
        file_upload_attempted=False,
        file_picker_used=picker_opened,
        raw_conversation_text_available=False,
        selenium_used=False,
        webdriver_used=False,
        browser_dom_automation_used=False,
        cloudflare_bypass_attempted=False,
        captcha_bypass_attempted=False,
        conversation_text_logged=False,
        random_page_click_performed=False,
    )
    title = target_probe.selected_target_title if target_probe else None
    return ChromeFilePickerReadyNoAttachResult(
        ok=ok,
        result_label=result_label,
        patch_name=PATCH_NAME,
        selected_action=selected_action,
        browser_lane=target.browser_lane,
        status_chat_configured=target.enabled,
        status_chat_url_hash_or_redacted=redact_url(target.target_url) or (f"sha256:{target.target_url_sha256}" if target.target_url_sha256 else None),
        target_url_sha256=target.target_url_sha256 or (sha256_text(target.target_url) if target.target_url else None),
        live_browser=live_browser,
        confirmation_text_supplied=confirmation_text_supplied,
        confirmation_matched=confirmation_matched,
        chrome_target_ready=bool(target_probe.ready) if target_probe else False,
        chrome_target_focused=focused,
        attachment_control_found=bool(target_probe.attachment_candidate_count > 0) if target_probe else False,
        attachment_candidate_count=target_probe.attachment_candidate_count if target_probe else 0,
        target_window_count=target_probe.target_window_count if target_probe else 0,
        matching_target_count=target_probe.matching_target_count if target_probe else 0,
        selected_target_title_hash=sha256_text(title) if title else None,
        selected_target_title_length=len(title) if title else None,
        attachment_trigger_attempted=trigger_attempted,
        file_picker_used=safety.file_picker_used,
        file_picker_opened=picker_opened,
        file_path_edit_found=bool(picker_probe.file_path_edit_found) if picker_probe else False,
        picker_cancelled=bool(picker_probe.picker_cancelled) if picker_probe else False,
        send_risk_detected=bool(picker_probe.send_risk_detected) if picker_probe else False,
        browser_action_performed=safety.browser_action_performed,
        file_upload_attempted=safety.file_upload_attempted,
        operator_report_uploaded=safety.operator_report_uploaded,
        chatgpt_submit_performed=safety.chatgpt_submit_performed,
        status_message_posted=safety.status_message_posted,
        send_button_pressed=safety.send_button_pressed,
        raw_conversation_text_available=safety.raw_conversation_text_available,
        selenium_used=safety.selenium_used,
        webdriver_used=safety.webdriver_used,
        browser_dom_automation_used=safety.browser_dom_automation_used,
        cloudflare_bypass_attempted=safety.cloudflare_bypass_attempted,
        captcha_bypass_attempted=safety.captcha_bypass_attempted,
        provider=provider,
        issues=tuple(issues),
        safety=safety,
    )


def run_chrome_file_picker_ready_no_attach(
    *,
    config_payload: Mapping[str, Any],
    provider: str,
    live_browser: bool,
    confirmation_text: str | None,
) -> ChromeFilePickerReadyNoAttachResult:
    selected_action = "upload_operator_report"
    target = extract_status_target(config_payload)
    confirmation_matched = confirmation_text == CONFIRM_CHROME_FILE_PICKER_READY_NO_ATTACH

    if not target.enabled:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FILE_PICKER_CONFIG_MISSING, selected_action=selected_action, target=target, live_browser=live_browser, confirmation_text_supplied=confirmation_text, confirmation_matched=confirmation_matched, target_probe=None, picker_probe=None, provider=provider, issues=("status_chat.enabled must be true",))
    if target.browser_lane != "chrome":
        return make_result(ok=False, result_label=BLOCKED_CHROME_FILE_PICKER_BROWSER_MISMATCH, selected_action=selected_action, target=target, live_browser=live_browser, confirmation_text_supplied=confirmation_text, confirmation_matched=confirmation_matched, target_probe=None, picker_probe=None, provider=provider, issues=("browser_lane must be chrome",))
    if not target.target_url and not target.target_url_sha256:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FILE_PICKER_URL_INVALID, selected_action=selected_action, target=target, live_browser=live_browser, confirmation_text_supplied=confirmation_text, confirmation_matched=confirmation_matched, target_probe=None, picker_probe=None, provider=provider, issues=("target_url or target_url_sha256 is required",))
    if target.target_url and not valid_chatgpt_status_url(target.target_url):
        return make_result(ok=False, result_label=BLOCKED_CHROME_FILE_PICKER_URL_INVALID, selected_action=selected_action, target=target, live_browser=live_browser, confirmation_text_supplied=confirmation_text, confirmation_matched=confirmation_matched, target_probe=None, picker_probe=None, provider=provider, issues=("target_url must be an https chatgpt.com conversation URL containing /c/<id>",))
    if target.target_url and target.target_url_sha256 and target.target_url_sha256 != sha256_text(target.target_url):
        return make_result(ok=False, result_label=BLOCKED_CHROME_FILE_PICKER_URL_INVALID, selected_action=selected_action, target=target, live_browser=live_browser, confirmation_text_supplied=confirmation_text, confirmation_matched=confirmation_matched, target_probe=None, picker_probe=None, provider=provider, issues=("target_url_sha256 does not match target_url",))
    if not live_browser:
        return make_result(ok=False, result_label=BLOCKED_SEND_RISK, selected_action=selected_action, target=target, live_browser=False, confirmation_text_supplied=confirmation_text, confirmation_matched=confirmation_matched, target_probe=None, picker_probe=None, provider=provider, issues=("--live-browser is required for Chrome file picker probing",))
    if confirmation_text is None:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FILE_PICKER_CONFIRMATION_REQUIRED, selected_action=selected_action, target=target, live_browser=True, confirmation_text_supplied=None, confirmation_matched=False, target_probe=None, picker_probe=None, provider=provider, issues=("confirmation text is required",))
    if not confirmation_matched:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FILE_PICKER_CONFIRMATION_MISMATCH, selected_action=selected_action, target=target, live_browser=True, confirmation_text_supplied=confirmation_text, confirmation_matched=False, target_probe=None, picker_probe=None, provider=provider, issues=(f"confirmation must exactly match {CONFIRM_CHROME_FILE_PICKER_READY_NO_ATTACH}",))

    try:
        adapter = build_adapter(provider)
    except Exception as exc:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FILE_PICKER_TARGET_NOT_READY, selected_action=selected_action, target=target, live_browser=True, confirmation_text_supplied=confirmation_text, confirmation_matched=True, target_probe=None, picker_probe=None, provider=provider, issues=(str(exc),))

    target_probe = adapter.focus_target(target)
    if target_probe.matching_target_count > 1:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FILE_PICKER_AMBIGUOUS_TARGET, selected_action=selected_action, target=target, live_browser=True, confirmation_text_supplied=confirmation_text, confirmation_matched=True, target_probe=target_probe, picker_probe=None, provider=adapter.provider_name, issues=target_probe.issues)
    if target_probe.focused and target_probe.attachment_candidate_count < 1:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FILE_PICKER_ATTACHMENT_CONTROL_NOT_FOUND, selected_action=selected_action, target=target, live_browser=True, confirmation_text_supplied=confirmation_text, confirmation_matched=True, target_probe=target_probe, picker_probe=None, provider=adapter.provider_name, issues=target_probe.issues)
    if not target_probe.ready or not target_probe.focused:
        return make_result(ok=False, result_label=BLOCKED_CHROME_FILE_PICKER_TARGET_NOT_READY, selected_action=selected_action, target=target, live_browser=True, confirmation_text_supplied=confirmation_text, confirmation_matched=True, target_probe=target_probe, picker_probe=None, provider=adapter.provider_name, issues=target_probe.issues)

    picker_probe = adapter.open_picker_and_cancel()
    if picker_probe.send_risk_detected:
        label = BLOCKED_SEND_RISK
    elif not picker_probe.file_picker_opened:
        label = BLOCKED_CHROME_FILE_PICKER_NOT_FOUND
    elif not picker_probe.file_path_edit_found:
        label = BLOCKED_CHROME_FILE_PICKER_PATH_EDIT_NOT_FOUND
    elif not picker_probe.picker_cancelled:
        label = BLOCKED_CHROME_FILE_PICKER_CANCEL_NOT_PROVEN
    else:
        label = PASS_CHROME_FILE_PICKER_READY_NO_ATTACH

    return make_result(
        ok=label == PASS_CHROME_FILE_PICKER_READY_NO_ATTACH,
        result_label=label,
        selected_action=selected_action,
        target=target,
        live_browser=True,
        confirmation_text_supplied=confirmation_text,
        confirmation_matched=True,
        target_probe=target_probe,
        picker_probe=picker_probe,
        provider=adapter.provider_name,
        issues=tuple(target_probe.issues + picker_probe.issues),
    )


def render_text(result: ChromeFilePickerReadyNoAttachResult) -> str:
    lines = [
        f"result_label: {result.result_label}",
        f"ok: {str(result.ok).lower()}",
        f"patch_name: {result.patch_name}",
        f"selected_action: {result.selected_action}",
        f"browser_lane: {result.browser_lane}",
        f"status_chat_configured: {str(result.status_chat_configured).lower()}",
        f"status_chat_url_hash_or_redacted: {result.status_chat_url_hash_or_redacted}",
        f"target_url_sha256: {result.target_url_sha256}",
        f"live_browser: {str(result.live_browser).lower()}",
        f"confirmation_text_supplied: {result.confirmation_text_supplied}",
        f"confirmation_matched: {str(result.confirmation_matched).lower()}",
        f"chrome_target_ready: {str(result.chrome_target_ready).lower()}",
        f"chrome_target_focused: {str(result.chrome_target_focused).lower()}",
        f"attachment_control_found: {str(result.attachment_control_found).lower()}",
        f"attachment_candidate_count: {result.attachment_candidate_count}",
        f"target_window_count: {result.target_window_count}",
        f"matching_target_count: {result.matching_target_count}",
        f"selected_target_title_hash: {result.selected_target_title_hash}",
        f"selected_target_title_length: {result.selected_target_title_length}",
        f"attachment_trigger_attempted: {str(result.attachment_trigger_attempted).lower()}",
        f"file_picker_used: {str(result.file_picker_used).lower()}",
        f"file_picker_opened: {str(result.file_picker_opened).lower()}",
        f"file_path_edit_found: {str(result.file_path_edit_found).lower()}",
        f"picker_cancelled: {str(result.picker_cancelled).lower()}",
        f"send_risk_detected: {str(result.send_risk_detected).lower()}",
        f"browser_action_performed: {str(result.browser_action_performed).lower()}",
        f"file_upload_attempted: {str(result.file_upload_attempted).lower()}",
        f"operator_report_uploaded: {str(result.operator_report_uploaded).lower()}",
        f"chatgpt_submit_performed: {str(result.chatgpt_submit_performed).lower()}",
        f"status_message_posted: {str(result.status_message_posted).lower()}",
        f"send_button_pressed: {str(result.send_button_pressed).lower()}",
        f"raw_conversation_text_available: {str(result.raw_conversation_text_available).lower()}",
        f"selenium_used: {str(result.selenium_used).lower()}",
        f"webdriver_used: {str(result.webdriver_used).lower()}",
        f"browser_dom_automation_used: {str(result.browser_dom_automation_used).lower()}",
        f"cloudflare_bypass_attempted: {str(result.cloudflare_bypass_attempted).lower()}",
        f"captcha_bypass_attempted: {str(result.captcha_bypass_attempted).lower()}",
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
    result: ChromeFilePickerReadyNoAttachResult,
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
    parser = argparse.ArgumentParser(description="Chrome file picker ready no-attach probe")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-ambiguous-target", "fake-no-attachment-control", "fake-no-dialog", "fake-no-path-edit", "fake-cancel-fails", "fake-send-risk", "pywinauto"), default="fake-ready")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config_path)
    payload = load_json_object(config_path) if config_path.exists() else {}
    result = run_chrome_file_picker_ready_no_attach(
        config_payload=payload,
        provider=args.provider,
        live_browser=bool(args.live_browser),
        confirmation_text=args.confirm_live_browser_text,
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