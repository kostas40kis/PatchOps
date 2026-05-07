from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

PATCH_NAME = "pseudo_self_report_upload_no_send_repair_09_slash_enter_enter"
CONFIRM_CHROME_SLASH_ENTER_ENTER_SELF_REPORT_UPLOAD_NO_SEND = "PATCHOPS_CONFIRM_CHROME_SLASH_ENTER_ENTER_SELF_REPORT_UPLOAD_NO_SEND"
CONFIRM_CHROME_SLASH_PICKER_SELF_REPORT_UPLOAD_NO_SEND = CONFIRM_CHROME_SLASH_ENTER_ENTER_SELF_REPORT_UPLOAD_NO_SEND
CONFIRM_CHROME_SLASH_ENTER_ENTER_SELF_REPORT_UPLOAD_NO_SEND = CONFIRM_CHROME_SLASH_ENTER_ENTER_SELF_REPORT_UPLOAD_NO_SEND
PASS_CHROME_SELF_REPORT_SLASH_ENTER_ENTER_ATTACHED_NO_SEND = "PASS_CHROME_SELF_REPORT_SLASH_ENTER_ENTER_ATTACHED_NO_SEND"
PASS_CHROME_SELF_REPORT_SLASH_PICKER_ATTACHED_NO_SEND = PASS_CHROME_SELF_REPORT_SLASH_ENTER_ENTER_ATTACHED_NO_SEND
PASS_CHROME_SELF_REPORT_SLASH_ENTER_ENTER_ATTACHED_NO_SEND = PASS_CHROME_SELF_REPORT_SLASH_ENTER_ENTER_ATTACHED_NO_SEND
BLOCKED_CHROME_SLASH_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_SLASH_CONFIRMATION_REQUIRED"
BLOCKED_CHROME_SLASH_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_SLASH_CONFIRMATION_MISMATCH"
BLOCKED_CHROME_SLASH_LIVE_BROWSER_REQUIRED = "BLOCKED_CHROME_SLASH_LIVE_BROWSER_REQUIRED"
BLOCKED_CHROME_SLASH_CONFIG_INVALID = "BLOCKED_CHROME_SLASH_CONFIG_INVALID"
BLOCKED_CHROME_SLASH_REPORT_MISSING = "BLOCKED_CHROME_SLASH_REPORT_MISSING"
BLOCKED_CHROME_SLASH_REPORT_HASH_MISMATCH = "BLOCKED_CHROME_SLASH_REPORT_HASH_MISMATCH"
BLOCKED_CHROME_SLASH_TARGET_NOT_READY = "BLOCKED_CHROME_SLASH_TARGET_NOT_READY"
BLOCKED_CHROME_SLASH_PICKER_NOT_OPENED = "BLOCKED_CHROME_SLASH_PICKER_NOT_OPENED"
BLOCKED_CHROME_SLASH_PICKER_AMBIGUOUS = "BLOCKED_CHROME_SLASH_PICKER_AMBIGUOUS"
BLOCKED_CHROME_SLASH_PATH_WRITE_FAILED = "BLOCKED_CHROME_SLASH_PATH_WRITE_FAILED"
BLOCKED_CHROME_SLASH_OPEN_CLICK_FAILED = "BLOCKED_CHROME_SLASH_OPEN_CLICK_FAILED"
BLOCKED_CHROME_SLASH_ATTACHMENT_NOT_VERIFIED = "BLOCKED_CHROME_SLASH_ATTACHMENT_NOT_VERIFIED"
BLOCKED_SEND_RISK = "BLOCKED_SEND_RISK"

DEFAULT_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_slash_enter_enter_upload_no_send.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_slash_enter_enter_upload_no_send.txt")

