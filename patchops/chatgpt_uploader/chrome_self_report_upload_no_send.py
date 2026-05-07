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

PATCH_NAME = "pseudo_self_report_upload_no_send"
CONFIRM_CHROME_SELF_REPORT_UPLOAD_NO_SEND = "PATCHOPS_CONFIRM_CHROME_SELF_REPORT_UPLOAD_NO_SEND"
PASS_CHROME_SELF_REPORT_ATTACHED_NO_SEND = "PASS_CHROME_SELF_REPORT_ATTACHED_NO_SEND"
BLOCKED_CHROME_SELF_REPORT_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_SELF_REPORT_CONFIRMATION_REQUIRED"
BLOCKED_CHROME_SELF_REPORT_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_SELF_REPORT_CONFIRMATION_MISMATCH"
BLOCKED_CHROME_SELF_REPORT_LIVE_BROWSER_REQUIRED = "BLOCKED_CHROME_SELF_REPORT_LIVE_BROWSER_REQUIRED"
BLOCKED_CHROME_SELF_REPORT_CONFIG_MISSING = "BLOCKED_CHROME_SELF_REPORT_CONFIG_MISSING"
BLOCKED_CHROME_SELF_REPORT_BROWSER_MISMATCH = "BLOCKED_CHROME_SELF_REPORT_BROWSER_MISMATCH"
BLOCKED_CHROME_SELF_REPORT_URL_INVALID = "BLOCKED_CHROME_SELF_REPORT_URL_INVALID"
BLOCKED_CHROME_SELF_REPORT_PATH_MISSING = "BLOCKED_CHROME_SELF_REPORT_PATH_MISSING"
BLOCKED_CHROME_SELF_REPORT_HASH_MISMATCH = "BLOCKED_CHROME_SELF_REPORT_HASH_MISMATCH"
BLOCKED_CHROME_SELF_REPORT_TARGET_NOT_READY = "BLOCKED_CHROME_SELF_REPORT_TARGET_NOT_READY"
BLOCKED_CHROME_SELF_REPORT_ATTACHMENT_CONTROL_NOT_FOUND = "BLOCKED_CHROME_SELF_REPORT_ATTACHMENT_CONTROL_NOT_FOUND"
BLOCKED_CHROME_SELF_REPORT_FILE_PICKER_NOT_READY = "BLOCKED_CHROME_SELF_REPORT_FILE_PICKER_NOT_READY"
BLOCKED_CHROME_SELF_REPORT_OPEN_BUTTON_NOT_FOUND = "BLOCKED_CHROME_SELF_REPORT_OPEN_BUTTON_NOT_FOUND"
BLOCKED_CHROME_SELF_REPORT_ATTACHMENT_NOT_VERIFIED = "BLOCKED_CHROME_SELF_REPORT_ATTACHMENT_NOT_VERIFIED"
BLOCKED_SEND_RISK = "BLOCKED_SEND_RISK"

DEFAULT_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_self_report_upload_no_send.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_self_report_upload_no_send.txt")

CHROME_TITLE_TOKENS = ("chrome", "google chrome")
CHATGPT_TITLE_TOKENS = ("chatgpt", "openai", "patchops")
ATTACHMENT_NAME_TOKENS = ("attach", "attached", "attachment", "upload", "uploads", "upload files", "upload file", "add files", "add photos", "add photo", "add file", "paperclip", "file", "files", "photos", "photo", "plus")
FILE_DIALOG_TITLE_TOKENS = ("open", "upload", "choose", "file", "select")
OPEN_BUTTON_TOKENS = ("open", "&open")


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


def normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


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


@dataclass(frozen=True)
class UploadProbe:
    chrome_target_ready: bool
    chrome_target_focused: bool
    attachment_control_found: bool
    attachment_candidate_count: int
    file_picker_used: bool
    file_picker_opened: bool
    file_path_written: bool
    open_button_clicked: bool
    enter_key_pressed: bool
    attachment_verified: bool
    selected_window_title: str | None
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class SelfReportUploadSafety:
    browser_action_performed: bool = False
    file_upload_attempted: bool = False
    operator_report_attached_to_composer: bool = False
    operator_report_uploaded: bool = False
    chatgpt_submit_performed: bool = False
    status_message_posted: bool = False
    send_button_pressed: bool = False
    enter_key_pressed: bool = False
    raw_conversation_text_available: bool = False
    selenium_used: bool = False
    webdriver_used: bool = False
    browser_dom_automation_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False


