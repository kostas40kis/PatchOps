from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence
from urllib.parse import urlparse

PATCH_NAME = "clu_03_chrome_operator_report_attach_no_send_probe"
CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND = "PATCHOPS_CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND"
ACTION_UPLOAD_OPERATOR_REPORT = "upload_operator_report"

PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND = "PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND"
BLOCKED_OPERATOR_REPORT_MISSING = "BLOCKED_OPERATOR_REPORT_MISSING"
BLOCKED_OPERATOR_REPORT_HASH_MISMATCH = "BLOCKED_OPERATOR_REPORT_HASH_MISMATCH"
BLOCKED_CHROME_ATTACH_CONFIG_MISSING = "BLOCKED_CHROME_ATTACH_CONFIG_MISSING"
BLOCKED_CHROME_ATTACH_BROWSER_MISMATCH = "BLOCKED_CHROME_ATTACH_BROWSER_MISMATCH"
BLOCKED_CHROME_ATTACH_URL_INVALID = "BLOCKED_CHROME_ATTACH_URL_INVALID"
BLOCKED_CHROME_ATTACH_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_ATTACH_CONFIRMATION_REQUIRED"
BLOCKED_CHROME_ATTACH_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_ATTACH_CONFIRMATION_MISMATCH"
BLOCKED_CHROME_TARGET_NOT_READY = "BLOCKED_CHROME_TARGET_NOT_READY"
BLOCKED_CHROME_AMBIGUOUS_TARGET = "BLOCKED_CHROME_AMBIGUOUS_TARGET"
BLOCKED_CHROME_ATTACHMENT_CONTROL_NOT_FOUND = "BLOCKED_CHROME_ATTACHMENT_CONTROL_NOT_FOUND"
BLOCKED_CHROME_FILE_PICKER_NOT_READY = "BLOCKED_CHROME_FILE_PICKER_NOT_READY"
BLOCKED_ATTACHMENT_NOT_VERIFIED = "BLOCKED_ATTACHMENT_NOT_VERIFIED"
BLOCKED_SEND_RISK = "BLOCKED_SEND_RISK"

DEFAULT_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_operator_report_attached_no_send.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_operator_report_attached_no_send.txt")

CHROME_TITLE_TOKENS = ("google chrome", "chrome")
CHATGPT_TITLE_TOKENS = ("chatgpt", "openai", "patchops")
ATTACH_BUTTON_NAME_TOKENS = ("attach", "upload", "add files", "add photos", "paperclip")
FILE_DIALOG_TITLE_TOKENS = ("open", "upload", "choose file", "file upload")
ATTACHMENT_READY_TOKENS = ("uploaded", "attached", "file", "remove attachment", "remove file")


@dataclass(frozen=True)
class ChromeReportAttachSafety:
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
class ChromeOperatorReportAttachNoSendResult:
    ok: bool
    result_label: str
    patch_name: str
    patch_result: str
    selected_action: str
    browser_lane: str | None
    status_chat_configured: bool
    status_chat_url_hash_or_redacted: str | None
    target_url_sha256: str | None
    live_browser: bool
    stop_before_send: bool
    confirmation_text_supplied: str | None
    confirmation_matched: bool
    operator_report_path: str | None
    operator_report_sha256: str | None
    computed_operator_report_sha256: str | None
    operator_report_size_bytes: int | None
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
    file_path_written: bool
    attachment_ready: bool
    attachment_verified: bool
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
    safety: ChromeReportAttachSafety = field(default_factory=ChromeReportAttachSafety)

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
class AttachmentProbe:
    attachment_trigger_attempted: bool
    file_picker_opened: bool
    file_path_written: bool
    attachment_ready: bool
    attachment_verified: bool
    send_risk_detected: bool
    issues: tuple[str, ...] = ()


class ChromeReportAttachAdapter(Protocol):
    provider_name: str

    def focus_target(self, target: StatusTargetConfig) -> ChromeTargetProbe:
        ...

    def attach_report_no_send(self, report_path: Path) -> AttachmentProbe:
        ...


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


