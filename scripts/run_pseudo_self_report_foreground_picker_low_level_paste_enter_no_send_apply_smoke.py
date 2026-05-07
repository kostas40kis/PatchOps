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
from typing import Any, Mapping, Sequence

PATCH_NAME = "pseudo_self_report_upload_no_send_repair_14_foreground_picker_low_level_paste_enter"
CONFIRM_TEXT = "PATCHOPS_CONFIRM_CHROME_FOREGROUND_PICKER_LOW_LEVEL_PASTE_ENTER_NO_SEND"
PASS_LABEL = "PASS_CHROME_SELF_REPORT_FOREGROUND_PICKER_LOW_LEVEL_PASTE_ENTER_ATTACHED_NO_SEND"
BLOCKED_CONFIG_INVALID = "BLOCKED_CHROME_FOREGROUND_PICKER_CONFIG_INVALID"
BLOCKED_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_FOREGROUND_PICKER_CONFIRMATION_REQUIRED"
BLOCKED_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_FOREGROUND_PICKER_CONFIRMATION_MISMATCH"
BLOCKED_LIVE_BROWSER_REQUIRED = "BLOCKED_CHROME_FOREGROUND_PICKER_LIVE_BROWSER_REQUIRED"
BLOCKED_REPORT_MISSING = "BLOCKED_CHROME_FOREGROUND_PICKER_REPORT_MISSING"
BLOCKED_REPORT_NOT_ON_DESKTOP = "BLOCKED_CHROME_FOREGROUND_PICKER_REPORT_NOT_ON_DESKTOP"
BLOCKED_REPORT_HASH_MISMATCH = "BLOCKED_CHROME_FOREGROUND_PICKER_REPORT_HASH_MISMATCH"
BLOCKED_TARGET_NOT_FOUND = "BLOCKED_CHROME_FOREGROUND_PICKER_TARGET_NOT_FOUND"
BLOCKED_TARGET_NOT_FOCUSED = "BLOCKED_CHROME_FOREGROUND_PICKER_TARGET_NOT_FOCUSED"
BLOCKED_PICKER_NOT_FOREGROUND = "BLOCKED_CHROME_FOREGROUND_PICKER_NOT_FOREGROUND"
BLOCKED_CLIPBOARD_FAILED = "BLOCKED_CHROME_FOREGROUND_PICKER_CLIPBOARD_FAILED"
BLOCKED_LOW_LEVEL_PASTE_FAILED = "BLOCKED_CHROME_FOREGROUND_PICKER_LOW_LEVEL_PASTE_FAILED"
BLOCKED_LOW_LEVEL_ENTER_FAILED = "BLOCKED_CHROME_FOREGROUND_PICKER_LOW_LEVEL_ENTER_FAILED"
BLOCKED_ATTACHMENT_NOT_VERIFIED = "BLOCKED_CHROME_FOREGROUND_PICKER_ATTACHMENT_NOT_VERIFIED"

DEFAULT_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_foreground_picker_low_level_paste_enter_no_send.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_foreground_picker_low_level_paste_enter_no_send.txt")
DEFAULT_DESKTOP_DIR = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"

CHROME_TITLE_TOKENS = ("chrome", "google chrome")
CHATGPT_TITLE_TOKENS = ("chatgpt", "openai", "patchops")
PICKER_TITLE_TOKENS = ("open", "upload", "choose", "select", "file")
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
VK_V = 0x56
VK_RETURN = 0x0D


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("union", INPUT_UNION)]


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


def _send_input_events(events: list[INPUT]) -> None:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    array_type = INPUT * len(events)
    sent = user32.SendInput(len(events), array_type(*events), ctypes.sizeof(INPUT))
    if sent != len(events):
        raise RuntimeError(f"SendInput sent {sent}/{len(events)} events")


def _key_event(vk: int, flags: int = 0) -> INPUT:
    extra = ctypes.pointer(ctypes.c_ulong(0))
    return INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=extra)))


def send_ctrl_v_low_level() -> None:
    _send_input_events([
        _key_event(VK_CONTROL, 0),
        _key_event(VK_V, 0),
        _key_event(VK_V, KEYEVENTF_KEYUP),
        _key_event(VK_CONTROL, KEYEVENTF_KEYUP),
    ])


def send_enter_low_level() -> None:
    _send_input_events([_key_event(VK_RETURN, 0), _key_event(VK_RETURN, KEYEVENTF_KEYUP)])


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


def safe_window_title(window: Any) -> str | None:
    try:
        text = str(window.window_text() or "").strip()
        return text or None
    except Exception:
        return None


