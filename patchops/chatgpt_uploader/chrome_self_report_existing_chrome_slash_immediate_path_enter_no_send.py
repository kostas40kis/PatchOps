from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

PATCH_NAME = "pseudo_self_report_upload_no_send_repair_13_existing_chrome_slash_immediate_path_enter"
CONFIRM_CHROME_EXISTING_SLASH_IMMEDIATE_PATH_ENTER_NO_SEND = "PATCHOPS_CONFIRM_CHROME_EXISTING_SLASH_IMMEDIATE_PATH_ENTER_NO_SEND"
PASS_CHROME_SELF_REPORT_EXISTING_SLASH_IMMEDIATE_PATH_ENTER_ATTACHED_NO_SEND = "PASS_CHROME_SELF_REPORT_EXISTING_SLASH_IMMEDIATE_PATH_ENTER_ATTACHED_NO_SEND"
BLOCKED_CHROME_EXISTING_SLASH_CONFIG_INVALID = "BLOCKED_CHROME_EXISTING_SLASH_CONFIG_INVALID"
BLOCKED_CHROME_EXISTING_SLASH_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_EXISTING_SLASH_CONFIRMATION_REQUIRED"
BLOCKED_CHROME_EXISTING_SLASH_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_EXISTING_SLASH_CONFIRMATION_MISMATCH"
BLOCKED_CHROME_EXISTING_SLASH_LIVE_BROWSER_REQUIRED = "BLOCKED_CHROME_EXISTING_SLASH_LIVE_BROWSER_REQUIRED"
BLOCKED_CHROME_EXISTING_SLASH_REPORT_MISSING = "BLOCKED_CHROME_EXISTING_SLASH_REPORT_MISSING"
BLOCKED_CHROME_EXISTING_SLASH_REPORT_NOT_ON_DESKTOP = "BLOCKED_CHROME_EXISTING_SLASH_REPORT_NOT_ON_DESKTOP"
BLOCKED_CHROME_EXISTING_SLASH_REPORT_HASH_MISMATCH = "BLOCKED_CHROME_EXISTING_SLASH_REPORT_HASH_MISMATCH"
BLOCKED_CHROME_EXISTING_SLASH_TARGET_NOT_FOUND = "BLOCKED_CHROME_EXISTING_SLASH_TARGET_NOT_FOUND"
BLOCKED_CHROME_EXISTING_SLASH_TARGET_NOT_FOCUSED = "BLOCKED_CHROME_EXISTING_SLASH_TARGET_NOT_FOCUSED"
BLOCKED_CHROME_EXISTING_SLASH_FOREGROUND_PICKER_NOT_READY = "BLOCKED_CHROME_EXISTING_SLASH_FOREGROUND_PICKER_NOT_READY"
BLOCKED_CHROME_EXISTING_SLASH_PATH_PASTE_FAILED = "BLOCKED_CHROME_EXISTING_SLASH_PATH_PASTE_FAILED"
BLOCKED_CHROME_EXISTING_SLASH_PICKER_ENTER_FAILED = "BLOCKED_CHROME_EXISTING_SLASH_PICKER_ENTER_FAILED"
BLOCKED_CHROME_EXISTING_SLASH_ATTACHMENT_NOT_VERIFIED = "BLOCKED_CHROME_EXISTING_SLASH_ATTACHMENT_NOT_VERIFIED"

DEFAULT_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_existing_chrome_slash_immediate_path_enter_no_send.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_existing_chrome_slash_immediate_path_enter_no_send.txt")
DEFAULT_DESKTOP_DIR = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"