class FakeChromeReportAttachAdapter:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.provider_name = f"fake-{mode}"
        self.focused = False
        self.attached_path: str | None = None

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

    def attach_report_no_send(self, report_path: Path) -> AttachmentProbe:
        if not self.focused:
            return AttachmentProbe(False, False, False, False, False, True, ("target not focused before attachment",))
        if self.mode == "send-risk":
            return AttachmentProbe(False, False, False, False, False, True, ("fake send risk before attachment",))
        if self.mode == "no-dialog":
            return AttachmentProbe(True, False, False, False, False, False, ("fake file picker did not open",))
        if self.mode == "path-write-fails":
            return AttachmentProbe(True, True, False, False, False, False, ("fake file picker path write failed",))
        if self.mode == "attachment-not-ready":
            self.attached_path = str(report_path)
            return AttachmentProbe(True, True, True, False, False, False, ("fake attachment readiness not detected",))
        if self.mode == "attachment-not-verified":
            self.attached_path = str(report_path)
            return AttachmentProbe(True, True, True, True, False, False, ("fake attachment not verified",))
        self.attached_path = str(report_path)
        return AttachmentProbe(True, True, True, True, True, False, ())


class PywinautoChromeReportAttachAdapter:
    provider_name = "pywinauto"

    def __init__(self, *, settle_seconds: float = 0.7) -> None:
        self.settle_seconds = settle_seconds
        self._selected_window: Any | None = None

    def _desktop(self) -> Any:
        try:
            from pywinauto import Desktop  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"pywinauto is required for live Chrome report attachment probing: {exc}") from exc
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

    def _find_open_button(self, dialog: Any) -> Any | None:
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
            if enabled and visible and control_type == "button" and name in {"open", "&open", "choose", "upload"}:
                return element
        return None

    def _attachment_ready(self, expected_name: str) -> bool:
        if self._selected_window is None:
            return False
        expected_lower = expected_name.lower()
        expected_stem = Path(expected_name).stem.lower()
        try:
            descendants = self._selected_window.descendants()
        except Exception:
            return False
        for element in descendants:
            try:
                text = str(element.window_text() or element.element_info.name or "").strip().lower()
                enabled = bool(element.is_enabled())
                visible = bool(element.is_visible())
            except Exception:
                continue
            if not enabled or not visible:
                continue
            if expected_lower and expected_lower in text:
                return True
            if expected_stem and expected_stem in text and any(token in text for token in ATTACHMENT_READY_TOKENS):
                return True
        return False

    def attach_report_no_send(self, report_path: Path) -> AttachmentProbe:
        if self._selected_window is None:
            return AttachmentProbe(False, False, False, False, False, True, ("Chrome target was not focused first",))
        buttons = self._find_attachment_controls(self._selected_window)
        if not buttons:
            return AttachmentProbe(False, False, False, False, False, False, ("no safe Chrome attachment control candidate",))
        if len(buttons) > 1:
            return AttachmentProbe(False, False, False, False, False, True, ("multiple Chrome attachment controls; refusing to choose",))
        try:
            buttons[0].click_input()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return AttachmentProbe(True, False, False, False, False, False, (f"Chrome attachment control click failed: {exc}",))
        dialog = self._find_file_dialog()
        if dialog is None:
            return AttachmentProbe(True, False, False, False, False, False, ("Chrome file picker did not appear",))
        edit = self._find_path_edit(dialog)
        if edit is None:
            return AttachmentProbe(True, True, False, False, False, False, ("Chrome file picker filename/path edit not found",))
        try:
            edit.set_focus()
            _set_windows_clipboard_text(str(report_path))
            try:
                from pywinauto.keyboard import send_keys  # type: ignore
            except Exception as exc:  # pragma: no cover
                raise RuntimeError(f"pywinauto keyboard helper unavailable: {exc}") from exc
            send_keys("^v", pause=0.05)
            time.sleep(self.settle_seconds)
            open_button = self._find_open_button(dialog)
            if open_button is not None:
                open_button.click_input()
            else:
                dialog.set_focus()
                send_keys("{ENTER}", pause=0.05)
            time.sleep(self.settle_seconds * 3)
        except Exception as exc:
            return AttachmentProbe(True, True, False, False, False, False, (f"Chrome file picker path write failed: {exc}",))
        ready = self._attachment_ready(report_path.name)
        if not ready:
            return AttachmentProbe(True, True, True, False, False, False, ("Chrome attachment readiness was not verified",))
        return AttachmentProbe(True, True, True, True, True, False, ())


