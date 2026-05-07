from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import time
from ctypes import wintypes
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH_NAME = "pseudo_self_report_upload_no_send_repair_16_win32_dialog_filename_submit"
CONFIRM_TEXT = "PATCHOPS_CONFIRM_CHROME_WIN32_DIALOG_FILENAME_SUBMIT_NO_SEND"
PASS_LABEL = "PASS_CHROME_SELF_REPORT_WIN32_DIALOG_FILENAME_SUBMIT_ATTACHED_NO_SEND"
BLOCKED_CONFIG_INVALID = "BLOCKED_CHROME_WIN32_DIALOG_CONFIG_INVALID"
BLOCKED_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_WIN32_DIALOG_CONFIRMATION_REQUIRED"
BLOCKED_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_WIN32_DIALOG_CONFIRMATION_MISMATCH"
BLOCKED_LIVE_BROWSER_REQUIRED = "BLOCKED_CHROME_WIN32_DIALOG_LIVE_BROWSER_REQUIRED"
BLOCKED_REPORT_MISSING = "BLOCKED_CHROME_WIN32_DIALOG_REPORT_MISSING"
BLOCKED_REPORT_NOT_ON_DESKTOP = "BLOCKED_CHROME_WIN32_DIALOG_REPORT_NOT_ON_DESKTOP"
BLOCKED_REPORT_HASH_MISMATCH = "BLOCKED_CHROME_WIN32_DIALOG_REPORT_HASH_MISMATCH"
BLOCKED_TARGET_NOT_FOUND = "BLOCKED_CHROME_WIN32_DIALOG_TARGET_NOT_FOUND"
BLOCKED_TARGET_NOT_FOCUSED = "BLOCKED_CHROME_WIN32_DIALOG_TARGET_NOT_FOCUSED"
BLOCKED_PICKER_NOT_FOREGROUND = "BLOCKED_CHROME_WIN32_DIALOG_PICKER_NOT_FOREGROUND"
BLOCKED_DIALOG_FILENAME_WRITE_FAILED = "BLOCKED_CHROME_WIN32_DIALOG_FILENAME_WRITE_FAILED"
BLOCKED_DIALOG_SUBMIT_FAILED = "BLOCKED_CHROME_WIN32_DIALOG_SUBMIT_FAILED"
BLOCKED_ATTACHMENT_NOT_VERIFIED = "BLOCKED_CHROME_WIN32_DIALOG_ATTACHMENT_NOT_VERIFIED"

DEFAULT_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_win32_dialog_filename_submit_no_send.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_win32_dialog_filename_submit_no_send.txt")
DEFAULT_DESKTOP_DIR = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"

CHROME_TITLE_TOKENS = ("chrome", "google chrome")
CHATGPT_TITLE_TOKENS = ("chatgpt", "openai", "patchops")
PICKER_TITLE_TOKENS = ("open", "upload", "choose", "select", "file")
FILE_NAME_CONTROL_ID = 1148
IDOK = 1
WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_COMMAND = 0x0111
VK_RETURN = 0x0D