CHROME_TITLE_TOKENS = ("chrome", "google chrome")
CHATGPT_TITLE_TOKENS = ("chatgpt", "openai", "patchops")
PICKER_TITLE_TOKENS = ("open", "upload", "choose", "select", "file")
SAFE_SHORTCUTS_USED = ("/", "ENTER_FOR_UPLOAD_COMMAND_ONLY", "SECOND_ENTER_FOR_UPLOAD_COMMAND_ONLY_IF_NEEDED")
FORBIDDEN_SHORTCUTS_USED: tuple[str, ...] = ()


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


@dataclass(frozen=True)
class SlashPickerProbe:
    chrome_target_ready: bool
    chrome_target_focused: bool
    safe_focus_click_performed: bool
    slash_key_pressed: bool
    upload_command_enter_pressed: bool
    picker_opened: bool
    picker_count: int
    path_written: bool
    open_button_clicked: bool
    picker_closed_after_open: bool
    attachment_verified: bool
    before_attachment_count: int
    after_attachment_count: int
    selected_window_title: str | None
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class SlashPickerSafety:
    browser_action_performed: bool = False
    safe_focus_click_performed: bool = False
    slash_key_pressed: bool = False
    upload_command_enter_pressed: bool = False
    enter_key_pressed_in_chat_composer: bool = False
    enter_key_pressed_in_picker: bool = False
    file_picker_used: bool = False
    file_path_written: bool = False
    open_button_clicked: bool = False
    file_upload_attempted: bool = False
    operator_report_attached_to_composer: bool = False
    operator_report_uploaded: bool = False
    chatgpt_submit_performed: bool = False
    status_message_posted: bool = False
    send_button_pressed: bool = False
    raw_conversation_text_available: bool = False
    selenium_used: bool = False
    webdriver_used: bool = False
    browser_dom_automation_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False