CHROME_TITLE_TOKENS = ("chrome", "google chrome")
CHATGPT_TITLE_TOKENS = ("chatgpt", "openai", "patchops")
PICKER_TITLE_TOKENS = ("open", "upload", "choose", "select", "file")
SAFE_KEYBOARD_ACTIONS = ("SLASH_IN_EXISTING_CHAT", "ENTER_FOR_UPLOAD_COMMAND_ONLY", "CTRL_V_FULL_PATH_IN_FOREGROUND_PICKER", "ENTER_IN_FOREGROUND_PICKER_ONLY")
FORBIDDEN_KEYBOARD_SHORTCUTS_USED: tuple[str, ...] = ()
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def normalize_bool(value: Any, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def validate_config(config_payload: Mapping[str, Any] | None) -> tuple[bool, str | None, str | None, str | None, tuple[str, ...]]:
    if not config_payload:
        return False, None, None, None, ("status target config is required",)
    status = config_payload.get("status_chat")
    if not isinstance(status, Mapping):
        return False, None, None, None, ("status_chat object is required",)
    issues: list[str] = []
    enabled = normalize_bool(status.get("enabled"), default=False)
    lane = str(status.get("browser_lane") or "").strip()
    target_url = str(status.get("target_url") or "").strip()
    target_hash = str(status.get("target_url_sha256") or "").strip() or None
    if not enabled:
        issues.append("status_chat.enabled must be true")
    if lane != "chrome":
        issues.append("browser_lane must be chrome")
    if not target_url.startswith("https://chatgpt.com/") or "/c/" not in target_url:
        issues.append("target_url must be a ChatGPT conversation URL")
    url_hash = sha256_text(target_url) if target_url else None
    if target_url and target_hash and target_hash != url_hash:
        issues.append("target_url_sha256 does not match target_url")
    return not issues, target_url or None, url_hash, target_hash, tuple(issues)


def is_child_of(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except ValueError:
        return False


def set_clipboard_text(value: str) -> None:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
    user32.OpenClipboard.restype = ctypes.c_bool
    user32.EmptyClipboard.argtypes = []
    user32.EmptyClipboard.restype = ctypes.c_bool
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p
    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = ctypes.c_bool
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.restype = ctypes.c_bool
    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.restype = ctypes.c_void_p
    payload = (value + "\0").encode("utf-16le")
    handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(payload))
    if not handle:
        raise RuntimeError("GlobalAlloc failed for clipboard text")
    locked = kernel32.GlobalLock(handle)
    if not locked:
        kernel32.GlobalFree(handle)
        raise RuntimeError("GlobalLock failed for clipboard text")
    try:
        ctypes.memmove(locked, payload, len(payload))
    finally:
        kernel32.GlobalUnlock(handle)
    if not user32.OpenClipboard(None):
        kernel32.GlobalFree(handle)
        raise RuntimeError("OpenClipboard failed")
    try:
        if not user32.EmptyClipboard():
            raise RuntimeError("EmptyClipboard failed")
        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
            raise RuntimeError("SetClipboardData(CF_UNICODETEXT) failed")
        handle = None
    finally:
        user32.CloseClipboard()
        if handle:
            kernel32.GlobalFree(handle)


def foreground_window_info() -> tuple[str, str]:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    hwnd = user32.GetForegroundWindow()
    class_buf = ctypes.create_unicode_buffer(256)
    title_buf = ctypes.create_unicode_buffer(512)
    user32.GetClassNameW(hwnd, class_buf, 256)
    user32.GetWindowTextW(hwnd, title_buf, 512)
    return class_buf.value or "", title_buf.value or ""


def foreground_looks_like_picker() -> bool:
    cls, title = foreground_window_info()
    lowered = title.lower()
    return cls == "#32770" or any(token in lowered for token in PICKER_TITLE_TOKENS)


@dataclass(frozen=True)
class ExistingSlashImmediateProbe:
    existing_chrome_used: bool
    chrome_open_invoked: bool
    chrome_target_ready: bool
    chrome_target_focused: bool
    slash_key_pressed: bool
    upload_command_enter_pressed: bool
    foreground_picker_ready: bool
    foreground_picker_class: str | None
    foreground_picker_title_length: int | None
    full_path_to_paste: str | None
    full_path_clipboard_written: bool
    ctrl_v_pressed_in_picker: bool
    picker_enter_pressed: bool
    attachment_verified: bool
    before_attachment_count: int
    after_attachment_count: int
    selected_window_title: str | None
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExistingSlashImmediateResult:
    ok: bool
    result_label: str
    patch_name: str
    selected_action: str
    browser_lane: str
    live_browser: bool
    stop_before_send: bool
    confirmation_matched: bool
    config_path: str
    status_chat_configured: bool
    status_chat_url_hash_or_redacted: str | None
    target_url_sha256: str | None
    desktop_directory: str | None
    self_report_path: str | None
    self_report_filename: str | None
    self_report_sha256: str | None
    computed_self_report_sha256: str | None
    existing_chrome_used: bool
    chrome_open_invoked: bool
    chrome_target_ready: bool
    chrome_target_focused: bool
    keyboard_actions_used: tuple[str, ...]
    forbidden_keyboard_shortcuts_used: tuple[str, ...]
    mouse_clicks_used: bool
    slash_key_pressed: bool
    upload_command_enter_pressed: bool
    enter_key_pressed_in_chat_composer: bool
    foreground_picker_ready: bool
    foreground_picker_class: str | None
    foreground_picker_title_length: int | None
    picker_detection_wait_used: bool
    full_path_pasted_to_picker: bool
    filename_only_written_to_picker: bool
    open_button_clicked: bool
    ctrl_v_pressed_in_picker: bool
    picker_enter_pressed: bool
    enter_key_pressed_in_picker: bool
    attachment_verified: bool
    before_attachment_count: int
    after_attachment_count: int
    operator_report_attached_to_composer: bool
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
    selected_target_title_hash: str | None
    selected_target_title_length: int | None
    provider: str
    issues: tuple[str, ...]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExistingSlashImmediateAdapter(Protocol):
    provider_name: str

    def attach_via_existing_chrome_slash_immediate_path_enter(self, report_path: Path) -> ExistingSlashImmediateProbe:
        ...


class FakeExistingSlashImmediateAdapter:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.provider_name = f"fake-{mode}"

    def attach_via_existing_chrome_slash_immediate_path_enter(self, report_path: Path) -> ExistingSlashImmediateProbe:
        title = "PatchOps - ChatGPT - Google Chrome"
        if self.mode == "no-target":
            return ExistingSlashImmediateProbe(False, False, False, False, False, False, False, None, None, str(report_path), False, False, False, False, 0, 0, None, ("fake existing target missing",))
        if self.mode == "no-picker":
            return ExistingSlashImmediateProbe(True, False, True, True, True, True, False, "Chrome_WidgetWin_1", 23, str(report_path), False, False, False, False, 0, 0, title, ("foreground picker not ready after slash Enter",))
        if self.mode == "paste-failed":
            return ExistingSlashImmediateProbe(True, False, True, True, True, True, True, "#32770", 4, str(report_path), False, False, False, False, 0, 0, title, ("fake path paste failed",))
        if self.mode == "enter-failed":
            return ExistingSlashImmediateProbe(True, False, True, True, True, True, True, "#32770", 4, str(report_path), True, True, False, False, 0, 0, title, ("fake picker enter failed",))
        if self.mode == "not-verified":
            return ExistingSlashImmediateProbe(True, False, True, True, True, True, True, "#32770", 4, str(report_path), True, True, True, False, 0, 0, title, ("fake attachment not verified",))
        return ExistingSlashImmediateProbe(True, False, True, True, True, True, True, "#32770", 4, str(report_path), True, True, True, True, 0, 1, title, ())


class PywinautoExistingSlashImmediateAdapter:
    provider_name = "pywinauto"

    def __init__(self, *, settle_seconds: float = 0.75, attach_timeout_seconds: float = 30.0) -> None:
        self.settle_seconds = settle_seconds
        self.attach_timeout_seconds = attach_timeout_seconds

    def _desktop(self) -> Any:
        try:
            from pywinauto import Desktop  # type: ignore
        except Exception as exc:
            raise RuntimeError(f"pywinauto is required: {exc}") from exc
        return Desktop(backend="uia")

    def _keyboard(self) -> Any:
        try:
            from pywinauto import keyboard  # type: ignore
        except Exception as exc:
            raise RuntimeError(f"pywinauto keyboard is required: {exc}") from exc
        return keyboard

    def _looks_like_chrome_target(self, window: Any) -> bool:
        title = (_safe_window_title(window) or "").lower()
        return any(token in title for token in CHROME_TITLE_TOKENS) and any(token in title for token in CHATGPT_TITLE_TOKENS)

    def _target_window(self) -> tuple[Any | None, tuple[str, ...]]:
        try:
            windows = list(self._desktop().windows())
        except Exception as exc:
            return None, (str(exc),)
        matches = [window for window in windows if self._looks_like_chrome_target(window)]
        if len(matches) < 1:
            return None, ("no existing loaded Chrome ChatGPT/PatchOps target window found",)
        return matches[0], ()

    def _element_rect_tuple(self, element: Any) -> tuple[int, int, int, int] | None:
        try:
            rect = element.rectangle()
            return (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))
        except Exception:
            return None

    def _visible_attachment_matches(self, window: Any, report_path: Path) -> set[tuple[str, tuple[int, int, int, int]]]:
        wanted = {report_path.name.lower(), report_path.stem.lower()}
        window_rect = self._element_rect_tuple(window)
        if window_rect is None:
            return set()
        lower_threshold = window_rect[1] + int(max(1, window_rect[3] - window_rect[1]) * 0.45)
        matches: set[tuple[str, tuple[int, int, int, int]]] = set()
        try:
            descendants = list(window.descendants())
        except Exception:
            descendants = []
        for element in descendants:
            try:
                if not bool(element.is_visible()):
                    continue
                text = str(element.window_text() or element.element_info.name or "").strip()
            except Exception:
                continue
            rect = self._element_rect_tuple(element)
            if rect is None or rect[3] < lower_threshold:
                continue
            lowered = text.lower()
            if any(token and token in lowered for token in wanted):
                matches.add((text[:160], rect))
        return matches

    def _wait_for_new_attachment(self, window: Any, report_path: Path, before: set[tuple[str, tuple[int, int, int, int]]]) -> tuple[bool, int, int]:
        deadline = time.monotonic() + self.attach_timeout_seconds
        latest_count = 0
        while time.monotonic() < deadline:
            after = self._visible_attachment_matches(window, report_path)
            latest_count = len(after)
            if after - before:
                return True, len(before), latest_count
            time.sleep(0.5)
        return False, len(before), latest_count

    def attach_via_existing_chrome_slash_immediate_path_enter(self, report_path: Path) -> ExistingSlashImmediateProbe:
        window, issues = self._target_window()
        if window is None:
            return ExistingSlashImmediateProbe(False, False, False, False, False, False, False, None, None, str(report_path), False, False, False, False, 0, 0, None, issues)
        title = _safe_window_title(window)
        try:
            window.set_focus()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return ExistingSlashImmediateProbe(True, False, True, False, False, False, False, None, None, str(report_path), False, False, False, False, 0, 0, title, (f"existing Chrome target focus failed: {exc}",))

        before = self._visible_attachment_matches(window, report_path)
        try:
            keyboard = self._keyboard()
            keyboard.send_keys("/", pause=0.05)
            time.sleep(0.25)
            keyboard.send_keys("{ENTER}", pause=0.05)
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return ExistingSlashImmediateProbe(True, False, True, True, False, False, False, None, None, str(report_path), False, False, False, False, len(before), len(before), title, (f"slash + upload-command Enter failed: {exc}",))

        fg_class, fg_title = foreground_window_info()
        fg_ready = foreground_looks_like_picker()
        if not fg_ready:
            return ExistingSlashImmediateProbe(True, False, True, True, True, True, False, fg_class, len(fg_title), str(report_path), False, False, False, False, len(before), len(before), title, (f"foreground Windows file picker was not ready after slash + Enter; foreground_class={fg_class!r}; foreground_title_length={len(fg_title)}",))

        try:
            set_clipboard_text(str(report_path.resolve(strict=False)))
            keyboard.send_keys("^v", pause=0.05)
            time.sleep(0.2)
        except Exception as exc:
            return ExistingSlashImmediateProbe(True, False, True, True, True, True, True, fg_class, len(fg_title), str(report_path), False, False, False, False, len(before), len(before), title, (f"full Desktop path paste into foreground picker failed: {exc}",))

        try:
            keyboard.send_keys("{ENTER}", pause=0.05)
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return ExistingSlashImmediateProbe(True, False, True, True, True, True, True, fg_class, len(fg_title), str(report_path), True, True, False, False, len(before), len(before), title, (f"foreground picker Enter failed after full path paste: {exc}",))

        verified, before_count, after_count = self._wait_for_new_attachment(window, report_path, before)
        if not verified:
            return ExistingSlashImmediateProbe(True, False, True, True, True, True, True, fg_class, len(fg_title), str(report_path), True, True, True, False, before_count, after_count, title, (f"new visible attachment was not verified after immediate full path paste + picker Enter; before_matches={before_count}; after_matches={after_count}",))
        return ExistingSlashImmediateProbe(True, False, True, True, True, True, True, fg_class, len(fg_title), str(report_path), True, True, True, True, before_count, after_count, title, ())