@dataclass(frozen=True)
class SmokeResult:
    ok: bool
    result_label: str
    patch_name: str
    selected_action: str
    browser_lane: str
    live_browser: bool
    stop_before_send: bool
    confirmation_matched: bool
    desktop_directory: str | None
    self_report_path: str | None
    self_report_filename: str | None
    self_report_sha256: str | None
    computed_self_report_sha256: str | None
    existing_chrome_used: bool
    chrome_open_invoked: bool
    chrome_target_ready: bool
    chrome_target_focused: bool
    mouse_clicks_used: bool
    slash_key_pressed: bool
    upload_command_enter_pressed: bool
    foreground_picker_ready: bool
    foreground_picker_class: str | None
    foreground_picker_title_length: int | None
    clipboard_text_written: bool
    full_path_pasted_to_picker: bool
    low_level_ctrl_v_sent: bool
    low_level_enter_sent: bool
    picker_enter_pressed: bool
    enter_key_pressed_in_picker: bool
    enter_key_pressed_in_chat_composer: bool
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


def make_result(**kwargs: Any) -> SmokeResult:
    defaults: dict[str, Any] = dict(
        ok=False,
        result_label="BLOCKED_UNSET",
        patch_name=PATCH_NAME,
        selected_action="upload_self_report_foreground_picker_low_level_paste_enter_no_send",
        browser_lane="chrome",
        live_browser=True,
        stop_before_send=True,
        confirmation_matched=False,
        desktop_directory=None,
        self_report_path=None,
        self_report_filename=None,
        self_report_sha256=None,
        computed_self_report_sha256=None,
        existing_chrome_used=False,
        chrome_open_invoked=False,
        chrome_target_ready=False,
        chrome_target_focused=False,
        mouse_clicks_used=False,
        slash_key_pressed=False,
        upload_command_enter_pressed=False,
        foreground_picker_ready=False,
        foreground_picker_class=None,
        foreground_picker_title_length=None,
        clipboard_text_written=False,
        full_path_pasted_to_picker=False,
        low_level_ctrl_v_sent=False,
        low_level_enter_sent=False,
        picker_enter_pressed=False,
        enter_key_pressed_in_picker=False,
        enter_key_pressed_in_chat_composer=False,
        attachment_verified=False,
        before_attachment_count=0,
        after_attachment_count=0,
        operator_report_attached_to_composer=False,
        browser_action_performed=False,
        file_upload_attempted=False,
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
        selected_target_title_hash=None,
        selected_target_title_length=None,
        provider="pywinauto",
        issues=(),
    )
    defaults.update(kwargs)
    return SmokeResult(**defaults)