@dataclass(frozen=True)
class SlashPickerResult:
    ok: bool
    result_label: str
    patch_name: str
    selected_action: str
    browser_lane: str
    live_browser: bool
    stop_before_send: bool
    confirmation_text_supplied: str | None
    confirmation_matched: bool
    config_path: str
    status_chat_configured: bool
    status_chat_url_hash_or_redacted: str | None
    target_url_sha256: str | None
    self_report_path: str | None
    self_report_sha256: str | None
    computed_self_report_sha256: str | None
    chrome_target_ready: bool
    chrome_target_focused: bool
    keyboard_shortcuts_used: tuple[str, ...]
    forbidden_keyboard_shortcuts_used: tuple[str, ...]
    safe_focus_click_performed: bool
    slash_key_pressed: bool
    upload_command_enter_pressed: bool
    enter_key_pressed_in_chat_composer: bool
    enter_key_pressed_in_picker: bool
    picker_opened: bool
    picker_count: int
    path_written: bool
    open_button_clicked: bool
    picker_closed_after_open: bool
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
    safety: SlashPickerSafety = field(default_factory=SlashPickerSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        return payload


class SlashPickerAdapter(Protocol):
    provider_name: str

    def attach_via_slash_picker(self, report_path: Path) -> SlashPickerProbe:
        ...


class FakeSlashPickerAdapter:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.provider_name = f"fake-{mode}"

    def attach_via_slash_picker(self, report_path: Path) -> SlashPickerProbe:
        title = "PatchOps - ChatGPT - Google Chrome"
        if self.mode == "no-target":
            return SlashPickerProbe(False, False, False, False, False, False, 0, False, False, False, False, 0, 0, None, ("fake target missing",))
        if self.mode == "no-picker":
            return SlashPickerProbe(True, True, True, True, True, False, 0, False, False, False, False, 0, 0, title, ("fake picker missing",))
        if self.mode == "ambiguous-picker":
            return SlashPickerProbe(True, True, True, True, True, True, 2, False, False, False, False, 0, 0, title, ("fake ambiguous picker",))
        if self.mode == "path-failed":
            return SlashPickerProbe(True, True, True, True, True, True, 1, False, False, False, False, 0, 0, title, ("fake path write failed",))
        if self.mode == "open-failed":
            return SlashPickerProbe(True, True, True, True, True, True, 1, True, False, False, False, 0, 0, title, ("fake open click failed",))
        if self.mode == "not-verified":
            return SlashPickerProbe(True, True, True, True, True, True, 1, True, True, True, False, 0, 0, title, ("fake attachment not verified",))
        return SlashPickerProbe(True, True, True, True, True, True, 1, True, True, True, True, 0, 1, title, ())


class PywinautoSlashPickerAdapter:
    provider_name = "pywinauto"

    def __init__(self, *, settle_seconds: float = 0.65, picker_timeout_seconds: float = 10.0, attach_timeout_seconds: float = 20.0) -> None:
        self.settle_seconds = settle_seconds
        self.picker_timeout_seconds = picker_timeout_seconds
        self.attach_timeout_seconds = attach_timeout_seconds

    def _desktop(self) -> Any:
        try:
            from pywinauto import Desktop  # type: ignore
        except Exception as exc:
            raise RuntimeError(f"pywinauto is required for live Chrome slash picker upload: {exc}") from exc
        return Desktop(backend="uia")

    def _keyboard(self) -> Any:
        try:
            from pywinauto import keyboard  # type: ignore
        except Exception as exc:
            raise RuntimeError(f"pywinauto keyboard is required for live Chrome slash picker upload: {exc}") from exc
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
        if len(matches) != 1:
            return None, (f"expected exactly one visible Chrome ChatGPT/PatchOps target; found {len(matches)}",)
        return matches[0], ()

    def _element_rect_tuple(self, element: Any) -> tuple[int, int, int, int] | None:
        try:
            rect = element.rectangle()
            return (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))
        except Exception:
            return None

    def _safe_focus_click(self, window: Any) -> bool:
        rect = self._element_rect_tuple(window)
        if rect is None:
            return False
        left, top, right, bottom = rect
        x = int(left + (right - left) * 0.50)
        y = int(top + (bottom - top) * 0.34)
        try:
            window.click_input(coords=(x - left, y - top))
            time.sleep(self.settle_seconds)
            return True
        except Exception:
            return False

    def _picker_windows_once(self) -> list[Any]:
        try:
            windows = list(self._desktop().windows())
        except Exception:
            return []
        pickers: list[Any] = []
        for window in windows:
            title = (_safe_window_title(window) or "").lower()
            try:
                cls = str(window.element_info.class_name or "").lower()
                visible = bool(window.is_visible())
            except Exception:
                continue
            if not visible:
                continue
            if "#32770" in cls or any(token in title for token in PICKER_TITLE_TOKENS):
                if self._path_edit(window) is not None and self._open_button(window) is not None:
                    pickers.append(window)
        return pickers

    def _wait_for_picker(self) -> list[Any]:
        deadline = time.monotonic() + self.picker_timeout_seconds
        latest: list[Any] = []
        while time.monotonic() < deadline:
            latest = self._picker_windows_once()
            if latest:
                return latest
            time.sleep(0.25)
        return latest

    def _path_edit(self, picker: Any) -> Any | None:
        try:
            descendants = list(picker.descendants())
        except Exception:
            return None
        scored: list[Any] = []
        for element in descendants:
            try:
                control_type = str(element.element_info.control_type or "").lower()
                enabled = bool(element.is_enabled())
                visible = bool(element.is_visible())
                name = str(element.window_text() or element.element_info.name or "").lower()
            except Exception:
                continue
            if not enabled or not visible:
                continue
            if control_type == "edit" or ("file name" in name and control_type in {"edit", "combobox"}):
                scored.append(element)
        return scored[0] if scored else None

    def _open_button(self, picker: Any) -> Any | None:
        try:
            descendants = list(picker.descendants())
        except Exception:
            return None
        for element in descendants:
            try:
                control_type = str(element.element_info.control_type or "").lower()
                enabled = bool(element.is_enabled())
                visible = bool(element.is_visible())
                name = str(element.window_text() or element.element_info.name or "").strip().lower()
            except Exception:
                continue
            if not enabled or not visible:
                continue
            if control_type == "button" and name in {"open", "&open"}:
                return element
        for element in descendants:
            try:
                control_type = str(element.element_info.control_type or "").lower()
                name = str(element.window_text() or element.element_info.name or "").strip().lower()
            except Exception:
                continue
            if control_type == "button" and "open" in name:
                return element
        return None

    def _visible_attachment_matches(self, window: Any, report_path: Path) -> set[tuple[str, tuple[int, int, int, int]]]:
        wanted = {report_path.name.lower(), report_path.stem.lower()}
        window_rect = self._element_rect_tuple(window)
        if window_rect is None:
            return set()
        wl, wt, wr, wb = window_rect
        lower_threshold = wt + int(max(1, wb - wt) * 0.45)
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
            if rect is None:
                continue
            if rect[3] < lower_threshold:
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

    def attach_via_slash_picker(self, report_path: Path) -> SlashPickerProbe:
        window, issues = self._target_window()
        if window is None:
            return SlashPickerProbe(False, False, False, False, False, False, 0, False, False, False, False, 0, 0, None, issues)
        title = _safe_window_title(window)
        try:
            window.set_focus()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return SlashPickerProbe(True, False, False, False, False, False, 0, False, False, False, False, 0, 0, title, (f"Chrome focus failed: {exc}",))
        safe_clicked = self._safe_focus_click(window)
        if not safe_clicked:
            return SlashPickerProbe(True, True, False, False, False, False, 0, False, False, False, False, 0, 0, title, ("safe focus click failed",))

        before = self._visible_attachment_matches(window, report_path)
        second_enter_used = False
        try:
            keyboard = self._keyboard()
            keyboard.send_keys("/", pause=0.05)
            time.sleep(self.settle_seconds)
            keyboard.send_keys("{ENTER}", pause=0.05)
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return SlashPickerProbe(True, True, True, False, False, False, 0, False, False, False, False, len(before), len(before), title, (f"slash + first Enter picker trigger failed: {exc}",))

        pickers = self._wait_for_picker()
        if len(pickers) == 0:
            try:
                keyboard.send_keys("{ENTER}", pause=0.05)
                second_enter_used = True
                time.sleep(self.settle_seconds)
            except Exception as exc:
                return SlashPickerProbe(True, True, True, True, True, False, 0, False, False, False, False, len(before), len(before), title, (f"slash + second Enter picker trigger failed: {exc}",))
            pickers = self._wait_for_picker()
        if len(pickers) == 0:
            return SlashPickerProbe(True, True, True, True, True, False, 0, False, False, False, False, len(before), len(before), title, ("native file picker did not open after slash + Enter + Enter-if-needed",))
        if len(pickers) != 1:
            return SlashPickerProbe(True, True, True, True, True, True, len(pickers), False, False, False, False, len(before), len(before), title, (f"expected exactly one native file picker; found {len(pickers)}",))

        picker = pickers[0]
        edit = self._path_edit(picker)
        if edit is None:
            return SlashPickerProbe(True, True, True, True, True, True, 1, False, False, False, False, len(before), len(before), title, ("native file picker path edit was not found",))
        try:
            edit.set_edit_text(str(report_path.resolve(strict=True)))
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return SlashPickerProbe(True, True, True, True, True, True, 1, False, False, False, False, len(before), len(before), title, (f"file picker path write failed: {exc}",))

        button = self._open_button(picker)
        if button is None:
            return SlashPickerProbe(True, True, True, True, True, True, 1, True, False, False, False, len(before), len(before), title, ("native file picker Open button was not found",))
        try:
            button.click_input()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return SlashPickerProbe(True, True, True, True, True, True, 1, True, False, False, False, len(before), len(before), title, (f"native file picker Open click failed: {exc}",))

        closed = len(self._picker_windows_once()) == 0
        verified, before_count, after_count = self._wait_for_new_attachment(window, report_path, before)
        if not verified:
            return SlashPickerProbe(True, True, True, True, True, True, 1, True, True, closed, False, before_count, after_count, title, (f"new visible attachment was not verified after picker Open; before_matches={before_count}; after_matches={after_count}",))
        return SlashPickerProbe(True, True, True, True, True, True, 1, True, True, closed, True, before_count, after_count, title, ())


