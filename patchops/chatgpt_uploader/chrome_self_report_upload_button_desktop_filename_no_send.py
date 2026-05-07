from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

from patchops.chatgpt_uploader.chrome_self_report_desktop_filename_upload_no_send import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_DESKTOP_DIR,
    PywinautoDesktopFilenameAdapter,
    _safe_window_title,
    is_child_of,
    load_json_object,
    normalize_bool,
    sha256_file,
    sha256_text,
    validate_config,
)

PATCH_NAME = "pseudo_self_report_upload_no_send_repair_11_upload_button_desktop_filename"
CONFIRM_CHROME_UPLOAD_BUTTON_DESKTOP_FILENAME_NO_SEND = "PATCHOPS_CONFIRM_CHROME_UPLOAD_BUTTON_DESKTOP_FILENAME_NO_SEND"
PASS_CHROME_SELF_REPORT_UPLOAD_BUTTON_DESKTOP_FILENAME_ATTACHED_NO_SEND = "PASS_CHROME_SELF_REPORT_UPLOAD_BUTTON_DESKTOP_FILENAME_ATTACHED_NO_SEND"
BLOCKED_CHROME_UPLOAD_BUTTON_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_UPLOAD_BUTTON_CONFIRMATION_REQUIRED"
BLOCKED_CHROME_UPLOAD_BUTTON_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_UPLOAD_BUTTON_CONFIRMATION_MISMATCH"
BLOCKED_CHROME_UPLOAD_BUTTON_LIVE_BROWSER_REQUIRED = "BLOCKED_CHROME_UPLOAD_BUTTON_LIVE_BROWSER_REQUIRED"
BLOCKED_CHROME_UPLOAD_BUTTON_CONFIG_INVALID = "BLOCKED_CHROME_UPLOAD_BUTTON_CONFIG_INVALID"
BLOCKED_CHROME_UPLOAD_BUTTON_REPORT_MISSING = "BLOCKED_CHROME_UPLOAD_BUTTON_REPORT_MISSING"
BLOCKED_CHROME_UPLOAD_BUTTON_REPORT_NOT_ON_DESKTOP = "BLOCKED_CHROME_UPLOAD_BUTTON_REPORT_NOT_ON_DESKTOP"
BLOCKED_CHROME_UPLOAD_BUTTON_REPORT_HASH_MISMATCH = "BLOCKED_CHROME_UPLOAD_BUTTON_REPORT_HASH_MISMATCH"
BLOCKED_CHROME_UPLOAD_BUTTON_TARGET_NOT_READY = "BLOCKED_CHROME_UPLOAD_BUTTON_TARGET_NOT_READY"
BLOCKED_CHROME_UPLOAD_BUTTON_CONTROL_NOT_FOUND = "BLOCKED_CHROME_UPLOAD_BUTTON_CONTROL_NOT_FOUND"
BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_NOT_OPENED = "BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_NOT_OPENED"
BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_AMBIGUOUS = "BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_AMBIGUOUS"
BLOCKED_CHROME_UPLOAD_BUTTON_FILENAME_WRITE_FAILED = "BLOCKED_CHROME_UPLOAD_BUTTON_FILENAME_WRITE_FAILED"
BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_ENTER_FAILED = "BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_ENTER_FAILED"
BLOCKED_CHROME_UPLOAD_BUTTON_ATTACHMENT_NOT_VERIFIED = "BLOCKED_CHROME_UPLOAD_BUTTON_ATTACHMENT_NOT_VERIFIED"

DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_upload_button_desktop_filename_no_send.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_upload_button_desktop_filename_no_send.txt")