def _safe_window_title(window: Any) -> str | None:
    try:
        title = str(window.window_text() or "")
        return title or None
    except Exception:
        return None


def _set_windows_clipboard_text(text: str) -> None:
    if not hasattr(ctypes, "windll"):
        raise RuntimeError("Windows clipboard is unavailable on this platform")
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
    user32.OpenClipboard.restype = ctypes.c_int
    user32.EmptyClipboard.argtypes = []
    user32.EmptyClipboard.restype = ctypes.c_int
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p
    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = ctypes.c_int
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.restype = ctypes.c_int
    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.restype = ctypes.c_void_p

    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002
    data = text.encode("utf-16-le") + b"\x00\x00"
    handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
    if not handle:
        raise RuntimeError("GlobalAlloc failed for clipboard text")
    locked = kernel32.GlobalLock(handle)
    if not locked:
        kernel32.GlobalFree(handle)
        raise RuntimeError("GlobalLock failed for clipboard text")
    ctypes.memmove(locked, data, len(data))
    kernel32.GlobalUnlock(handle)
    if not user32.OpenClipboard(None):
        kernel32.GlobalFree(handle)
        raise RuntimeError("OpenClipboard failed")
    try:
        if not user32.EmptyClipboard():
            raise RuntimeError("EmptyClipboard failed")
        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
            raise RuntimeError("SetClipboardData failed")
        handle = None
    finally:
        user32.CloseClipboard()
        if handle:
            kernel32.GlobalFree(handle)


def build_adapter(provider: str) -> ChromeReportAttachAdapter:
    if provider.startswith("fake-"):
        return FakeChromeReportAttachAdapter(provider.removeprefix("fake-"))
    if provider == "pywinauto":
        return PywinautoChromeReportAttachAdapter()
    raise ValueError(f"Unknown provider: {provider}")