def _safe_window_title(window: Any) -> str | None:
    try:
        text = str(window.window_text() or "").strip()
        return text or None
    except Exception:
        return None


def build_adapter(provider: str) -> ExistingSlashImmediateAdapter:
    if provider.startswith("fake-"):
        return FakeExistingSlashImmediateAdapter(provider.removeprefix("fake-"))
    if provider == "pywinauto":
        return PywinautoExistingSlashImmediateAdapter()
    raise ValueError(f"Unknown provider: {provider}")


def make_result(*, ok: bool, result_label: str, config_path: Path, status_chat_configured: bool, url_hash: str | None, target_hash: str | None, live_browser: bool, confirmation_matched: bool, desktop_dir: Path | None, report_path: Path | None, expected_hash: str | None, computed_hash: str | None, probe: ExistingSlashImmediateProbe | None, provider: str, issues: Sequence[str]) -> ExistingSlashImmediateResult:
    title = probe.selected_window_title if probe else None
    return ExistingSlashImmediateResult(
        ok=ok,
        result_label=result_label,
        patch_name=PATCH_NAME,
        selected_action="upload_self_report_existing_chrome_slash_immediate_full_path_enter_no_send",
        browser_lane="chrome",
        live_browser=live_browser,
        stop_before_send=True,
        confirmation_matched=confirmation_matched,
        config_path=str(config_path),
        status_chat_configured=status_chat_configured,
        status_chat_url_hash_or_redacted=url_hash,
        target_url_sha256=target_hash,
        desktop_directory=str(desktop_dir) if desktop_dir else None,
        self_report_path=str(report_path) if report_path else None,
        self_report_filename=report_path.name if report_path else None,
        self_report_sha256=expected_hash,
        computed_self_report_sha256=computed_hash,
        existing_chrome_used=bool(probe and probe.existing_chrome_used),
        chrome_open_invoked=False,
        chrome_target_ready=bool(probe and probe.chrome_target_ready),
        chrome_target_focused=bool(probe and probe.chrome_target_focused),
        keyboard_actions_used=SAFE_KEYBOARD_ACTIONS if probe and probe.slash_key_pressed else (),
        forbidden_keyboard_shortcuts_used=FORBIDDEN_KEYBOARD_SHORTCUTS_USED,
        mouse_clicks_used=False,
        slash_key_pressed=bool(probe and probe.slash_key_pressed),
        upload_command_enter_pressed=bool(probe and probe.upload_command_enter_pressed),
        enter_key_pressed_in_chat_composer=False,
        foreground_picker_ready=bool(probe and probe.foreground_picker_ready),
        foreground_picker_class=probe.foreground_picker_class if probe else None,
        foreground_picker_title_length=probe.foreground_picker_title_length if probe else None,
        picker_detection_wait_used=False,
        full_path_pasted_to_picker=bool(probe and probe.ctrl_v_pressed_in_picker),
        filename_only_written_to_picker=False,
        open_button_clicked=False,
        ctrl_v_pressed_in_picker=bool(probe and probe.ctrl_v_pressed_in_picker),
        picker_enter_pressed=bool(probe and probe.picker_enter_pressed),
        enter_key_pressed_in_picker=bool(probe and probe.picker_enter_pressed),
        attachment_verified=bool(probe and probe.attachment_verified),
        before_attachment_count=probe.before_attachment_count if probe else 0,
        after_attachment_count=probe.after_attachment_count if probe else 0,
        operator_report_attached_to_composer=bool(probe and probe.attachment_verified),
        browser_action_performed=bool(probe and (probe.chrome_target_focused or probe.slash_key_pressed or probe.picker_enter_pressed)),
        file_upload_attempted=bool(probe and probe.picker_enter_pressed),
        operator_report_uploaded=False,
        chatgpt_submit_performed=False,
        status_message_posted=False,
        send_button_pressed=False,
        raw_conversation_text_available=False,
        selenium_used=False,
        webdriver_used=False,
        browser_dom_automation_used=False,
        cloudflare_bypass_attempted=False,
        captcha_bypass_attempted=False,
        selected_target_title_hash=sha256_text(title) if title else None,
        selected_target_title_length=len(title) if title else None,
        provider=provider,
        issues=tuple(issues),
    )