def _safe_window_title(window: Any) -> str | None:
    try:
        text = str(window.window_text() or "").strip()
        return text or None
    except Exception:
        return None


def build_adapter(provider: str) -> SlashPickerAdapter:
    if provider.startswith("fake-"):
        return FakeSlashPickerAdapter(provider.removeprefix("fake-"))
    if provider == "pywinauto":
        return PywinautoSlashPickerAdapter()
    raise ValueError(f"Unknown provider: {provider}")


def make_result(
    *,
    ok: bool,
    result_label: str,
    config_path: Path,
    status_chat_configured: bool,
    status_chat_url_hash_or_redacted: str | None,
    target_url_sha256: str | None,
    live_browser: bool,
    confirmation_text: str | None,
    confirmation_matched: bool,
    report_path: Path | None,
    report_sha256: str | None,
    computed_report_sha256: str | None,
    probe: SlashPickerProbe | None,
    provider: str,
    issues: Sequence[str],
) -> SlashPickerResult:
    title = probe.selected_window_title if probe else None
    safety = SlashPickerSafety(
        browser_action_performed=bool(probe and (probe.chrome_target_focused or probe.slash_key_pressed or probe.open_button_clicked)),
        safe_focus_click_performed=bool(probe and probe.safe_focus_click_performed),
        slash_key_pressed=bool(probe and probe.slash_key_pressed),
        upload_command_enter_pressed=bool(probe and probe.upload_command_enter_pressed),
        enter_key_pressed_in_chat_composer=False,
        enter_key_pressed_in_picker=False,
        file_picker_used=bool(probe and probe.picker_opened),
        file_path_written=bool(probe and probe.path_written),
        open_button_clicked=bool(probe and probe.open_button_clicked),
        file_upload_attempted=bool(probe and probe.open_button_clicked),
        operator_report_attached_to_composer=bool(probe and probe.attachment_verified),
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
        conversation_text_logged=False,
        random_page_click_performed=False,
    )
    return SlashPickerResult(
        ok=ok,
        result_label=result_label,
        patch_name=PATCH_NAME,
        selected_action="upload_self_report_slash_enter_enter_no_send",
        browser_lane="chrome",
        live_browser=live_browser,
        stop_before_send=True,
        confirmation_text_supplied=confirmation_text,
        confirmation_matched=confirmation_matched,
        config_path=str(config_path),
        status_chat_configured=status_chat_configured,
        status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
        target_url_sha256=target_url_sha256,
        self_report_path=str(report_path) if report_path else None,
        self_report_sha256=report_sha256,
        computed_self_report_sha256=computed_report_sha256,
        chrome_target_ready=bool(probe and probe.chrome_target_ready),
        chrome_target_focused=bool(probe and probe.chrome_target_focused),
        keyboard_shortcuts_used=SAFE_SHORTCUTS_USED if probe and probe.slash_key_pressed else (),
        forbidden_keyboard_shortcuts_used=FORBIDDEN_SHORTCUTS_USED,
        safe_focus_click_performed=safety.safe_focus_click_performed,
        slash_key_pressed=safety.slash_key_pressed,
        upload_command_enter_pressed=safety.upload_command_enter_pressed,
        enter_key_pressed_in_chat_composer=False,
        enter_key_pressed_in_picker=False,
        picker_opened=bool(probe and probe.picker_opened),
        picker_count=probe.picker_count if probe else 0,
        path_written=safety.file_path_written,
        open_button_clicked=safety.open_button_clicked,
        picker_closed_after_open=bool(probe and probe.picker_closed_after_open),
        attachment_verified=bool(probe and probe.attachment_verified),
        before_attachment_count=probe.before_attachment_count if probe else 0,
        after_attachment_count=probe.after_attachment_count if probe else 0,
        operator_report_attached_to_composer=safety.operator_report_attached_to_composer,
        browser_action_performed=safety.browser_action_performed,
        file_upload_attempted=safety.file_upload_attempted,
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
        safety=safety,
    )