UPLOAD_BUTTON_TOKENS = (
    "attach",
    "attachment",
    "upload",
    "add files",
    "add file",
    "add photos",
    "photos and files",
    "paperclip",
    "file",
    "files",
)
UPLOAD_MENU_TOKENS = (
    "upload file",
    "upload files",
    "add file",
    "add files",
    "from computer",
    "choose file",
    "choose files",
    "photos and files",
)
BUTTON_CONTROL_TYPES = {"button", "splitbutton", "menuitem", "custom", "group", "hyperlink"}
SAFE_BROWSER_ACTIONS = ("UPLOAD_BUTTON_CLICK", "UPLOAD_MENU_ITEM_CLICK_IF_NEEDED", "ENTER_IN_NATIVE_FILE_PICKER_ONLY")
FORBIDDEN_SHORTCUTS_USED: tuple[str, ...] = ()


@dataclass(frozen=True)
class UploadButtonProbe:
    chrome_target_ready: bool
    chrome_target_focused: bool
    safe_focus_click_performed: bool
    upload_button_clicked: bool
    upload_button_candidate_count: int
    upload_menu_item_clicked: bool
    upload_menu_item_count: int
    picker_opened: bool
    picker_count: int
    desktop_directory: str | None
    filename_to_type: str | None
    filename_written: bool
    picker_enter_pressed: bool
    picker_closed_after_enter: bool
    attachment_verified: bool
    before_attachment_count: int
    after_attachment_count: int
    selected_window_title: str | None
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class UploadButtonResult:
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
    chrome_target_ready: bool
    chrome_target_focused: bool
    browser_actions_used: tuple[str, ...]
    forbidden_keyboard_shortcuts_used: tuple[str, ...]
    safe_focus_click_performed: bool
    upload_button_clicked: bool
    upload_button_candidate_count: int
    upload_menu_item_clicked: bool
    upload_menu_item_count: int
    slash_key_pressed: bool
    upload_command_enter_pressed: bool
    enter_key_pressed_in_chat_composer: bool
    enter_key_pressed_in_picker: bool
    picker_opened: bool
    picker_count: int
    filename_written: bool
    full_path_written_to_picker: bool
    open_button_clicked: bool
    picker_enter_pressed: bool
    picker_closed_after_enter: bool
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


class UploadButtonAdapter(Protocol):
    provider_name: str

    def attach_via_upload_button(self, report_path: Path, desktop_dir: Path) -> UploadButtonProbe:
        ...


class FakeUploadButtonAdapter:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.provider_name = f"fake-{mode}"

    def attach_via_upload_button(self, report_path: Path, desktop_dir: Path) -> UploadButtonProbe:
        title = "PatchOps - ChatGPT - Google Chrome"
        if self.mode == "no-target":
            return UploadButtonProbe(False, False, False, False, 0, False, 0, False, 0, str(desktop_dir), report_path.name, False, False, False, False, 0, 0, None, ("fake target missing",))
        if self.mode == "no-button":
            return UploadButtonProbe(True, True, True, False, 0, False, 0, False, 0, str(desktop_dir), report_path.name, False, False, False, False, 0, 0, title, ("fake upload button missing",))
        if self.mode == "no-picker":
            return UploadButtonProbe(True, True, True, True, 1, False, 0, False, 0, str(desktop_dir), report_path.name, False, False, False, False, 0, 0, title, ("fake picker missing",))
        if self.mode == "write-failed":
            return UploadButtonProbe(True, True, True, True, 1, False, 0, True, 1, str(desktop_dir), report_path.name, False, False, False, False, 0, 0, title, ("fake filename write failed",))
        if self.mode == "enter-failed":
            return UploadButtonProbe(True, True, True, True, 1, False, 0, True, 1, str(desktop_dir), report_path.name, True, False, False, False, 0, 0, title, ("fake picker enter failed",))
        if self.mode == "not-verified":
            return UploadButtonProbe(True, True, True, True, 1, False, 0, True, 1, str(desktop_dir), report_path.name, True, True, True, False, 0, 0, title, ("fake attachment not verified",))
        return UploadButtonProbe(True, True, True, True, 1, False, 0, True, 1, str(desktop_dir), report_path.name, True, True, True, True, 0, 1, title, ())