class LiveRunner:
    def __init__(self, *, attach_timeout_seconds: float = 35.0) -> None:
        self.attach_timeout_seconds = attach_timeout_seconds

    def _desktop(self) -> Any:
        from pywinauto import Desktop  # type: ignore
        return Desktop(backend="uia")

    def _keyboard(self) -> Any:
        from pywinauto import keyboard  # type: ignore
        return keyboard

    def _looks_like_chrome_target(self, window: Any) -> bool:
        title = (safe_window_title(window) or "").lower()
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

    def run(self, report_path: Path) -> SmokeResult:
        window, issues = self._target_window()
        if window is None:
            return make_result(result_label=BLOCKED_TARGET_NOT_FOUND, self_report_path=str(report_path), self_report_filename=report_path.name, issues=issues)
        title = safe_window_title(window)
        try:
            window.set_focus()
            time.sleep(0.65)
        except Exception as exc:
            return make_result(result_label=BLOCKED_TARGET_NOT_FOCUSED, self_report_path=str(report_path), self_report_filename=report_path.name, existing_chrome_used=True, chrome_target_ready=True, issues=(f"existing Chrome target focus failed: {exc}",), selected_target_title_hash=sha256_text(title or "") if title else None, selected_target_title_length=len(title) if title else None)

        before = self._visible_attachment_matches(window, report_path)
        try:
            keyboard = self._keyboard()
            keyboard.send_keys("/", pause=0.05)
            time.sleep(0.25)
            keyboard.send_keys("{ENTER}", pause=0.05)
            time.sleep(0.75)
        except Exception as exc:
            return make_result(result_label=BLOCKED_TARGET_NOT_FOCUSED, self_report_path=str(report_path), self_report_filename=report_path.name, existing_chrome_used=True, chrome_target_ready=True, chrome_target_focused=True, browser_action_performed=True, issues=(f"slash + Enter failed: {exc}",), selected_target_title_hash=sha256_text(title or "") if title else None, selected_target_title_length=len(title) if title else None)

        fg_class, fg_title = foreground_window_info()
        fg_ready = foreground_looks_like_picker()
        base = dict(
            self_report_path=str(report_path),
            self_report_filename=report_path.name,
            existing_chrome_used=True,
            chrome_target_ready=True,
            chrome_target_focused=True,
            browser_action_performed=True,
            slash_key_pressed=True,
            upload_command_enter_pressed=True,
            foreground_picker_ready=fg_ready,
            foreground_picker_class=fg_class,
            foreground_picker_title_length=len(fg_title),
            before_attachment_count=len(before),
            selected_target_title_hash=sha256_text(title or "") if title else None,
            selected_target_title_length=len(title) if title else None,
        )
        if not fg_ready:
            return make_result(result_label=BLOCKED_PICKER_NOT_FOREGROUND, issues=(f"foreground file picker not detected before paste; foreground_class={fg_class!r}; foreground_title_length={len(fg_title)}",), **base)

        try:
            set_clipboard_text(str(report_path.resolve(strict=False)))
        except Exception as exc:
            return make_result(result_label=BLOCKED_CLIPBOARD_FAILED, issues=(f"clipboard text write failed: {exc}",), **base)

        try:
            send_ctrl_v_low_level()
            time.sleep(0.25)
        except Exception as exc:
            return make_result(result_label=BLOCKED_LOW_LEVEL_PASTE_FAILED, clipboard_text_written=True, issues=(f"low-level Ctrl+V failed: {exc}",), **base)

        try:
            send_enter_low_level()
            time.sleep(1.0)
        except Exception as exc:
            return make_result(result_label=BLOCKED_LOW_LEVEL_ENTER_FAILED, clipboard_text_written=True, full_path_pasted_to_picker=True, low_level_ctrl_v_sent=True, issues=(f"low-level picker Enter failed: {exc}",), **base)

        verified, before_count, after_count = self._wait_for_new_attachment(window, report_path, before)
        if not verified:
            return make_result(
                result_label=BLOCKED_ATTACHMENT_NOT_VERIFIED,
                clipboard_text_written=True,
                full_path_pasted_to_picker=True,
                low_level_ctrl_v_sent=True,
                low_level_enter_sent=True,
                picker_enter_pressed=True,
                enter_key_pressed_in_picker=True,
                file_upload_attempted=True,
                before_attachment_count=before_count,
                after_attachment_count=after_count,
                issues=(f"new visible attachment was not verified after low-level full path paste + picker Enter; before_matches={before_count}; after_matches={after_count}",),
                **{key: value for key, value in base.items() if key not in {"before_attachment_count"}},
            )
        return make_result(
            ok=True,
            result_label=PASS_LABEL,
            clipboard_text_written=True,
            full_path_pasted_to_picker=True,
            low_level_ctrl_v_sent=True,
            low_level_enter_sent=True,
            picker_enter_pressed=True,
            enter_key_pressed_in_picker=True,
            attachment_verified=True,
            operator_report_attached_to_composer=True,
            file_upload_attempted=True,
            before_attachment_count=before_count,
            after_attachment_count=after_count,
            issues=(),
            **{key: value for key, value in base.items() if key not in {"before_attachment_count"}},
        )


def run_smoke(*, config_payload: Mapping[str, Any] | None, config_path: Path, provider: str, live_browser: bool, confirmation_text: str | None, self_report_path: str | None, expected_sha256: str | None, desktop_dir: Path) -> SmokeResult:
    config_ok, _target_url, url_hash, target_hash, config_issues = validate_config(config_payload)
    confirmation_matched = confirmation_text == CONFIRM_TEXT
    report = Path(self_report_path) if self_report_path else None
    common = dict(confirmation_matched=confirmation_matched, desktop_directory=str(desktop_dir), self_report_path=str(report) if report else None, self_report_filename=report.name if report else None)
    if not config_ok:
        return make_result(result_label=BLOCKED_CONFIG_INVALID, issues=config_issues, **common)
    if confirmation_text is None:
        return make_result(result_label=BLOCKED_CONFIRMATION_REQUIRED, issues=("live confirmation is required",), **common)
    if not confirmation_matched:
        return make_result(result_label=BLOCKED_CONFIRMATION_MISMATCH, issues=(f"confirmation must exactly match {CONFIRM_TEXT}",), **common)
    if not live_browser:
        return make_result(result_label=BLOCKED_LIVE_BROWSER_REQUIRED, live_browser=False, issues=("--live-browser is required",), **common)
    if report is None or not report.exists() or not report.is_file():
        return make_result(result_label=BLOCKED_REPORT_MISSING, issues=(f"self report not found: {report}",), **common)
    if not is_child_of(report, desktop_dir):
        return make_result(result_label=BLOCKED_REPORT_NOT_ON_DESKTOP, issues=(f"self report must be on Desktop: {desktop_dir}",), **common)
    computed = sha256_file(report)
    if expected_sha256 and expected_sha256 != computed:
        return make_result(result_label=BLOCKED_REPORT_HASH_MISMATCH, self_report_sha256=expected_sha256, computed_self_report_sha256=computed, issues=("self report hash mismatch",), **common)
    if provider.startswith("fake-"):
        if provider == "fake-ready":
            return make_result(ok=True, result_label=PASS_LABEL, confirmation_matched=True, desktop_directory=str(desktop_dir), self_report_path=str(report), self_report_filename=report.name, self_report_sha256=computed, computed_self_report_sha256=computed, existing_chrome_used=True, chrome_target_ready=True, chrome_target_focused=True, slash_key_pressed=True, upload_command_enter_pressed=True, foreground_picker_ready=True, foreground_picker_class="#32770", foreground_picker_title_length=4, clipboard_text_written=True, full_path_pasted_to_picker=True, low_level_ctrl_v_sent=True, low_level_enter_sent=True, picker_enter_pressed=True, enter_key_pressed_in_picker=True, attachment_verified=True, before_attachment_count=0, after_attachment_count=1, operator_report_attached_to_composer=True, browser_action_performed=True, file_upload_attempted=True, issues=(), provider=provider)
        return make_result(result_label=BLOCKED_PICKER_NOT_FOREGROUND, confirmation_matched=True, desktop_directory=str(desktop_dir), self_report_path=str(report), self_report_filename=report.name, self_report_sha256=computed, computed_self_report_sha256=computed, existing_chrome_used=True, chrome_target_ready=True, chrome_target_focused=True, slash_key_pressed=True, upload_command_enter_pressed=True, issues=("fake blocked",), provider=provider)
    result = LiveRunner().run(report)
    return make_result(**{**result.to_dict(), "confirmation_matched": True, "desktop_directory": str(desktop_dir), "self_report_sha256": computed, "computed_self_report_sha256": computed, "provider": provider})