@dataclass(frozen=True)
class SelfReportUploadResult:
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
    attachment_control_found: bool
    attachment_candidate_count: int
    file_picker_used: bool
    file_picker_opened: bool
    file_path_written: bool
    open_button_clicked: bool
    enter_key_pressed: bool
    attachment_verified: bool
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
    safety: SelfReportUploadSafety = field(default_factory=SelfReportUploadSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        return payload


class UploadAdapter(Protocol):
    provider_name: str

    def upload_no_send(self, report_path: Path) -> UploadProbe:
        ...


class FakeUploadAdapter:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.provider_name = f"fake-{mode}"

    def upload_no_send(self, report_path: Path) -> UploadProbe:
        title = "PatchOps - ChatGPT - Google Chrome"
        if self.mode == "no-target":
            return UploadProbe(False, False, False, 0, False, False, False, False, False, False, None, ("fake target missing",))
        if self.mode == "no-attachment-control":
            return UploadProbe(True, True, False, 0, False, False, False, False, False, False, title, ("fake attachment control missing",))
        if self.mode == "no-dialog":
            return UploadProbe(True, True, True, 1, True, False, False, False, False, False, title, ("fake file picker missing",))
        if self.mode == "no-open-button":
            return UploadProbe(True, True, True, 1, True, True, True, False, False, False, title, ("fake Open button missing",))
        if self.mode == "not-verified":
            return UploadProbe(True, True, True, 1, True, True, True, True, False, False, title, ("fake attachment not verified",))
        return UploadProbe(True, True, True, 1, True, True, True, True, False, True, title, ())


class PywinautoUploadAdapter:
    provider_name = "pywinauto"

    def __init__(self, *, settle_seconds: float = 0.7, verify_timeout_seconds: float = 12.0) -> None:
        self.settle_seconds = settle_seconds
        self.verify_timeout_seconds = verify_timeout_seconds

    def _desktop(self) -> Any:
        try:
            from pywinauto import Desktop  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"pywinauto is required for live Chrome self-report upload: {exc}") from exc
        return Desktop(backend="uia")

    def _looks_like_chrome_target(self, window: Any) -> bool:
        title = (_safe_window_title(window) or "").lower()
        return any(token in title for token in CHROME_TITLE_TOKENS) and any(token in title for token in CHATGPT_TITLE_TOKENS)

    def _find_target_window(self) -> tuple[Any | None, list[Any], tuple[str, ...]]:
        try:
            windows = list(self._desktop().windows())
        except Exception as exc:
            return None, [], (str(exc),)
        matches = [window for window in windows if self._looks_like_chrome_target(window)]
        if len(matches) != 1:
            return None, matches, (f"expected exactly one visible Chrome ChatGPT/PatchOps target; found {len(matches)}",)
        return matches[0], matches, ()

    def _element_name(self, element: Any) -> str:
        parts: list[str] = []
        for getter in (
            lambda: element.window_text(),
            lambda: element.element_info.name,
            lambda: getattr(element.element_info, "automation_id", ""),
            lambda: getattr(element.element_info, "class_name", ""),
        ):
            try:
                value = str(getter() or "").strip()
            except Exception:
                value = ""
            if value:
                parts.append(value)
        return " ".join(parts).lower()

    def _element_rect_tuple(self, element: Any) -> tuple[int, int, int, int] | None:
        try:
            rect = element.rectangle()
            return (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))
        except Exception:
            return None

    def _element_center(self, element: Any) -> tuple[int, int] | None:
        rect = self._element_rect_tuple(element)
        if rect is None:
            return None
        left, top, right, bottom = rect
        return (int((left + right) / 2), int((top + bottom) / 2))

    def _looks_like_attachment_by_name(self, element: Any) -> bool:
        name = self._element_name(element)
        if not name:
            return False
        blocked_tokens = ("send", "submit", "voice", "microphone", "dictate", "stop", "close", "new chat", "profile", "settings")
        if any(token in name for token in blocked_tokens):
            return False
        return any(token in name for token in ATTACHMENT_NAME_TOKENS)

    def _looks_like_attachment_by_position(self, window: Any, element: Any) -> bool:
        try:
            control_type = str(element.element_info.control_type or "").lower()
            visible = bool(element.is_visible())
            enabled = bool(element.is_enabled())
        except Exception:
            return False
        if not visible or not enabled:
            return False
        if control_type not in {"button", "splitbutton", "menuitem", "custom", "group", "pane", "hyperlink"}:
            return False
        window_rect = self._element_rect_tuple(window)
        rect = self._element_rect_tuple(element)
        center = self._element_center(element)
        if window_rect is None or rect is None or center is None:
            return False
        wl, wt, wr, wb = window_rect
        left, top, right, bottom = rect
        cx, cy = center
        width = max(1, wr - wl)
        height = max(1, wb - wt)
        element_width = max(1, right - left)
        element_height = max(1, bottom - top)
        lower_half = cy >= wt + int(height * 0.50)
        left_half = cx <= wl + int(width * 0.50)
        plausible_button_size = 10 <= element_width <= 120 and 10 <= element_height <= 120
        return lower_half and left_half and plausible_button_size

    def _attachment_controls(self, window: Any) -> list[Any]:
        try:
            descendants = list(window.descendants())
        except Exception:
            return []

        named: list[Any] = []
        geometric: list[Any] = []
        for element in descendants:
            try:
                if not bool(element.is_visible()) or not bool(element.is_enabled()):
                    continue
            except Exception:
                continue
            if self._looks_like_attachment_by_name(element):
                named.append(element)
            elif self._looks_like_attachment_by_position(window, element):
                geometric.append(element)

        candidates = named if named else geometric
        deduped: list[Any] = []
        seen: set[tuple[int, int, int, int]] = set()
        for element in candidates:
            rect = self._element_rect_tuple(element)
            if rect is None or rect in seen:
                continue
            seen.add(rect)
            deduped.append(element)

        if len(deduped) <= 1:
            return deduped

        ranked: list[tuple[int, int, Any]] = []
        for element in deduped:
            center = self._element_center(element)
            if center is None:
                continue
            cx, cy = center
            ranked.append((cx, -cy, element))
        ranked.sort(key=lambda item: (item[0], item[1]))
        return [ranked[0][2]] if ranked else []
    def _upload_menu_items(self) -> list[Any]:
        """Find a visible ChatGPT upload-files menu item after the attachment/plus button is clicked.

        Current ChatGPT Chrome UI may open a small menu first instead of immediately opening the
        native file picker. This method only returns visible, enabled UIA elements whose accessible
        text explicitly looks like an upload/add-files action. It does not use DOM inspection and does
        not click arbitrary coordinates.
        """
        try:
            desktop = self._desktop()
            windows = list(desktop.windows())
        except Exception:
            windows = []

        candidates: list[Any] = []
        upload_tokens = ("upload files", "upload file", "add files", "add file", "attach files", "attach file", "file upload")
        blocked_tokens = ("send", "submit", "new chat", "settings", "profile", "voice", "microphone")
        for root in windows:
            try:
                descendants = list(root.descendants())
            except Exception:
                descendants = []
            for element in descendants:
                try:
                    visible = bool(element.is_visible())
                    enabled = bool(element.is_enabled())
                    control_type = str(element.element_info.control_type or "").lower()
                except Exception:
                    continue
                if not visible or not enabled:
                    continue
                if control_type not in {"button", "menuitem", "listitem", "text", "custom", "group", "pane", "hyperlink"}:
                    continue
                name = self._element_name(element)
                if not name or any(token in name for token in blocked_tokens):
                    continue
                if any(token in name for token in upload_tokens):
                    candidates.append(element)

        deduped: list[Any] = []
        seen: set[tuple[int, int, int, int]] = set()
        for element in candidates:
            rect = self._element_rect_tuple(element)
            if rect is None or rect in seen:
                continue
            seen.add(rect)
            deduped.append(element)
        return deduped

    def _click_upload_menu_item_if_present(self) -> tuple[bool, int, tuple[str, ...]]:
        items = self._upload_menu_items()
        if len(items) == 0:
            return False, 0, ()
        if len(items) != 1:
            return False, len(items), (f"expected zero or one upload menu item; found {len(items)}",)
        try:
            items[0].click_input()
            time.sleep(self.settle_seconds)
            return True, 1, ()
        except Exception as exc:
            return False, 1, (f"upload menu item click failed: {exc}",)
    def _file_dialogs(self) -> list[Any]:
        try:
            windows = list(self._desktop().windows())
        except Exception:
            return []
        matches: list[Any] = []
        for window in windows:
            title = (_safe_window_title(window) or "").lower()
            if any(token in title for token in FILE_DIALOG_TITLE_TOKENS):
                matches.append(window)
        return matches

    def _path_edit(self, dialog: Any) -> Any | None:
        try:
            edits = [item for item in dialog.descendants(control_type="Edit") if item.is_visible() and item.is_enabled()]
        except Exception:
            return None
        return edits[0] if edits else None

    def _open_button(self, dialog: Any) -> Any | None:
        try:
            buttons = [item for item in dialog.descendants(control_type="Button") if item.is_visible() and item.is_enabled()]
        except Exception:
            return None
        for button in buttons:
            name = str(button.window_text() or button.element_info.name or "").strip().lower()
            if any(token == name or token in name for token in OPEN_BUTTON_TOKENS):
                return button
        return None

    def _attachment_verified(self, window: Any, report_path: Path) -> bool:
        wanted = {report_path.name.lower(), report_path.stem.lower()}
        deadline = time.monotonic() + self.verify_timeout_seconds
        while time.monotonic() < deadline:
            try:
                descendants = window.descendants()
            except Exception:
                descendants = []
            for element in descendants:
                try:
                    text = str(element.window_text() or element.element_info.name or "").strip().lower()
                except Exception:
                    continue
                if any(token and token in text for token in wanted):
                    return True
            time.sleep(0.35)
        return False

    def upload_no_send(self, report_path: Path) -> UploadProbe:
        window, matches, issues = self._find_target_window()
        if window is None:
            return UploadProbe(False, False, False, 0, False, False, False, False, False, False, None, issues)
        title = _safe_window_title(window)
        try:
            window.set_focus()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return UploadProbe(True, False, False, 0, False, False, False, False, False, False, title, (f"Chrome focus failed: {exc}",))

        controls = self._attachment_controls(window)
        if len(controls) != 1:
            return UploadProbe(True, True, False, len(controls), False, False, False, False, False, False, title, (f"expected exactly one attachment control; found {len(controls)}",))

        try:
            controls[0].click_input()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return UploadProbe(True, True, True, 1, False, False, False, False, False, False, title, (f"attachment control click failed: {exc}",))

        dialogs = self._file_dialogs()
        menu_clicked = False
        menu_count = 0
        menu_issues: tuple[str, ...] = ()
        if len(dialogs) != 1:
            menu_clicked, menu_count, menu_issues = self._click_upload_menu_item_if_present()
            if menu_issues:
                return UploadProbe(True, True, True, 1, True, False, False, False, False, False, title, menu_issues)
            if menu_clicked:
                time.sleep(self.settle_seconds)
                dialogs = self._file_dialogs()
        if len(dialogs) != 1:
            suffix = f"; upload menu items found/clicked: {menu_count}/{str(menu_clicked).lower()}"
            return UploadProbe(True, True, True, 1, True, False, False, False, False, False, title, (f"expected exactly one native file picker; found {len(dialogs)}" + suffix,))
        dialog = dialogs[0]
        edit = self._path_edit(dialog)
        if edit is None:
            return UploadProbe(True, True, True, 1, True, True, False, False, False, False, title, ("file picker path edit not found",))
        try:
            edit.set_edit_text(str(report_path))
            time.sleep(self.settle_seconds / 2)
        except Exception as exc:
            return UploadProbe(True, True, True, 1, True, True, False, False, False, False, title, (f"file path write failed: {exc}",))

        open_button = self._open_button(dialog)
        if open_button is None:
            return UploadProbe(True, True, True, 1, True, True, True, False, False, False, title, ("Open button not found; refusing Enter fallback",))
        try:
            open_button.click_input()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return UploadProbe(True, True, True, 1, True, True, True, False, False, False, title, (f"Open button click failed: {exc}",))

        verified = self._attachment_verified(window, report_path)
        if not verified:
            return UploadProbe(True, True, True, 1, True, True, True, True, False, False, title, ("attachment chip/text was not verified after Open click",))
        return UploadProbe(True, True, True, 1, True, True, True, True, False, True, title, ())