class PywinautoUploadButtonAdapter(PywinautoDesktopFilenameAdapter):
    provider_name = "pywinauto"

    def _element_name(self, element: Any) -> str:
        parts: list[str] = []
        for getter in (
            lambda: element.window_text(),
            lambda: element.element_info.name,
            lambda: element.element_info.automation_id,
            lambda: element.element_info.class_name,
        ):
            try:
                value = str(getter() or "").strip()
            except Exception:
                value = ""
            if value:
                parts.append(value)
        return " ".join(parts).strip()

    def _control_type(self, element: Any) -> str:
        try:
            return str(element.element_info.control_type or "").lower()
        except Exception:
            return ""

    def _is_visible_enabled(self, element: Any) -> bool:
        try:
            return bool(element.is_visible()) and bool(element.is_enabled())
        except Exception:
            return False

    def _upload_button_candidates(self, window: Any) -> list[Any]:
        try:
            descendants = list(window.descendants())
        except Exception:
            return []
        window_rect = self._element_rect_tuple(window)
        lower_threshold = None
        if window_rect:
            lower_threshold = window_rect[1] + int(max(1, window_rect[3] - window_rect[1]) * 0.45)
        found: list[tuple[int, int, Any]] = []
        seen_rects: set[tuple[int, int, int, int]] = set()
        for element in descendants:
            if not self._is_visible_enabled(element):
                continue
            control_type = self._control_type(element)
            if control_type not in BUTTON_CONTROL_TYPES:
                continue
            rect = self._element_rect_tuple(element)
            if rect is None or rect in seen_rects:
                continue
            name = self._element_name(element).lower()
            semantic = any(token in name for token in UPLOAD_BUTTON_TOKENS)
            position_ok = lower_threshold is not None and rect[3] >= lower_threshold and rect[0] <= window_rect[0] + int(max(1, window_rect[2] - window_rect[0]) * 0.35)  # type: ignore[index]
            if not semantic and not position_ok:
                continue
            seen_rects.add(rect)
            score = 0 if semantic else 10
            center_x = int((rect[0] + rect[2]) / 2)
            center_y = int((rect[1] + rect[3]) / 2)
            found.append((score + center_x, -center_y, element))
        found.sort(key=lambda item: (item[0], item[1]))
        return [item[2] for item in found]

    def _click_upload_button(self, window: Any) -> tuple[bool, int, tuple[str, ...]]:
        candidates = self._upload_button_candidates(window)
        if len(candidates) < 1:
            return False, 0, ("no visible upload/paperclip control candidate found",)
        chosen = candidates[0]
        try:
            chosen.click_input()
            time.sleep(self.settle_seconds)
            return True, len(candidates), ()
        except Exception as exc:
            return False, len(candidates), (f"upload/paperclip control click failed: {exc}",)

    def _upload_menu_candidates(self) -> list[Any]:
        try:
            windows = list(self._desktop().windows())
        except Exception:
            return []
        candidates: list[tuple[int, str, Any]] = []
        for window in windows:
            try:
                descendants = list(window.descendants())
            except Exception:
                descendants = []
            for element in descendants:
                if not self._is_visible_enabled(element):
                    continue
                name = self._element_name(element).lower()
                control_type = self._control_type(element)
                if control_type not in BUTTON_CONTROL_TYPES and control_type != "menuitem":
                    continue
                if not any(token in name for token in UPLOAD_MENU_TOKENS):
                    continue
                score = 0
                if "upload file" in name or "upload files" in name:
                    score -= 20
                if "from computer" in name:
                    score -= 10
                candidates.append((score, name, element))
        candidates.sort(key=lambda item: (item[0], item[1]))
        return [item[2] for item in candidates]

    def _click_upload_menu_if_present(self) -> tuple[bool, int, tuple[str, ...]]:
        candidates = self._upload_menu_candidates()
        if not candidates:
            return False, 0, ()
        try:
            candidates[0].click_input()
            time.sleep(self.settle_seconds)
            return True, len(candidates), ()
        except Exception as exc:
            return False, len(candidates), (f"upload menu item click failed: {exc}",)

    def attach_via_upload_button(self, report_path: Path, desktop_dir: Path) -> UploadButtonProbe:
        window, issues = self._target_window()
        if window is None:
            return UploadButtonProbe(False, False, False, False, 0, False, 0, False, 0, str(desktop_dir), report_path.name, False, False, False, False, 0, 0, None, issues)
        title = _safe_window_title(window)
        try:
            window.set_focus()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return UploadButtonProbe(True, False, False, False, 0, False, 0, False, 0, str(desktop_dir), report_path.name, False, False, False, False, 0, 0, title, (f"Chrome focus failed: {exc}",))
        safe_clicked = self._safe_focus_click(window)
        before = self._visible_attachment_matches(window, report_path)
        clicked, button_count, button_issues = self._click_upload_button(window)
        if button_issues:
            return UploadButtonProbe(True, True, safe_clicked, clicked, button_count, False, 0, False, 0, str(desktop_dir), report_path.name, False, False, False, False, len(before), len(before), title, button_issues)
        if not clicked:
            return UploadButtonProbe(True, True, safe_clicked, False, button_count, False, 0, False, 0, str(desktop_dir), report_path.name, False, False, False, False, len(before), len(before), title, ("upload/paperclip control was not clicked",))

        pickers = self._wait_for_picker()
        menu_clicked = False
        menu_count = 0
        if len(pickers) == 0:
            menu_clicked, menu_count, menu_issues = self._click_upload_menu_if_present()
            if menu_issues:
                return UploadButtonProbe(True, True, safe_clicked, True, button_count, menu_clicked, menu_count, False, 0, str(desktop_dir), report_path.name, False, False, False, False, len(before), len(before), title, menu_issues)
            if menu_clicked:
                pickers = self._wait_for_picker()

        if len(pickers) == 0:
            return UploadButtonProbe(True, True, safe_clicked, True, button_count, menu_clicked, menu_count, False, 0, str(desktop_dir), report_path.name, False, False, False, False, len(before), len(before), title, ("native file picker did not open after upload/paperclip control click",))
        if len(pickers) != 1:
            return UploadButtonProbe(True, True, safe_clicked, True, button_count, menu_clicked, menu_count, True, len(pickers), str(desktop_dir), report_path.name, False, False, False, False, len(before), len(before), title, (f"expected exactly one native file picker; found {len(pickers)}",))

        picker = pickers[0]
        edit = self._path_edit(picker)
        if edit is None:
            return UploadButtonProbe(True, True, safe_clicked, True, button_count, menu_clicked, menu_count, True, 1, str(desktop_dir), report_path.name, False, False, False, False, len(before), len(before), title, ("native file picker filename edit was not found",))
        try:
            edit.set_focus()
            time.sleep(0.1)
            edit.set_edit_text(report_path.name)
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return UploadButtonProbe(True, True, safe_clicked, True, button_count, menu_clicked, menu_count, True, 1, str(desktop_dir), report_path.name, False, False, False, False, len(before), len(before), title, (f"Desktop filename write failed: {exc}",))
        try:
            self._keyboard().send_keys("{ENTER}", pause=0.05)
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return UploadButtonProbe(True, True, safe_clicked, True, button_count, menu_clicked, menu_count, True, 1, str(desktop_dir), report_path.name, True, False, False, False, len(before), len(before), title, (f"native picker Enter failed after Desktop filename write: {exc}",))
        closed = len(self._picker_windows_once()) == 0
        verified, before_count, after_count = self._wait_for_new_attachment(window, report_path, before)
        if not verified:
            return UploadButtonProbe(True, True, safe_clicked, True, button_count, menu_clicked, menu_count, True, 1, str(desktop_dir), report_path.name, True, True, closed, False, before_count, after_count, title, (f"new visible attachment was not verified after upload button + Desktop filename + picker Enter; before_matches={before_count}; after_matches={after_count}",))
        return UploadButtonProbe(True, True, safe_clicked, True, button_count, menu_clicked, menu_count, True, 1, str(desktop_dir), report_path.name, True, True, closed, True, before_count, after_count, title, ())