def make_result(
    *,
    ok: bool,
    result_label: str,
    target: StatusTargetConfig,
    live_browser: bool,
    stop_before_send: bool,
    confirmation_text_supplied: str | None,
    confirmation_matched: bool,
    operator_report_path: str | None,
    operator_report_sha256: str | None,
    computed_operator_report_sha256: str | None,
    operator_report_size_bytes: int | None,
    target_probe: ChromeTargetProbe | None,
    attachment_probe: AttachmentProbe | None,
    provider: str,
    issues: Sequence[str],
) -> ChromeOperatorReportAttachNoSendResult:
    focused = bool(target_probe.focused) if target_probe else False
    trigger_attempted = bool(attachment_probe.attachment_trigger_attempted) if attachment_probe else False
    picker_opened = bool(attachment_probe.file_picker_opened) if attachment_probe else False
    path_written = bool(attachment_probe.file_path_written) if attachment_probe else False
    safety = ChromeReportAttachSafety(
        browser_action_performed=bool(focused or trigger_attempted or picker_opened or path_written),
        chatgpt_submit_performed=False,
        operator_report_uploaded=False,
        status_message_posted=False,
        send_button_pressed=False,
        file_upload_attempted=bool(trigger_attempted or picker_opened or path_written),
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
    return ChromeOperatorReportAttachNoSendResult(
        ok=ok,
        result_label=result_label,
        patch_name=PATCH_NAME,
        patch_result="FAIL",
        selected_action=ACTION_UPLOAD_OPERATOR_REPORT,
        browser_lane=target.browser_lane,
        status_chat_configured=target.enabled,
        status_chat_url_hash_or_redacted=redact_url(target.target_url) or (f"sha256:{target.target_url_sha256}" if target.target_url_sha256 else None),
        target_url_sha256=target.target_url_sha256 or (sha256_text(target.target_url) if target.target_url else None),
        live_browser=live_browser,
        stop_before_send=stop_before_send,
        confirmation_text_supplied=confirmation_text_supplied,
        confirmation_matched=confirmation_matched,
        operator_report_path=operator_report_path,
        operator_report_sha256=operator_report_sha256,
        computed_operator_report_sha256=computed_operator_report_sha256,
        operator_report_size_bytes=operator_report_size_bytes,
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
        file_path_written=path_written,
        attachment_ready=bool(attachment_probe.attachment_ready) if attachment_probe else False,
        attachment_verified=bool(attachment_probe.attachment_verified) if attachment_probe else False,
        send_risk_detected=bool(attachment_probe.send_risk_detected) if attachment_probe else False,
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


def run_chrome_operator_report_attach_no_send(
    *,
    config_payload: Mapping[str, Any],
    provider: str,
    live_browser: bool,
    stop_before_send: bool,
    confirmation_text: str | None,
    operator_report_path: str | None,
    expected_operator_report_sha256: str | None = None,
) -> ChromeOperatorReportAttachNoSendResult:
    target = extract_status_target(config_payload)
    confirmation_matched = confirmation_text == CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND

    if not target.enabled:
        return make_result(ok=False, result_label=BLOCKED_CHROME_ATTACH_CONFIG_MISSING, target=target, live_browser=live_browser, stop_before_send=stop_before_send, confirmation_text_supplied=confirmation_text, confirmation_matched=confirmation_matched, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, operator_report_size_bytes=None, target_probe=None, attachment_probe=None, provider=provider, issues=("status_chat.enabled must be true",))
    if target.browser_lane != "chrome":
        return make_result(ok=False, result_label=BLOCKED_CHROME_ATTACH_BROWSER_MISMATCH, target=target, live_browser=live_browser, stop_before_send=stop_before_send, confirmation_text_supplied=confirmation_text, confirmation_matched=confirmation_matched, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, operator_report_size_bytes=None, target_probe=None, attachment_probe=None, provider=provider, issues=("browser_lane must be chrome",))
    if not target.target_url and not target.target_url_sha256:
        return make_result(ok=False, result_label=BLOCKED_CHROME_ATTACH_URL_INVALID, target=target, live_browser=live_browser, stop_before_send=stop_before_send, confirmation_text_supplied=confirmation_text, confirmation_matched=confirmation_matched, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, operator_report_size_bytes=None, target_probe=None, attachment_probe=None, provider=provider, issues=("target_url or target_url_sha256 is required",))
    if target.target_url and not valid_chatgpt_status_url(target.target_url):
        return make_result(ok=False, result_label=BLOCKED_CHROME_ATTACH_URL_INVALID, target=target, live_browser=live_browser, stop_before_send=stop_before_send, confirmation_text_supplied=confirmation_text, confirmation_matched=confirmation_matched, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, operator_report_size_bytes=None, target_probe=None, attachment_probe=None, provider=provider, issues=("target_url must be an https chatgpt.com conversation URL containing /c/<id>",))
    if target.target_url and target.target_url_sha256 and target.target_url_sha256 != sha256_text(target.target_url):
        return make_result(ok=False, result_label=BLOCKED_CHROME_ATTACH_URL_INVALID, target=target, live_browser=live_browser, stop_before_send=stop_before_send, confirmation_text_supplied=confirmation_text, confirmation_matched=confirmation_matched, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, operator_report_size_bytes=None, target_probe=None, attachment_probe=None, provider=provider, issues=("target_url_sha256 does not match target_url",))
    if confirmation_text is None:
        return make_result(ok=False, result_label=BLOCKED_CHROME_ATTACH_CONFIRMATION_REQUIRED, target=target, live_browser=live_browser, stop_before_send=stop_before_send, confirmation_text_supplied=None, confirmation_matched=False, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, operator_report_size_bytes=None, target_probe=None, attachment_probe=None, provider=provider, issues=("confirmation text is required",))
    if not confirmation_matched:
        return make_result(ok=False, result_label=BLOCKED_CHROME_ATTACH_CONFIRMATION_MISMATCH, target=target, live_browser=live_browser, stop_before_send=stop_before_send, confirmation_text_supplied=confirmation_text, confirmation_matched=False, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, operator_report_size_bytes=None, target_probe=None, attachment_probe=None, provider=provider, issues=(f"confirmation must exactly match {CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND}",))
    if not live_browser:
        return make_result(ok=False, result_label=BLOCKED_SEND_RISK, target=target, live_browser=False, stop_before_send=stop_before_send, confirmation_text_supplied=confirmation_text, confirmation_matched=True, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, operator_report_size_bytes=None, target_probe=None, attachment_probe=None, provider=provider, issues=("--live-browser is required for Chrome report attachment probing",))
    if not stop_before_send:
        return make_result(ok=False, result_label=BLOCKED_SEND_RISK, target=target, live_browser=True, stop_before_send=False, confirmation_text_supplied=confirmation_text, confirmation_matched=True, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, operator_report_size_bytes=None, target_probe=None, attachment_probe=None, provider=provider, issues=("--stop-before-send is required for CLU-03",))
    if operator_report_path is None or not str(operator_report_path).strip():
        return make_result(ok=False, result_label=BLOCKED_OPERATOR_REPORT_MISSING, target=target, live_browser=True, stop_before_send=True, confirmation_text_supplied=confirmation_text, confirmation_matched=True, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, operator_report_size_bytes=None, target_probe=None, attachment_probe=None, provider=provider, issues=("operator_report_path is required",))

    report_path = Path(operator_report_path)
    if not report_path.exists() or not report_path.is_file():
        return make_result(ok=False, result_label=BLOCKED_OPERATOR_REPORT_MISSING, target=target, live_browser=True, stop_before_send=True, confirmation_text_supplied=confirmation_text, confirmation_matched=True, operator_report_path=str(report_path), operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, operator_report_size_bytes=None, target_probe=None, attachment_probe=None, provider=provider, issues=(f"operator report file not found: {report_path}",))

    computed_hash = sha256_file(report_path)
    size_bytes = report_path.stat().st_size
    if expected_operator_report_sha256 and expected_operator_report_sha256 != computed_hash:
        return make_result(ok=False, result_label=BLOCKED_OPERATOR_REPORT_HASH_MISMATCH, target=target, live_browser=True, stop_before_send=True, confirmation_text_supplied=confirmation_text, confirmation_matched=True, operator_report_path=str(report_path), operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=computed_hash, operator_report_size_bytes=size_bytes, target_probe=None, attachment_probe=None, provider=provider, issues=("operator_report_sha256 does not match operator_report_path",))

    try:
        adapter = build_adapter(provider)
    except Exception as exc:
        return make_result(ok=False, result_label=BLOCKED_CHROME_TARGET_NOT_READY, target=target, live_browser=True, stop_before_send=True, confirmation_text_supplied=confirmation_text, confirmation_matched=True, operator_report_path=str(report_path), operator_report_sha256=computed_hash, computed_operator_report_sha256=computed_hash, operator_report_size_bytes=size_bytes, target_probe=None, attachment_probe=None, provider=provider, issues=(str(exc),))

    target_probe = adapter.focus_target(target)
    if target_probe.matching_target_count > 1:
        return make_result(ok=False, result_label=BLOCKED_CHROME_AMBIGUOUS_TARGET, target=target, live_browser=True, stop_before_send=True, confirmation_text_supplied=confirmation_text, confirmation_matched=True, operator_report_path=str(report_path), operator_report_sha256=computed_hash, computed_operator_report_sha256=computed_hash, operator_report_size_bytes=size_bytes, target_probe=target_probe, attachment_probe=None, provider=adapter.provider_name, issues=target_probe.issues)
    if target_probe.focused and target_probe.attachment_candidate_count < 1:
        return make_result(ok=False, result_label=BLOCKED_CHROME_ATTACHMENT_CONTROL_NOT_FOUND, target=target, live_browser=True, stop_before_send=True, confirmation_text_supplied=confirmation_text, confirmation_matched=True, operator_report_path=str(report_path), operator_report_sha256=computed_hash, computed_operator_report_sha256=computed_hash, operator_report_size_bytes=size_bytes, target_probe=target_probe, attachment_probe=None, provider=adapter.provider_name, issues=target_probe.issues)
    if not target_probe.ready or not target_probe.focused:
        return make_result(ok=False, result_label=BLOCKED_CHROME_TARGET_NOT_READY, target=target, live_browser=True, stop_before_send=True, confirmation_text_supplied=confirmation_text, confirmation_matched=True, operator_report_path=str(report_path), operator_report_sha256=computed_hash, computed_operator_report_sha256=computed_hash, operator_report_size_bytes=size_bytes, target_probe=target_probe, attachment_probe=None, provider=adapter.provider_name, issues=target_probe.issues)

    attachment_probe = adapter.attach_report_no_send(report_path)
    if attachment_probe.send_risk_detected:
        label = BLOCKED_SEND_RISK
    elif not attachment_probe.file_picker_opened or not attachment_probe.file_path_written:
        label = BLOCKED_CHROME_FILE_PICKER_NOT_READY
    elif not attachment_probe.attachment_verified:
        label = BLOCKED_ATTACHMENT_NOT_VERIFIED
    else:
        label = PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND

    return make_result(
        ok=label == PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND,
        result_label=label,
        target=target,
        live_browser=True,
        stop_before_send=True,
        confirmation_text_supplied=confirmation_text,
        confirmation_matched=True,
        operator_report_path=str(report_path),
        operator_report_sha256=computed_hash,
        computed_operator_report_sha256=computed_hash,
        operator_report_size_bytes=size_bytes,
        target_probe=target_probe,
        attachment_probe=attachment_probe,
        provider=adapter.provider_name,
        issues=tuple(target_probe.issues + attachment_probe.issues),
    )


def render_text(result: ChromeOperatorReportAttachNoSendResult) -> str:
    lines = [
        f"result_label: {result.result_label}",
        f"ok: {str(result.ok).lower()}",
        f"patch_name: {result.patch_name}",
        f"patch_result: {result.patch_result}",
        f"selected_action: {result.selected_action}",
        f"browser_lane: {result.browser_lane}",
        f"status_chat_configured: {str(result.status_chat_configured).lower()}",
        f"status_chat_url_hash_or_redacted: {result.status_chat_url_hash_or_redacted}",
        f"target_url_sha256: {result.target_url_sha256}",
        f"live_browser: {str(result.live_browser).lower()}",
        f"stop_before_send: {str(result.stop_before_send).lower()}",
        f"confirmation_text_supplied: {result.confirmation_text_supplied}",
        f"confirmation_matched: {str(result.confirmation_matched).lower()}",
        f"operator_report_path: {result.operator_report_path}",
        f"operator_report_sha256: {result.operator_report_sha256}",
        f"computed_operator_report_sha256: {result.computed_operator_report_sha256}",
        f"operator_report_size_bytes: {result.operator_report_size_bytes}",
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
        f"file_path_written: {str(result.file_path_written).lower()}",
        f"attachment_ready: {str(result.attachment_ready).lower()}",
        f"attachment_verified: {str(result.attachment_verified).lower()}",
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
    result: ChromeOperatorReportAttachNoSendResult,
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
    parser = argparse.ArgumentParser(description="Chrome operator report attach no-send probe")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-ambiguous-target", "fake-no-attachment-control", "fake-no-dialog", "fake-path-write-fails", "fake-attachment-not-ready", "fake-attachment-not-verified", "fake-send-risk", "pywinauto"), default="fake-ready")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--stop-before-send", action="store_true")
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
    payload = load_json_object(config_path) if config_path.exists() else {}
    result = run_chrome_operator_report_attach_no_send(
        config_payload=payload,
        provider=args.provider,
        live_browser=bool(args.live_browser),
        stop_before_send=bool(args.stop_before_send),
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