def _safe_window_title(window: Any) -> str | None:
    try:
        title = str(window.window_text() or "")
        return title or None
    except Exception:
        return None


def build_adapter(provider: str) -> UploadAdapter:
    if provider.startswith("fake-"):
        return FakeUploadAdapter(provider.removeprefix("fake-"))
    if provider == "pywinauto":
        return PywinautoUploadAdapter()
    raise ValueError(f"Unknown provider: {provider}")


def validate_config(config_payload: Mapping[str, Any] | None) -> tuple[bool, str | None, str | None, list[str]]:
    if not config_payload:
        return False, None, None, ["status target config is required"]
    status = config_payload.get("status_chat")
    if not isinstance(status, Mapping):
        return False, None, None, ["status_chat object is required"]
    issues: list[str] = []
    enabled = normalize_bool(status.get("enabled"), default=False)
    lane = normalize_optional_text(status.get("browser_lane"))
    target_url = normalize_optional_text(status.get("target_url"))
    target_hash = normalize_optional_text(status.get("target_url_sha256"))
    if not enabled:
        issues.append("status_chat.enabled must be true")
    if lane != "chrome":
        issues.append("browser_lane must be chrome")
    if not target_url or not target_url.startswith("https://chatgpt.com/") or "/c/" not in target_url:
        issues.append("target_url must be a ChatGPT conversation URL")
    if target_url and target_hash and sha256_text(target_url) != target_hash:
        issues.append("target_url_sha256 does not match target_url")
    return not issues, sha256_text(target_url) if target_url else None, target_hash, issues


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
    probe: UploadProbe | None,
    provider: str,
    issues: Sequence[str],
) -> SelfReportUploadResult:
    title = probe.selected_window_title if probe else None
    safety = SelfReportUploadSafety(
        browser_action_performed=bool(probe and (probe.chrome_target_focused or probe.file_picker_used or probe.file_path_written or probe.open_button_clicked)),
        file_upload_attempted=bool(probe and probe.open_button_clicked),
        operator_report_attached_to_composer=bool(probe and probe.attachment_verified),
        operator_report_uploaded=False,
        chatgpt_submit_performed=False,
        status_message_posted=False,
        send_button_pressed=False,
        enter_key_pressed=bool(probe and probe.enter_key_pressed),
        raw_conversation_text_available=False,
        selenium_used=False,
        webdriver_used=False,
        browser_dom_automation_used=False,
        cloudflare_bypass_attempted=False,
        captcha_bypass_attempted=False,
        conversation_text_logged=False,
        random_page_click_performed=False,
    )
    return SelfReportUploadResult(
        ok=ok,
        result_label=result_label,
        patch_name=PATCH_NAME,
        selected_action="upload_self_report_no_send",
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
        attachment_control_found=bool(probe and probe.attachment_control_found),
        attachment_candidate_count=probe.attachment_candidate_count if probe else 0,
        file_picker_used=bool(probe and probe.file_picker_used),
        file_picker_opened=bool(probe and probe.file_picker_opened),
        file_path_written=bool(probe and probe.file_path_written),
        open_button_clicked=bool(probe and probe.open_button_clicked),
        enter_key_pressed=safety.enter_key_pressed,
        attachment_verified=bool(probe and probe.attachment_verified),
        operator_report_attached_to_composer=safety.operator_report_attached_to_composer,
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
        selected_target_title_hash=sha256_text(title) if title else None,
        selected_target_title_length=len(title) if title else None,
        provider=provider,
        issues=tuple(issues),
        safety=safety,
    )