def build_adapter(provider: str) -> UploadButtonAdapter:
    if provider.startswith("fake-"):
        return FakeUploadButtonAdapter(provider.removeprefix("fake-"))
    if provider == "pywinauto":
        return PywinautoUploadButtonAdapter()
    raise ValueError(f"Unknown provider: {provider}")


def make_result(*, ok: bool, result_label: str, config_path: Path, status_chat_configured: bool, url_hash: str | None, target_hash: str | None, live_browser: bool, confirmation_matched: bool, desktop_dir: Path | None, report_path: Path | None, expected_hash: str | None, computed_hash: str | None, probe: UploadButtonProbe | None, provider: str, issues: Sequence[str]) -> UploadButtonResult:
    title = probe.selected_window_title if probe else None
    return UploadButtonResult(
        ok=ok,
        result_label=result_label,
        patch_name=PATCH_NAME,
        selected_action="upload_self_report_upload_button_desktop_filename_no_send",
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
        chrome_target_ready=bool(probe and probe.chrome_target_ready),
        chrome_target_focused=bool(probe and probe.chrome_target_focused),
        browser_actions_used=SAFE_BROWSER_ACTIONS if probe and probe.upload_button_clicked else (),
        forbidden_keyboard_shortcuts_used=FORBIDDEN_SHORTCUTS_USED,
        safe_focus_click_performed=bool(probe and probe.safe_focus_click_performed),
        upload_button_clicked=bool(probe and probe.upload_button_clicked),
        upload_button_candidate_count=probe.upload_button_candidate_count if probe else 0,
        upload_menu_item_clicked=bool(probe and probe.upload_menu_item_clicked),
        upload_menu_item_count=probe.upload_menu_item_count if probe else 0,
        slash_key_pressed=False,
        upload_command_enter_pressed=False,
        enter_key_pressed_in_chat_composer=False,
        enter_key_pressed_in_picker=bool(probe and probe.picker_enter_pressed),
        picker_opened=bool(probe and probe.picker_opened),
        picker_count=probe.picker_count if probe else 0,
        filename_written=bool(probe and probe.filename_written),
        full_path_written_to_picker=False,
        open_button_clicked=False,
        picker_enter_pressed=bool(probe and probe.picker_enter_pressed),
        picker_closed_after_enter=bool(probe and probe.picker_closed_after_enter),
        attachment_verified=bool(probe and probe.attachment_verified),
        before_attachment_count=probe.before_attachment_count if probe else 0,
        after_attachment_count=probe.after_attachment_count if probe else 0,
        operator_report_attached_to_composer=bool(probe and probe.attachment_verified),
        browser_action_performed=bool(probe and (probe.chrome_target_focused or probe.upload_button_clicked or probe.picker_enter_pressed)),
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


def run_upload_button_desktop_filename_no_send(*, config_payload: Mapping[str, Any] | None, config_path: Path = DEFAULT_CONFIG_PATH, provider: str = "fake-ready", live_browser: bool, confirmation_text: str | None, self_report_path: str | None, expected_self_report_sha256: str | None = None, desktop_dir: str | None = None) -> UploadButtonResult:
    config_ok, url_hash, target_hash, config_issues = validate_config(config_payload)
    confirmation_matched = confirmation_text == CONFIRM_CHROME_UPLOAD_BUTTON_DESKTOP_FILENAME_NO_SEND
    desktop_path = Path(desktop_dir) if desktop_dir else DEFAULT_DESKTOP_DIR
    report = Path(self_report_path) if self_report_path else None
    empty = UploadButtonProbe(False, False, False, False, 0, False, 0, False, 0, str(desktop_path), report.name if report else None, False, False, False, False, 0, 0, None, ())
    if not config_ok:
        return make_result(ok=False, result_label=BLOCKED_CHROME_UPLOAD_BUTTON_CONFIG_INVALID, config_path=config_path, status_chat_configured=False, url_hash=url_hash, target_hash=target_hash, live_browser=live_browser, confirmation_matched=confirmation_matched, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=None, probe=empty, provider=provider, issues=config_issues)
    if confirmation_text is None:
        return make_result(ok=False, result_label=BLOCKED_CHROME_UPLOAD_BUTTON_CONFIRMATION_REQUIRED, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=live_browser, confirmation_matched=False, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=None, probe=empty, provider=provider, issues=("live upload-button confirmation is required",))
    if not confirmation_matched:
        return make_result(ok=False, result_label=BLOCKED_CHROME_UPLOAD_BUTTON_CONFIRMATION_MISMATCH, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=live_browser, confirmation_matched=False, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=None, probe=empty, provider=provider, issues=(f"confirmation must exactly match {CONFIRM_CHROME_UPLOAD_BUTTON_DESKTOP_FILENAME_NO_SEND}",))
    if not live_browser:
        return make_result(ok=False, result_label=BLOCKED_CHROME_UPLOAD_BUTTON_LIVE_BROWSER_REQUIRED, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=False, confirmation_matched=True, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=None, probe=empty, provider=provider, issues=("--live-browser is required",))
    if report is None or not report.exists() or not report.is_file():
        return make_result(ok=False, result_label=BLOCKED_CHROME_UPLOAD_BUTTON_REPORT_MISSING, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=True, confirmation_matched=True, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=None, probe=empty, provider=provider, issues=(f"self report not found: {report}",))
    if not is_child_of(report, desktop_path):
        return make_result(ok=False, result_label=BLOCKED_CHROME_UPLOAD_BUTTON_REPORT_NOT_ON_DESKTOP, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=True, confirmation_matched=True, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=None, probe=empty, provider=provider, issues=(f"self report must be on Desktop: {desktop_path}",))
    computed = sha256_file(report)
    if expected_self_report_sha256 and expected_self_report_sha256 != computed:
        return make_result(ok=False, result_label=BLOCKED_CHROME_UPLOAD_BUTTON_REPORT_HASH_MISMATCH, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=True, confirmation_matched=True, desktop_dir=desktop_path, report_path=report, expected_hash=expected_self_report_sha256, computed_hash=computed, probe=empty, provider=provider, issues=("self report hash mismatch",))

    adapter = build_adapter(provider)
    try:
        probe = adapter.attach_via_upload_button(report, desktop_path)
    except Exception as exc:
        return make_result(ok=False, result_label=BLOCKED_CHROME_UPLOAD_BUTTON_TARGET_NOT_READY, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=True, confirmation_matched=True, desktop_dir=desktop_path, report_path=report, expected_hash=computed, computed_hash=computed, probe=empty, provider=provider, issues=(str(exc),))

    if not probe.chrome_target_ready or not probe.chrome_target_focused:
        label = BLOCKED_CHROME_UPLOAD_BUTTON_TARGET_NOT_READY
    elif not probe.upload_button_clicked:
        label = BLOCKED_CHROME_UPLOAD_BUTTON_CONTROL_NOT_FOUND
    elif not probe.picker_opened:
        label = BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_NOT_OPENED
    elif probe.picker_count != 1:
        label = BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_AMBIGUOUS
    elif not probe.filename_written:
        label = BLOCKED_CHROME_UPLOAD_BUTTON_FILENAME_WRITE_FAILED
    elif not probe.picker_enter_pressed:
        label = BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_ENTER_FAILED
    elif not probe.attachment_verified:
        label = BLOCKED_CHROME_UPLOAD_BUTTON_ATTACHMENT_NOT_VERIFIED
    else:
        label = PASS_CHROME_SELF_REPORT_UPLOAD_BUTTON_DESKTOP_FILENAME_ATTACHED_NO_SEND
    return make_result(ok=label == PASS_CHROME_SELF_REPORT_UPLOAD_BUTTON_DESKTOP_FILENAME_ATTACHED_NO_SEND, result_label=label, config_path=config_path, status_chat_configured=True, url_hash=url_hash, target_hash=target_hash, live_browser=True, confirmation_matched=True, desktop_dir=desktop_path, report_path=report, expected_hash=computed, computed_hash=computed, probe=probe, provider=adapter.provider_name, issues=probe.issues)


def render_text(result: UploadButtonResult) -> str:
    lines = [
        f"result_label: {result.result_label}",
        f"ok: {str(result.ok).lower()}",
        f"patch_name: {result.patch_name}",
        f"selected_action: {result.selected_action}",
        f"browser_lane: {result.browser_lane}",
        f"live_browser: {str(result.live_browser).lower()}",
        f"stop_before_send: {str(result.stop_before_send).lower()}",
        f"confirmation_matched: {str(result.confirmation_matched).lower()}",
        f"desktop_directory: {result.desktop_directory}",
        f"self_report_path: {result.self_report_path}",
        f"self_report_filename: {result.self_report_filename}",
        f"self_report_sha256: {result.self_report_sha256}",
        f"computed_self_report_sha256: {result.computed_self_report_sha256}",
        f"chrome_target_ready: {str(result.chrome_target_ready).lower()}",
        f"chrome_target_focused: {str(result.chrome_target_focused).lower()}",
        f"browser_actions_used: {','.join(result.browser_actions_used) if result.browser_actions_used else 'none'}",
        f"forbidden_keyboard_shortcuts_used: {','.join(result.forbidden_keyboard_shortcuts_used) if result.forbidden_keyboard_shortcuts_used else 'none'}",
        f"safe_focus_click_performed: {str(result.safe_focus_click_performed).lower()}",
        f"upload_button_clicked: {str(result.upload_button_clicked).lower()}",
        f"upload_button_candidate_count: {result.upload_button_candidate_count}",
        f"upload_menu_item_clicked: {str(result.upload_menu_item_clicked).lower()}",
        f"upload_menu_item_count: {result.upload_menu_item_count}",
        f"slash_key_pressed: {str(result.slash_key_pressed).lower()}",
        f"upload_command_enter_pressed: {str(result.upload_command_enter_pressed).lower()}",
        f"enter_key_pressed_in_chat_composer: {str(result.enter_key_pressed_in_chat_composer).lower()}",
        f"enter_key_pressed_in_picker: {str(result.enter_key_pressed_in_picker).lower()}",
        f"picker_opened: {str(result.picker_opened).lower()}",
        f"picker_count: {result.picker_count}",
        f"filename_written: {str(result.filename_written).lower()}",
        f"full_path_written_to_picker: {str(result.full_path_written_to_picker).lower()}",
        f"open_button_clicked: {str(result.open_button_clicked).lower()}",
        f"picker_enter_pressed: {str(result.picker_enter_pressed).lower()}",
        f"picker_closed_after_enter: {str(result.picker_closed_after_enter).lower()}",
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


def write_evidence(result: UploadButtonResult, *, json_output_path: Path = DEFAULT_JSON_OUTPUT_PATH, txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_text(result), encoding="utf-8")
    return json_output_path, txt_output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Attach Desktop self-report by visible upload button + filename Enter in Chrome, without Send")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-no-button", "fake-no-picker", "fake-write-failed", "fake-enter-failed", "fake-not-verified", "pywinauto"), default="fake-ready")
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
    result = run_upload_button_desktop_filename_no_send(
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