def run_existing_chrome_slash_immediate_path_enter_no_send(*, config_payload: Mapping[str, Any] | None, config_path: Path = DEFAULT_CONFIG_PATH, provider: str = "fake-ready", live_browser: bool, confirmation_text: str | None, self_report_path: str | None, expected_self_report_sha256: str | None = None, desktop_dir: str | None = None) -> ExistingSlashImmediateResult:
    config_ok, target_url, url_hash, target_hash, config_issues = validate_config(config_payload)
    confirmation_matched = confirmation_text == CONFIRM_CHROME_EXISTING_SLASH_IMMEDIATE_PATH_ENTER_NO_SEND
    desktop_path = Path(desktop_dir) if desktop_dir else DEFAULT_DESKTOP_DIR
    report = Path(self_report_path) if self_report_path else None
    empty = ExistingSlashImmediateProbe(False, False, False, False, False, False, False, None, None, str(report) if report else None, False, False, False, False, 0, 0, None, ())
    if not config_ok or not target_url:
        return make_result(ok=False, result_label=BLOCKED_CHROME_EXISTING_SLASH_CONFIG_INVALID, config_path=config_path, status_chat_configured=False, url_hash=url_hash, target_hash=target_hash, live_browser=live_browser, confirmation_matched=confirmation_matched, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=None, probe=empty, provider=provider, issues=config_issues)
    if confirmation_text is None:
        return make_result(ok=False, result_label=BLOCKED_CHROME_EXISTING_SLASH_CONFIRMATION_REQUIRED, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=live_browser, confirmation_matched=False, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=None, probe=empty, provider=provider, issues=("live existing-Chrome slash immediate path confirmation is required",))
    if not confirmation_matched:
        return make_result(ok=False, result_label=BLOCKED_CHROME_EXISTING_SLASH_CONFIRMATION_MISMATCH, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=live_browser, confirmation_matched=False, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=None, probe=empty, provider=provider, issues=(f"confirmation must exactly match {CONFIRM_CHROME_EXISTING_SLASH_IMMEDIATE_PATH_ENTER_NO_SEND}",))
    if not live_browser:
        return make_result(ok=False, result_label=BLOCKED_CHROME_EXISTING_SLASH_LIVE_BROWSER_REQUIRED, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=False, confirmation_matched=True, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=None, probe=empty, provider=provider, issues=("--live-browser is required",))
    if report is None or not report.exists() or not report.is_file():
        return make_result(ok=False, result_label=BLOCKED_CHROME_EXISTING_SLASH_REPORT_MISSING, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=True, confirmation_matched=True, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=None, probe=empty, provider=provider, issues=(f"self report not found: {report}",))
    if not is_child_of(report, desktop_path):
        return make_result(ok=False, result_label=BLOCKED_CHROME_EXISTING_SLASH_REPORT_NOT_ON_DESKTOP, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=True, confirmation_matched=True, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=None, probe=empty, provider=provider, issues=(f"self report must be on Desktop: {desktop_path}",))
    computed = sha256_file(report)
    if expected_self_report_sha256 and expected_self_report_sha256 != computed:
        return make_result(ok=False, result_label=BLOCKED_CHROME_EXISTING_SLASH_REPORT_HASH_MISMATCH, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=True, confirmation_matched=True, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=computed, probe=empty, provider=provider, issues=("self report hash mismatch",))
    adapter = build_adapter(provider)
    try:
        probe = adapter.attach_via_existing_chrome_slash_immediate_path_enter(report)
    except Exception as exc:
        return make_result(ok=False, result_label=BLOCKED_CHROME_EXISTING_SLASH_TARGET_NOT_FOUND, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=True, confirmation_matched=True, desktop_dir=desktop_path, report_path=report, expected_hash=computed, computed_hash=computed, probe=empty, provider=provider, issues=(str(exc),))
    if not probe.existing_chrome_used or not probe.chrome_target_ready:
        label = BLOCKED_CHROME_EXISTING_SLASH_TARGET_NOT_FOUND
    elif not probe.chrome_target_focused:
        label = BLOCKED_CHROME_EXISTING_SLASH_TARGET_NOT_FOCUSED
    elif not probe.foreground_picker_ready:
        label = BLOCKED_CHROME_EXISTING_SLASH_FOREGROUND_PICKER_NOT_READY
    elif not probe.full_path_clipboard_written or not probe.ctrl_v_pressed_in_picker:
        label = BLOCKED_CHROME_EXISTING_SLASH_PATH_PASTE_FAILED
    elif not probe.picker_enter_pressed:
        label = BLOCKED_CHROME_EXISTING_SLASH_PICKER_ENTER_FAILED
    elif not probe.attachment_verified:
        label = BLOCKED_CHROME_EXISTING_SLASH_ATTACHMENT_NOT_VERIFIED
    else:
        label = PASS_CHROME_SELF_REPORT_EXISTING_SLASH_IMMEDIATE_PATH_ENTER_ATTACHED_NO_SEND
    return make_result(ok=label == PASS_CHROME_SELF_REPORT_EXISTING_SLASH_IMMEDIATE_PATH_ENTER_ATTACHED_NO_SEND, result_label=label, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=True, confirmation_matched=True, desktop_dir=desktop_path, report_path=report, expected_hash=computed, computed_hash=computed, probe=probe, provider=adapter.provider_name, issues=probe.issues)