def run_self_report_upload_no_send(
    *,
    config_payload: Mapping[str, Any] | None,
    config_path: Path = DEFAULT_CONFIG_PATH,
    provider: str = "fake-ready",
    live_browser: bool,
    confirmation_text: str | None,
    self_report_path: str | None,
    expected_self_report_sha256: str | None = None,
) -> SelfReportUploadResult:
    config_ok, url_hash, target_hash, config_issues = validate_config(config_payload)
    confirmation_matched = confirmation_text == CONFIRM_CHROME_SELF_REPORT_UPLOAD_NO_SEND
    if not config_ok:
        label = BLOCKED_CHROME_SELF_REPORT_CONFIG_MISSING
        if any("browser_lane" in issue for issue in config_issues):
            label = BLOCKED_CHROME_SELF_REPORT_BROWSER_MISMATCH
        elif any("target_url" in issue for issue in config_issues):
            label = BLOCKED_CHROME_SELF_REPORT_URL_INVALID
        return make_result(ok=False, result_label=label, config_path=config_path, status_chat_configured=False, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=live_browser, confirmation_text=confirmation_text, confirmation_matched=confirmation_matched, report_path=Path(self_report_path) if self_report_path else None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=None, provider=provider, issues=config_issues)
    if confirmation_text is None:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SELF_REPORT_CONFIRMATION_REQUIRED, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=live_browser, confirmation_text=None, confirmation_matched=False, report_path=Path(self_report_path) if self_report_path else None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=None, provider=provider, issues=("live upload confirmation is required",))
    if not confirmation_matched:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SELF_REPORT_CONFIRMATION_MISMATCH, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=live_browser, confirmation_text=confirmation_text, confirmation_matched=False, report_path=Path(self_report_path) if self_report_path else None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=None, provider=provider, issues=(f"confirmation must exactly match {CONFIRM_CHROME_SELF_REPORT_UPLOAD_NO_SEND}",))
    if not live_browser:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SELF_REPORT_LIVE_BROWSER_REQUIRED, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=False, confirmation_text=confirmation_text, confirmation_matched=True, report_path=Path(self_report_path) if self_report_path else None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=None, provider=provider, issues=("--live-browser is required",))
    if not self_report_path:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SELF_REPORT_PATH_MISSING, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=None, provider=provider, issues=("self report path is required",))
    report_path = Path(self_report_path)
    if not report_path.exists() or not report_path.is_file():
        return make_result(ok=False, result_label=BLOCKED_CHROME_SELF_REPORT_PATH_MISSING, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=report_path, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=None, provider=provider, issues=(f"self report not found: {report_path}",))
    computed_hash = sha256_file(report_path)
    if expected_self_report_sha256 and expected_self_report_sha256 != computed_hash:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SELF_REPORT_HASH_MISMATCH, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=report_path, report_sha256=expected_self_report_sha256, computed_report_sha256=computed_hash, probe=None, provider=provider, issues=("self report hash mismatch",))

    try:
        adapter = build_adapter(provider)
        probe = adapter.upload_no_send(report_path)
    except Exception as exc:
        return make_result(ok=False, result_label=BLOCKED_CHROME_SELF_REPORT_TARGET_NOT_READY, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=report_path, report_sha256=computed_hash, computed_report_sha256=computed_hash, probe=None, provider=provider, issues=(str(exc),))

    if not probe.chrome_target_ready or not probe.chrome_target_focused:
        label = BLOCKED_CHROME_SELF_REPORT_TARGET_NOT_READY
    elif not probe.attachment_control_found:
        label = BLOCKED_CHROME_SELF_REPORT_ATTACHMENT_CONTROL_NOT_FOUND
    elif not probe.file_picker_opened or not probe.file_path_written:
        label = BLOCKED_CHROME_SELF_REPORT_FILE_PICKER_NOT_READY
    elif not probe.open_button_clicked:
        label = BLOCKED_CHROME_SELF_REPORT_OPEN_BUTTON_NOT_FOUND
    elif probe.enter_key_pressed:
        label = BLOCKED_SEND_RISK
    elif not probe.attachment_verified:
        label = BLOCKED_CHROME_SELF_REPORT_ATTACHMENT_NOT_VERIFIED
    else:
        label = PASS_CHROME_SELF_REPORT_ATTACHED_NO_SEND

    return make_result(ok=label == PASS_CHROME_SELF_REPORT_ATTACHED_NO_SEND, result_label=label, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=report_path, report_sha256=computed_hash, computed_report_sha256=computed_hash, probe=probe, provider=adapter.provider_name, issues=probe.issues)