user32 = ctypes.WinDLL("user32", use_last_error=True)
EnumChildProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetDlgItem.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetDlgItem.restype = wintypes.HWND
user32.SendMessageW.argtypes = [wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = wintypes.LPARAM
user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
user32.SetWindowTextW.restype = wintypes.BOOL
user32.EnumChildWindows.argtypes = [wintypes.HWND, EnumChildProc, wintypes.LPARAM]
user32.EnumChildWindows.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.PostMessageW.argtypes = [wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL


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


def validate_config(config_payload: Mapping[str, Any] | None) -> tuple[bool, str | None, str | None, tuple[str, ...]]:
    if not config_payload:
        return False, None, None, ("status target config is required",)
    status = config_payload.get("status_chat")
    if not isinstance(status, Mapping):
        return False, None, None, ("status_chat object is required",)
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
    return not issues, url_hash, target_hash, tuple(issues)


def is_child_of(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except ValueError:
        return False


def hwnd_class(hwnd: int) -> str:
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value or ""


def hwnd_text(hwnd: int, max_chars: int = 512) -> str:
    buf = ctypes.create_unicode_buffer(max_chars)
    user32.GetWindowTextW(hwnd, buf, max_chars)
    return buf.value or ""


def foreground_window_info() -> tuple[int, str, str]:
    hwnd = int(user32.GetForegroundWindow())
    return hwnd, hwnd_class(hwnd), hwnd_text(hwnd)


def foreground_looks_like_picker() -> bool:
    _hwnd, cls, title = foreground_window_info()
    lowered = title.lower()
    return cls == "#32770" or any(token in lowered for token in PICKER_TITLE_TOKENS)


def safe_window_title(window: Any) -> str | None:
    try:
        text = str(window.window_text() or "").strip()
        return text or None
    except Exception:
        return None


def enum_child_hwnds(parent: int) -> list[int]:
    children: list[int] = []

    @EnumChildProc
    def callback(hwnd: int, _lparam: int) -> bool:
        children.append(int(hwnd))
        return True

    user32.EnumChildWindows(parent, callback, 0)
    return children


def read_control_text(hwnd: int) -> str:
    length = int(user32.SendMessageW(hwnd, WM_GETTEXTLENGTH, 0, 0))
    size = max(length + 2, 512)
    buf = ctypes.create_unicode_buffer(size)
    user32.SendMessageW(hwnd, WM_GETTEXT, size, ctypes.addressof(buf))
    return buf.value or hwnd_text(hwnd, size)


def set_control_text(hwnd: int, value: str) -> bool:
    ok1 = bool(user32.SetWindowTextW(hwnd, value))
    ok2 = bool(user32.SendMessageW(hwnd, WM_SETTEXT, 0, ctypes.cast(ctypes.c_wchar_p(value), wintypes.LPARAM)))
    return ok1 or ok2


def candidate_filename_controls(dialog_hwnd: int) -> list[int]:
    candidates: list[int] = []
    direct = int(user32.GetDlgItem(dialog_hwnd, FILE_NAME_CONTROL_ID) or 0)
    if direct:
        candidates.append(direct)
    for hwnd in enum_child_hwnds(dialog_hwnd):
        cls = hwnd_class(hwnd).lower()
        if cls in {"edit", "combobox", "comboboxex32"}:
            if hwnd not in candidates:
                candidates.append(hwnd)
    return candidates


def write_dialog_filename(dialog_hwnd: int, full_path: str) -> tuple[bool, int, str | None, str | None, tuple[str, ...]]:
    candidates = candidate_filename_controls(dialog_hwnd)
    issues: list[str] = []
    for hwnd in candidates:
        cls = hwnd_class(hwnd)
        try:
            ok = set_control_text(hwnd, full_path)
            time.sleep(0.15)
            text = read_control_text(hwnd)
            reflected = full_path.lower() in text.lower() or Path(full_path).name.lower() in text.lower()
            if ok or reflected:
                return reflected or ok, len(candidates), cls, text[:260], tuple(issues)
            issues.append(f"candidate class={cls!r} did not accept text")
        except Exception as exc:
            issues.append(f"candidate class={cls!r} failed: {exc}")
    return False, len(candidates), None, None, tuple(issues)


def submit_dialog(dialog_hwnd: int) -> tuple[bool, str]:
    user32.SetForegroundWindow(dialog_hwnd)
    time.sleep(0.1)
    posted_down = bool(user32.PostMessageW(dialog_hwnd, WM_KEYDOWN, VK_RETURN, 0))
    posted_up = bool(user32.PostMessageW(dialog_hwnd, WM_KEYUP, VK_RETURN, 0))
    time.sleep(0.75)
    still_hwnd, still_cls, _title = foreground_window_info()
    if still_hwnd != dialog_hwnd or still_cls != "#32770":
        return True, "post_enter_closed_or_unfocused_dialog"
    command_ok = bool(user32.PostMessageW(dialog_hwnd, WM_COMMAND, IDOK, 0))
    time.sleep(0.75)
    return posted_down and posted_up or command_ok, "post_enter_then_idok_fallback" if command_ok else "post_enter_only"


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
    foreground_picker_hwnd_seen: bool
    foreground_picker_class: str | None
    foreground_picker_title_length: int | None
    dialog_filename_control_attempted: bool
    dialog_filename_candidate_count: int
    dialog_filename_control_class: str | None
    dialog_filename_value_reflected: bool
    full_path_written_to_picker: bool
    dialog_submit_attempted: bool
    dialog_submit_method: str | None
    picker_enter_pressed: bool
    enter_key_pressed_in_picker: bool
    open_button_clicked: bool
    clipboard_text_written: bool
    ctrl_v_pressed_in_picker: bool
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
        selected_action="upload_self_report_win32_dialog_filename_submit_no_send",
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
        foreground_picker_hwnd_seen=False,
        foreground_picker_class=None,
        foreground_picker_title_length=None,
        dialog_filename_control_attempted=False,
        dialog_filename_candidate_count=0,
        dialog_filename_control_class=None,
        dialog_filename_value_reflected=False,
        full_path_written_to_picker=False,
        dialog_submit_attempted=False,
        dialog_submit_method=None,
        picker_enter_pressed=False,
        enter_key_pressed_in_picker=False,
        open_button_clicked=False,
        clipboard_text_written=False,
        ctrl_v_pressed_in_picker=False,
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

        dialog_hwnd, fg_class, fg_title = foreground_window_info()
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
            foreground_picker_hwnd_seen=bool(dialog_hwnd),
            foreground_picker_class=fg_class,
            foreground_picker_title_length=len(fg_title),
            before_attachment_count=len(before),
            selected_target_title_hash=sha256_text(title or "") if title else None,
            selected_target_title_length=len(title) if title else None,
        )
        if not fg_ready:
            return make_result(result_label=BLOCKED_PICKER_NOT_FOREGROUND, issues=(f"foreground file picker not detected; foreground_hwnd={dialog_hwnd}; foreground_class={fg_class!r}; foreground_title_length={len(fg_title)}",), **base)

        full_path = str(report_path.resolve(strict=False))
        wrote, candidate_count, control_class, reflected_value, write_issues = write_dialog_filename(dialog_hwnd, full_path)
        if not wrote:
            return make_result(
                result_label=BLOCKED_DIALOG_FILENAME_WRITE_FAILED,
                dialog_filename_control_attempted=True,
                dialog_filename_candidate_count=candidate_count,
                dialog_filename_control_class=control_class,
                issues=("failed to write full path into native dialog filename field", *write_issues),
                **base,
            )

        submitted, method = submit_dialog(dialog_hwnd)
        if not submitted:
            return make_result(
                result_label=BLOCKED_DIALOG_SUBMIT_FAILED,
                dialog_filename_control_attempted=True,
                dialog_filename_candidate_count=candidate_count,
                dialog_filename_control_class=control_class,
                dialog_filename_value_reflected=bool(reflected_value),
                full_path_written_to_picker=True,
                dialog_submit_attempted=True,
                dialog_submit_method=method,
                issues=("failed to submit native dialog after filename write",),
                **base,
            )

        verified, before_count, after_count = self._wait_for_new_attachment(window, report_path, before)
        after_write = dict(
            dialog_filename_control_attempted=True,
            dialog_filename_candidate_count=candidate_count,
            dialog_filename_control_class=control_class,
            dialog_filename_value_reflected=bool(reflected_value),
            full_path_written_to_picker=True,
            dialog_submit_attempted=True,
            dialog_submit_method=method,
            picker_enter_pressed=True,
            enter_key_pressed_in_picker=True,
            file_upload_attempted=True,
        )
        if not verified:
            return make_result(
                result_label=BLOCKED_ATTACHMENT_NOT_VERIFIED,
                before_attachment_count=before_count,
                after_attachment_count=after_count,
                issues=(f"new visible attachment was not verified after Win32 dialog filename write and submit; before_matches={before_count}; after_matches={after_count}",),
                **after_write,
                **{key: value for key, value in base.items() if key not in {"before_attachment_count"}},
            )
        return make_result(
            ok=True,
            result_label=PASS_LABEL,
            attachment_verified=True,
            operator_report_attached_to_composer=True,
            before_attachment_count=before_count,
            after_attachment_count=after_count,
            issues=(),
            **after_write,
            **{key: value for key, value in base.items() if key not in {"before_attachment_count"}},
        )


def run_smoke(*, config_payload: Mapping[str, Any] | None, provider: str, live_browser: bool, confirmation_text: str | None, self_report_path: str | None, expected_sha256: str | None, desktop_dir: Path) -> SmokeResult:
    config_ok, url_hash, target_hash, config_issues = validate_config(config_payload)
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
        return make_result(ok=True, result_label=PASS_LABEL, confirmation_matched=True, desktop_directory=str(desktop_dir), self_report_path=str(report), self_report_filename=report.name, self_report_sha256=computed, computed_self_report_sha256=computed, existing_chrome_used=True, chrome_target_ready=True, chrome_target_focused=True, slash_key_pressed=True, upload_command_enter_pressed=True, foreground_picker_ready=True, foreground_picker_hwnd_seen=True, foreground_picker_class="#32770", foreground_picker_title_length=4, dialog_filename_control_attempted=True, dialog_filename_candidate_count=2, dialog_filename_control_class="ComboBoxEx32", dialog_filename_value_reflected=True, full_path_written_to_picker=True, dialog_submit_attempted=True, dialog_submit_method="post_enter_closed_or_unfocused_dialog", picker_enter_pressed=True, enter_key_pressed_in_picker=True, attachment_verified=True, before_attachment_count=0, after_attachment_count=1, operator_report_attached_to_composer=True, browser_action_performed=True, file_upload_attempted=True, issues=(), provider=provider)
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
        "purpose: write full Desktop path into native Windows picker by Win32 dialog filename control and submit, no Send",
        f"created_at: {datetime.now(timezone.utc).isoformat()}",
        "selected_action: upload_self_report_win32_dialog_filename_submit_no_send",
        "browser_lane: chrome",
        "manual_sequence: existing_chrome_loaded__slash__enter__win32_dialog_filename_full_path__enter_or_idok",
        f"expected_result_label: {PASS_LABEL}",
        "operator_report_uploaded: false",
        "chatgpt_submit_performed: false",
        "send_button_pressed: false",
        "chrome_open_invoked: false",
        "mouse_clicks_used: false",
        "clipboard_text_written: false",
        "ctrl_v_pressed_in_picker: false",
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
    parser = argparse.ArgumentParser(description="Existing Chrome target, slash+Enter, Win32 set native dialog filename to full path, submit, no Send")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--desktop-dir", default=str(DEFAULT_DESKTOP_DIR))
    parser.add_argument("--self-report-filename", default="pseudo_self_report_upload_no_send_repair_16_win32_dialog_filename_submit_self_report.txt")
    parser.add_argument("--provider", choices=("pywinauto", "fake-ready"), default="pywinauto")
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