def render_text(result: ExistingSlashImmediateResult) -> str:
    lines = [f"{key}: {str(value).lower() if isinstance(value, bool) else value}" for key, value in result.to_dict().items() if key != "issues"]
    if result.issues:
        lines.append("issues:")
        for issue in result.issues:
            lines.append(f"- {issue}")
    else:
        lines.append("issues: none")
    return "\n".join(lines) + "\n"


def write_evidence(result: ExistingSlashImmediateResult, *, json_output_path: Path = DEFAULT_JSON_OUTPUT_PATH, txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_text(result), encoding="utf-8")
    return json_output_path, txt_output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Use existing Chrome target, slash+Enter, immediately paste full Desktop path into foreground picker, picker Enter, no Send")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-no-picker", "fake-paste-failed", "fake-enter-failed", "fake-not-verified", "pywinauto"), default="fake-ready")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--self-report-path", required=True)
    parser.add_argument("--self-report-sha256", default=None)
    parser.add_argument("--desktop-dir", default=str(DEFAULT_DESKTOP_DIR))
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config_path)
    config_payload = load_json_object(config_path) if config_path.exists() else None
    result = run_existing_chrome_slash_immediate_path_enter_no_send(
        config_payload=config_payload,
        config_path=config_path,
        provider=args.provider,
        live_browser=bool(args.live_browser),
        confirmation_text=args.confirm_live_browser_text,
        self_report_path=args.self_report_path,
        expected_self_report_sha256=args.self_report_sha256,
        desktop_dir=args.desktop_dir,
    )
    write_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        print(render_text(result), end="")
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())