def render_text(result: SelfReportUploadResult) -> str:
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
        f"attachment_control_found: {str(result.attachment_control_found).lower()}",
        f"attachment_candidate_count: {result.attachment_candidate_count}",
        f"file_picker_used: {str(result.file_picker_used).lower()}",
        f"file_picker_opened: {str(result.file_picker_opened).lower()}",
        f"file_path_written: {str(result.file_path_written).lower()}",
        f"open_button_clicked: {str(result.open_button_clicked).lower()}",
        f"enter_key_pressed: {str(result.enter_key_pressed).lower()}",
        f"attachment_verified: {str(result.attachment_verified).lower()}",
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


def write_evidence(result: SelfReportUploadResult, *, json_output_path: Path = DEFAULT_JSON_OUTPUT_PATH, txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_text(result), encoding="utf-8")
    return json_output_path, txt_output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Upload a self report to the configured Chrome target without pressing Enter or Send")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-no-attachment-control", "fake-no-dialog", "fake-no-open-button", "fake-not-verified", "pywinauto"), default="fake-ready")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--self-report-path", required=True)
    parser.add_argument("--self-report-sha256", default=None)
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config_path)
    config_payload = load_json_object(config_path) if config_path.exists() else None
    result = run_self_report_upload_no_send(
        config_payload=config_payload,
        config_path=config_path,
        provider=args.provider,
        live_browser=bool(args.live_browser),
        confirmation_text=args.confirm_live_browser_text,
        self_report_path=args.self_report_path,
        expected_self_report_sha256=args.self_report_sha256,
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