def run_slash_picker_upload_no_send(
    *,
    config_payload: Mapping[str, Any] | None,
    config_path: Path = DEFAULT_CONFIG_PATH,
    provider: str = "fake-ready",
    live_browser: bool,
    confirmation_text: str | None,
    self_report_path: str | None,
    expected_self_report_sha256: str | None = None,
) -> SlashPickerResult:
    config_ok, url_hash, target_hash, config_issues = validate_config(config_payload)
    confirmation_matched = confirmation_text == CONFIRM_CHROME_SLASH_ENTER_ENTER_SELF_REPORT_UPLOAD_NO_SEND
    empty_probe = SlashPickerProbe(False, False, False, False, False, False, 0, False, False, False, False, 0, 0, None, ())
    if not config_ok:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SLASH_CONFIG_INVALID, config_path=config_path, status_chat_configured=False, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=live_browser, confirmation_text=confirmation_text, confirmation_matched=confirmation_matched, report_path=Path(self_report_path) if self_report_path else None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=empty_probe, provider=provider, issues=config_issues)
    if confirmation_text is None:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SLASH_CONFIRMATION_REQUIRED, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=live_browser, confirmation_text=None, confirmation_matched=False, report_path=Path(self_report_path) if self_report_path else None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=empty_probe, provider=provider, issues=("live slash picker confirmation is required",))
    if not confirmation_matched:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SLASH_CONFIRMATION_MISMATCH, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=live_browser, confirmation_text=confirmation_text, confirmation_matched=False, report_path=Path(self_report_path) if self_report_path else None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=empty_probe, provider=provider, issues=(f"confirmation must exactly match {CONFIRM_CHROME_SLASH_ENTER_ENTER_SELF_REPORT_UPLOAD_NO_SEND}",))
    if not live_browser:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SLASH_LIVE_BROWSER_REQUIRED, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=False, confirmation_text=confirmation_text, confirmation_matched=True, report_path=Path(self_report_path) if self_report_path else None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=empty_probe, provider=provider, issues=("--live-browser is required",))
    if not self_report_path:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SLASH_REPORT_MISSING, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=empty_probe, provider=provider, issues=("self report path is required",))
    report_path = Path(self_report_path)
    if not report_path.exists() or not report_path.is_file():
        return make_result(ok=False, result_label=BLOCKED_CHROME_SLASH_REPORT_MISSING, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=report_path, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=empty_probe, provider=provider, issues=(f"self report not found: {report_path}",))
    computed_hash = sha256_file(report_path)
    if expected_self_report_sha256 and expected_self_report_sha256 != computed_hash:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SLASH_REPORT_HASH_MISMATCH, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=report_path, report_sha256=expected_self_report_sha256, computed_report_sha256=computed_hash, probe=empty_probe, provider=provider, issues=("self report hash mismatch",))

    try:
        adapter = build_adapter(provider)
        probe = adapter.attach_via_slash_picker(report_path)
    except Exception as exc:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SLASH_TARGET_NOT_READY, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=report_path, report_sha256=computed_hash, computed_report_sha256=computed_hash, probe=empty_probe, provider=provider, issues=(str(exc),))

    if not probe.chrome_target_ready or not probe.chrome_target_focused:
        label = BLOCKED_CHROME_SLASH_TARGET_NOT_READY
    elif not probe.picker_opened:
        label = BLOCKED_CHROME_SLASH_PICKER_NOT_OPENED
    elif probe.picker_count != 1:
        label = BLOCKED_CHROME_SLASH_PICKER_AMBIGUOUS
    elif not probe.path_written:
        label = BLOCKED_CHROME_SLASH_PATH_WRITE_FAILED
    elif not probe.open_button_clicked:
        label = BLOCKED_CHROME_SLASH_OPEN_CLICK_FAILED
    elif not probe.attachment_verified:
        label = BLOCKED_CHROME_SLASH_ATTACHMENT_NOT_VERIFIED
    else:
        label = PASS_CHROME_SELF_REPORT_SLASH_ENTER_ENTER_ATTACHED_NO_SEND

    return make_result(ok=label == PASS_CHROME_SELF_REPORT_SLASH_ENTER_ENTER_ATTACHED_NO_SEND, result_label=label, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=report_path, report_sha256=computed_hash, computed_report_sha256=computed_hash, probe=probe, provider=adapter.provider_name, issues=probe.issues)