def render_text(result: SmokeResult) -> str:
    lines: list[str] = []
    for key, value in result.to_dict().items():
        if key == "issues":
            continue
        if isinstance(value, bool):
            value = str(value).lower()
        lines.append(f"{key}: {value}")
    if result.issues:
        lines.append("issues:")
        for issue in result.issues:
            lines.append(f"- {issue}")
    else:
        lines.append("issues: none")
    return "\n".join(lines) + "\n"


def write_evidence(result: SmokeResult, *, json_output_path: Path = DEFAULT_JSON_OUTPUT_PATH, txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_text(result), encoding="utf-8")
    return json_output_path, txt_output_path


def write_self_report(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"patch_name: {PATCH_NAME}",
        "purpose: foreground Windows picker low-level full path paste and Enter, no Send",
        f"created_at: {datetime.now(timezone.utc).isoformat()}",
        "selected_action: upload_self_report_foreground_picker_low_level_paste_enter_no_send",
        "browser_lane: chrome",
        "manual_sequence: existing_chrome_loaded__slash__enter__foreground_picker__low_level_ctrl_v_full_path__low_level_enter",
        f"expected_result_label: {PASS_LABEL}",
        "operator_report_uploaded: false",
        "chatgpt_submit_performed: false",
        "send_button_pressed: false",
        "chrome_open_invoked: false",
        "mouse_clicks_used: false",
        "raw_conversation_text_available: false",
        "selenium_used: false",
        "webdriver_used: false",
        "browser_dom_automation_used: false",
        "cloudflare_bypass_attempted: false",
        "captcha_bypass_attempted: false",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return sha256_file(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Existing Chrome target, slash+Enter, low-level Ctrl+V full path into foreground picker, low-level Enter, no Send")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--desktop-dir", default=str(DEFAULT_DESKTOP_DIR))
    parser.add_argument("--self-report-filename", default="pseudo_self_report_upload_no_send_repair_14_foreground_picker_low_level_paste_enter_self_report.txt")
    parser.add_argument("--provider", choices=("pywinauto", "fake-ready", "fake-blocked"), default="pywinauto")
    parser.add_argument("--confirm-live-browser-text", default=CONFIRM_TEXT)
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config_path)
    desktop_dir = Path(args.desktop_dir)
    self_report_path = desktop_dir / args.self_report_filename
    self_report_hash = write_self_report(self_report_path)
    config_payload = load_json_object(config_path) if config_path.exists() else None
    result = run_smoke(
        config_payload=config_payload,
        config_path=config_path,
        provider=args.provider,
        live_browser=True,
        confirmation_text=args.confirm_live_browser_text,
        self_report_path=str(self_report_path),
        expected_sha256=self_report_hash,
        desktop_dir=desktop_dir,
    )
    write_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))
    print(f"DESKTOP_DIR: {desktop_dir}")
    print(f"SELF_REPORT_FILENAME: {self_report_path.name}")
    print(f"SELF_REPORT_PATH: {self_report_path}")
    print(f"SELF_REPORT_SHA256: {self_report_hash}")
    print(f"EVIDENCE_JSON: {args.json_output_path}")
    print(f"EVIDENCE_TXT: {args.txt_output_path}")
    print(render_text(result), end="")
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())