def render_text(result: SlashPickerResult) -> str:
    lines = [
        f"result_label: {result.result_label}",
        f"ok: {str(result.ok).lower()}",
        f"patch_name: {result.patch_name}",
        f"selected_action: {result.selected_action}",
        f"browser_lane: {result.browser_lane}",
        f"live_browser: {str(result.live_browser).lower()}",
        f"stop_before_send: {str(result.stop_before_send).lower()}",
        f"confirmation_matched: {str(result.confirmation_matched).lower()}",
        f"self_report_path: {result.self_report_path}",
        f"self_report_sha256: {result.self_report_sha256}",
        f"computed_self_report_sha256: {result.computed_self_report_sha256}",
        f"chrome_target_ready: {str(result.chrome_target_ready).lower()}",
        f"chrome_target_focused: {str(result.chrome_target_focused).lower()}",
        f"keyboard_shortcuts_used: {','.join(result.keyboard_shortcuts_used) if result.keyboard_shortcuts_used else 'none'}",
        f"forbidden_keyboard_shortcuts_used: {','.join(result.forbidden_keyboard_shortcuts_used) if result.forbidden_keyboard_shortcuts_used else 'none'}",
        f"safe_focus_click_performed: {str(result.safe_focus_click_performed).lower()}",
        f"slash_key_pressed: {str(result.slash_key_pressed).lower()}",
        f"upload_command_enter_pressed: {str(result.upload_command_enter_pressed).lower()}",
        f"enter_key_pressed_in_chat_composer: {str(result.enter_key_pressed_in_chat_composer).lower()}",
        f"enter_key_pressed_in_picker: {str(result.enter_key_pressed_in_picker).lower()}",
        f"picker_opened: {str(result.picker_opened).lower()}",
        f"picker_count: {result.picker_count}",
        f"path_written: {str(result.path_written).lower()}",
        f"open_button_clicked: {str(result.open_button_clicked).lower()}",
        f"picker_closed_after_open: {str(result.picker_closed_after_open).lower()}",
        f"attachment_verified: {str(result.attachment_verified).lower()}",
        f"before_attachment_count: {result.before_attachment_count}",
        f"after_attachment_count: {result.after_attachment_count}",
        f"operator_report_attached_to_composer: {str(result.operator_report_attached_to_composer).lower()}",
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


def write_evidence(result: SlashPickerResult, *, json_output_path: Path = DEFAULT_JSON_OUTPUT_PATH, txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_text(result), encoding="utf-8")
    return json_output_path, txt_output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Attach a self-report file in Chrome via slash picker path without Send")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-no-picker", "fake-ambiguous-picker", "fake-path-failed", "fake-open-failed", "fake-not-verified", "pywinauto"), default="fake-ready")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--self-report-path", required=True)
    parser.add_argument("--self-report-sha256", default=None)
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config_path)
    config_payload = load_json_object(config_path) if config_path.exists() else None
    result = run_slash_picker_upload_no_send(
        config_payload=config_payload,
        config_path=config_path,
        provider=args.provider,
        live_browser=bool(args.live_browser),
        confirmation_text=args.confirm_live_browser_text,
        self_report_path=args.self_report_path,
        expected_self_report_sha256=args.self_report_sha256,
    )
    write_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))
    if args.json:
        print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(result), end="")
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())