from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import struct
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

PATCH_NAME = "pseudo_self_report_upload_no_send_repair_05_keyboard_paste"
CONFIRM_CHROME_KEYBOARD_SELF_REPORT_UPLOAD_NO_SEND = "PATCHOPS_CONFIRM_CHROME_KEYBOARD_SELF_REPORT_UPLOAD_NO_SEND"
PASS_CHROME_SELF_REPORT_KEYBOARD_ATTACHED_NO_SEND = "PASS_CHROME_SELF_REPORT_KEYBOARD_ATTACHED_NO_SEND"
BLOCKED_CHROME_KEYBOARD_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_KEYBOARD_CONFIRMATION_REQUIRED"
BLOCKED_CHROME_KEYBOARD_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_KEYBOARD_CONFIRMATION_MISMATCH"
BLOCKED_CHROME_KEYBOARD_LIVE_BROWSER_REQUIRED = "BLOCKED_CHROME_KEYBOARD_LIVE_BROWSER_REQUIRED"
BLOCKED_CHROME_KEYBOARD_CONFIG_MISSING = "BLOCKED_CHROME_KEYBOARD_CONFIG_MISSING"
BLOCKED_CHROME_KEYBOARD_BROWSER_MISMATCH = "BLOCKED_CHROME_KEYBOARD_BROWSER_MISMATCH"
BLOCKED_CHROME_KEYBOARD_URL_INVALID = "BLOCKED_CHROME_KEYBOARD_URL_INVALID"
BLOCKED_CHROME_KEYBOARD_REPORT_MISSING = "BLOCKED_CHROME_KEYBOARD_REPORT_MISSING"
BLOCKED_CHROME_KEYBOARD_REPORT_HASH_MISMATCH = "BLOCKED_CHROME_KEYBOARD_REPORT_HASH_MISMATCH"
BLOCKED_CHROME_KEYBOARD_TARGET_NOT_READY = "BLOCKED_CHROME_KEYBOARD_TARGET_NOT_READY"
BLOCKED_CHROME_KEYBOARD_CLIPBOARD_FAILED = "BLOCKED_CHROME_KEYBOARD_CLIPBOARD_FAILED"
BLOCKED_CHROME_KEYBOARD_PASTE_FAILED = "BLOCKED_CHROME_KEYBOARD_PASTE_FAILED"
BLOCKED_CHROME_KEYBOARD_ATTACHMENT_NOT_VERIFIED = "BLOCKED_CHROME_KEYBOARD_ATTACHMENT_NOT_VERIFIED"
BLOCKED_SEND_RISK = "BLOCKED_SEND_RISK"

DEFAULT_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_keyboard_upload_no_send.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_keyboard_upload_no_send.txt")
EDGE_LANE_FILES = (
    Path("patchops/chatgpt_uploader/edge_report_uploader.py"),
    Path("patchops/chatgpt_uploader/edge_status_reporter.py"),
    Path("scripts/run_uploader_edge_fail_report_upload_no_send_probe.py"),
)

CHROME_TITLE_TOKENS = ("chrome", "google chrome")
CHATGPT_TITLE_TOKENS = ("chatgpt", "openai", "patchops")
SAFE_KEYBOARD_SHORTCUTS = ("CTRL+V",)
FORBIDDEN_KEYBOARD_SHORTCUTS = ("ENTER", "CTRL+ENTER", "ALT+ENTER", "CTRL+U", "/")


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


def scan_edge_keyboard_shortcuts(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path.cwd()
    tokens = {
        "ctrl_v": ("^v", "CTRL+V", "VK_CONTROL", "paste"),
        "enter": ("{ENTER}", "ENTER", "VK_RETURN"),
        "ctrl_u": ("^u", "CTRL+U"),
        "slash": ("/", "SLASH"),
        "clipboard": ("clipboard", "SetClipboard", "OpenClipboard"),
        "type_keys": ("type_keys", "send_keys"),
    }
    found: dict[str, bool] = {key: False for key in tokens}
    scanned_files: list[str] = []
    for rel in EDGE_LANE_FILES:
        path = root / rel
        if not path.exists():
            continue
        scanned_files.append(str(rel).replace("\\", "/"))
        text = path.read_text(encoding="utf-8", errors="replace")
        lowered = text.lower()
        for key, variants in tokens.items():
            if any(variant.lower() in lowered for variant in variants):
                found[key] = True
    return {
        "scanned_files": scanned_files,
        "found": found,
        "safe_shortcuts_reused": list(SAFE_KEYBOARD_SHORTCUTS),
        "forbidden_shortcuts_not_used": list(FORBIDDEN_KEYBOARD_SHORTCUTS),
    }


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


@dataclass(frozen=True)
class KeyboardProbe:
    chrome_target_ready: bool
    chrome_target_focused: bool
    file_clipboard_written: bool
    ctrl_v_pressed: bool
    attachment_verified: bool
    selected_window_title: str | None
    edge_keyboard_scan: Mapping[str, Any] = field(default_factory=dict)
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class KeyboardUploadSafety:
    browser_action_performed: bool = False
    file_clipboard_written: bool = False
    keyboard_shortcut_used: bool = False
    ctrl_v_pressed: bool = False
    enter_key_pressed: bool = False
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
class KeyboardUploadResult:
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
    edge_keyboard_scan: Mapping[str, Any]
    keyboard_shortcuts_used: tuple[str, ...]
    forbidden_keyboard_shortcuts_used: tuple[str, ...]
    file_clipboard_written: bool
    ctrl_v_pressed: bool
    enter_key_pressed: bool
    file_picker_used: bool
    file_path_written: bool
    open_button_clicked: bool
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
    safety: KeyboardUploadSafety = field(default_factory=KeyboardUploadSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        return payload


class KeyboardAdapter(Protocol):
    provider_name: str

    def _element_rect_tuple(self, element: Any) -> tuple[int, int, int, int] | None:
        try:
            rect = element.rectangle()
            return (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))
        except Exception:
            return None

    def _element_text(self, element: Any) -> str:
        parts: list[str] = []
        try:
            text = str(element.window_text() or "").strip()
            if text:
                parts.append(text)
        except Exception:
            pass
        try:
            name = str(element.element_info.name or "").strip()
            if name:
                parts.append(name)
        except Exception:
            pass
        return " ".join(parts).strip()

    def _visible_attachment_matches(self, window: Any, report_path: Path) -> set[tuple[str, tuple[int, int, int, int]]]:
        """Return visible lower-composer filename matches.

        This deliberately ignores arbitrary hidden accessibility text. A match must be visible,
        have a rectangle, live in the lower part of the Chrome target, and contain the generated
        report filename/stem. The caller compares before/after paste sets so old text cannot
        produce a false pass.
        """
        wanted = {report_path.name.lower(), report_path.stem.lower()}
        window_rect = self._element_rect_tuple(window)
        if window_rect is None:
            return set()
        wl, wt, wr, wb = window_rect
        height = max(1, wb - wt)
        lower_threshold = wt + int(height * 0.45)
        matches: set[tuple[str, tuple[int, int, int, int]]] = set()
        try:
            descendants = window.descendants()
        except Exception:
            descendants = []
        for element in descendants:
            try:
                if not bool(element.is_visible()):
                    continue
            except Exception:
                continue
            rect = self._element_rect_tuple(element)
            if rect is None:
                continue
            left, top, right, bottom = rect
            if bottom < lower_threshold:
                continue
            text = self._element_text(element).strip()
            lowered = text.lower()
            if not lowered:
                continue
            if any(token and token in lowered for token in wanted):
                matches.add((text[:160], rect))
        return matches

    def _attachment_verified_after_paste(self, window: Any, report_path: Path, before_matches: set[tuple[str, tuple[int, int, int, int]]]) -> tuple[bool, int, int]:
        deadline = time.monotonic() + self.verify_timeout_seconds
        latest_after_count = 0
        while time.monotonic() < deadline:
            after_matches = self._visible_attachment_matches(window, report_path)
            latest_after_count = len(after_matches)
            new_matches = after_matches - before_matches
            if new_matches:
                return True, len(before_matches), latest_after_count
            time.sleep(0.35)
        return False, len(before_matches), latest_after_count
    def attach_by_keyboard(self, report_path: Path, *, edge_keyboard_scan: Mapping[str, Any]) -> KeyboardProbe:
        ...


class FakeKeyboardAdapter:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.provider_name = f"fake-{mode}"

    def _element_rect_tuple(self, element: Any) -> tuple[int, int, int, int] | None:
        try:
            rect = element.rectangle()
            return (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))
        except Exception:
            return None

    def _element_text(self, element: Any) -> str:
        parts: list[str] = []
        try:
            text = str(element.window_text() or "").strip()
            if text:
                parts.append(text)
        except Exception:
            pass
        try:
            name = str(element.element_info.name or "").strip()
            if name:
                parts.append(name)
        except Exception:
            pass
        return " ".join(parts).strip()

    def _visible_attachment_matches(self, window: Any, report_path: Path) -> set[tuple[str, tuple[int, int, int, int]]]:
        """Return visible lower-composer filename matches.

        This deliberately ignores arbitrary hidden accessibility text. A match must be visible,
        have a rectangle, live in the lower part of the Chrome target, and contain the generated
        report filename/stem. The caller compares before/after paste sets so old text cannot
        produce a false pass.
        """
        wanted = {report_path.name.lower(), report_path.stem.lower()}
        window_rect = self._element_rect_tuple(window)
        if window_rect is None:
            return set()
        wl, wt, wr, wb = window_rect
        height = max(1, wb - wt)
        lower_threshold = wt + int(height * 0.45)
        matches: set[tuple[str, tuple[int, int, int, int]]] = set()
        try:
            descendants = window.descendants()
        except Exception:
            descendants = []
        for element in descendants:
            try:
                if not bool(element.is_visible()):
                    continue
            except Exception:
                continue
            rect = self._element_rect_tuple(element)
            if rect is None:
                continue
            left, top, right, bottom = rect
            if bottom < lower_threshold:
                continue
            text = self._element_text(element).strip()
            lowered = text.lower()
            if not lowered:
                continue
            if any(token and token in lowered for token in wanted):
                matches.add((text[:160], rect))
        return matches

    def _attachment_verified_after_paste(self, window: Any, report_path: Path, before_matches: set[tuple[str, tuple[int, int, int, int]]]) -> tuple[bool, int, int]:
        deadline = time.monotonic() + self.verify_timeout_seconds
        latest_after_count = 0
        while time.monotonic() < deadline:
            after_matches = self._visible_attachment_matches(window, report_path)
            latest_after_count = len(after_matches)
            new_matches = after_matches - before_matches
            if new_matches:
                return True, len(before_matches), latest_after_count
            time.sleep(0.35)
        return False, len(before_matches), latest_after_count
    def attach_by_keyboard(self, report_path: Path, *, edge_keyboard_scan: Mapping[str, Any]) -> KeyboardProbe:
        title = "PatchOps - ChatGPT - Google Chrome"
        if self.mode == "no-target":
            return KeyboardProbe(False, False, False, False, False, None, edge_keyboard_scan, ("fake target missing",))
        if self.mode == "clipboard-failed":
            return KeyboardProbe(True, True, False, False, False, title, edge_keyboard_scan, ("fake clipboard failed",))
        if self.mode == "paste-failed":
            return KeyboardProbe(True, True, True, False, False, title, edge_keyboard_scan, ("fake ctrl+v failed",))
        if self.mode == "not-verified":
            return KeyboardProbe(True, True, True, True, False, title, edge_keyboard_scan, ("fake attachment not verified",))
        return KeyboardProbe(True, True, True, True, True, title, edge_keyboard_scan, ())


class PywinautoKeyboardAdapter:
    provider_name = "pywinauto"

    def __init__(self, *, settle_seconds: float = 0.7, verify_timeout_seconds: float = 12.0) -> None:
        self.settle_seconds = settle_seconds
        self.verify_timeout_seconds = verify_timeout_seconds

    def _desktop(self) -> Any:
        try:
            from pywinauto import Desktop  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"pywinauto is required for live Chrome keyboard upload: {exc}") from exc
        return Desktop(backend="uia")

    def _keyboard(self) -> Any:
        try:
            from pywinauto import keyboard  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"pywinauto keyboard is required for live Chrome keyboard upload: {exc}") from exc
        return keyboard

    def _looks_like_chrome_target(self, window: Any) -> bool:
        title = (_safe_window_title(window) or "").lower()
        return any(token in title for token in CHROME_TITLE_TOKENS) and any(token in title for token in CHATGPT_TITLE_TOKENS)

    def _find_target_window(self) -> tuple[Any | None, tuple[str, ...]]:
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

    def _element_text(self, element: Any) -> str:
        parts: list[str] = []
        try:
            text = str(element.window_text() or "").strip()
            if text:
                parts.append(text)
        except Exception:
            pass
        try:
            name = str(element.element_info.name or "").strip()
            if name:
                parts.append(name)
        except Exception:
            pass
        return " ".join(parts).strip()

    def _visible_attachment_matches(self, window: Any, report_path: Path) -> set[tuple[str, tuple[int, int, int, int]]]:
        """Return visible lower-composer filename matches.

        This deliberately ignores arbitrary hidden accessibility text. A match must be visible,
        have a rectangle, live in the lower part of the Chrome target, and contain the generated
        report filename/stem. The caller compares before/after paste sets so old text cannot
        produce a false pass.
        """
        wanted = {report_path.name.lower(), report_path.stem.lower()}
        window_rect = self._element_rect_tuple(window)
        if window_rect is None:
            return set()
        wl, wt, wr, wb = window_rect
        height = max(1, wb - wt)
        lower_threshold = wt + int(height * 0.45)
        matches: set[tuple[str, tuple[int, int, int, int]]] = set()
        try:
            descendants = window.descendants()
        except Exception:
            descendants = []
        for element in descendants:
            try:
                if not bool(element.is_visible()):
                    continue
            except Exception:
                continue
            rect = self._element_rect_tuple(element)
            if rect is None:
                continue
            left, top, right, bottom = rect
            if bottom < lower_threshold:
                continue
            text = self._element_text(element).strip()
            lowered = text.lower()
            if not lowered:
                continue
            if any(token and token in lowered for token in wanted):
                matches.add((text[:160], rect))
        return matches

    def _attachment_verified_after_paste(self, window: Any, report_path: Path, before_matches: set[tuple[str, tuple[int, int, int, int]]]) -> tuple[bool, int, int]:
        deadline = time.monotonic() + self.verify_timeout_seconds
        latest_after_count = 0
        while time.monotonic() < deadline:
            after_matches = self._visible_attachment_matches(window, report_path)
            latest_after_count = len(after_matches)
            new_matches = after_matches - before_matches
            if new_matches:
                return True, len(before_matches), latest_after_count
            time.sleep(0.35)
        return False, len(before_matches), latest_after_count
    def attach_by_keyboard(self, report_path: Path, *, edge_keyboard_scan: Mapping[str, Any]) -> KeyboardProbe:
        window, issues = self._find_target_window()
        if window is None:
            return KeyboardProbe(False, False, False, False, False, None, edge_keyboard_scan, issues)
        title = _safe_window_title(window)
        try:
            window.set_focus()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return KeyboardProbe(True, False, False, False, False, title, edge_keyboard_scan, (f"Chrome focus failed: {exc}",))

        try:
            set_clipboard_file_drop(report_path)
        except Exception as exc:
            return KeyboardProbe(True, True, False, False, False, title, edge_keyboard_scan, (f"file clipboard setup failed: {exc}",))

        before_matches = self._visible_attachment_matches(window, report_path)
        try:
            self._keyboard().send_keys("^v", pause=0.05)
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return KeyboardProbe(True, True, True, False, False, title, edge_keyboard_scan, (f"Ctrl+V paste failed: {exc}",))

        verified, before_count, after_count = self._attachment_verified_after_paste(window, report_path, before_matches)
        if not verified:
            return KeyboardProbe(True, True, True, True, False, title, edge_keyboard_scan, (f"new visible lower-composer attachment was not verified after Ctrl+V file paste; before_matches={before_count}; after_matches={after_count}",))
        return KeyboardProbe(True, True, True, True, True, title, edge_keyboard_scan, ())

def _safe_window_title(window: Any) -> str | None:
    try:
        title = str(window.window_text() or "")
        return title or None
    except Exception:
        return None


def build_cf_hdrop_payload(path: Path) -> bytes:
    """Build a Windows CF_HDROP payload for one file path."""
    resolved = str(path.resolve(strict=False))
    dropfiles = struct.pack("<IiiII", 20, 0, 0, 0, 1)
    file_list = (resolved + "\0\0").encode("utf-16le")
    return dropfiles + file_list


def _last_winerror_message(prefix: str) -> str:
    error_code = ctypes.get_last_error()
    if error_code:
        return f"{prefix}: WinError {error_code}: {ctypes.FormatError(error_code)}"
    return prefix


def set_clipboard_file_drop(path: Path) -> None:
    """Place a file path on the Windows clipboard as CF_HDROP.

    This is the keyboard-paste equivalent of selecting a file in Explorer and pressing Ctrl+C,
    then pressing Ctrl+V in the focused ChatGPT composer. It uses explicit 64-bit-safe ctypes
    signatures for GlobalAlloc/GlobalLock/SetClipboardData.
    """
    resolved_path = path.resolve(strict=True)
    payload = build_cf_hdrop_payload(resolved_path)

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    CF_HDROP = 15
    GMEM_MOVEABLE = 0x0002
    GMEM_ZEROINIT = 0x0040

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

    if not user32.OpenClipboard(None):
        raise RuntimeError(_last_winerror_message("OpenClipboard failed"))

    handle: int | None = None
    try:
        if not user32.EmptyClipboard():
            raise RuntimeError(_last_winerror_message("EmptyClipboard failed"))
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, len(payload))
        if not handle:
            raise RuntimeError(_last_winerror_message("GlobalAlloc failed"))
        locked = kernel32.GlobalLock(handle)
        if not locked:
            raise RuntimeError(_last_winerror_message("GlobalLock failed"))
        try:
            ctypes.memmove(locked, payload, len(payload))
        finally:
            kernel32.GlobalUnlock(handle)
        transferred = user32.SetClipboardData(CF_HDROP, handle)
        if not transferred:
            raise RuntimeError(_last_winerror_message("SetClipboardData(CF_HDROP) failed"))
        handle = None
    finally:
        user32.CloseClipboard()
        if handle:
            kernel32.GlobalFree(handle)

def build_adapter(provider: str) -> KeyboardAdapter:
    if provider.startswith("fake-"):
        return FakeKeyboardAdapter(provider.removeprefix("fake-"))
    if provider == "pywinauto":
        return PywinautoKeyboardAdapter()
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
    probe: KeyboardProbe | None,
    provider: str,
    issues: Sequence[str],
) -> KeyboardUploadResult:
    title = probe.selected_window_title if probe else None
    edge_scan = probe.edge_keyboard_scan if probe else scan_edge_keyboard_shortcuts()
    safety = KeyboardUploadSafety(
        browser_action_performed=bool(probe and (probe.chrome_target_focused or probe.ctrl_v_pressed)),
        file_clipboard_written=bool(probe and probe.file_clipboard_written),
        keyboard_shortcut_used=bool(probe and probe.ctrl_v_pressed),
        ctrl_v_pressed=bool(probe and probe.ctrl_v_pressed),
        enter_key_pressed=False,
        file_picker_used=False,
        file_path_written=False,
        open_button_clicked=False,
        file_upload_attempted=bool(probe and probe.ctrl_v_pressed),
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
    return KeyboardUploadResult(
        ok=ok,
        result_label=result_label,
        patch_name=PATCH_NAME,
        selected_action="upload_self_report_keyboard_no_send",
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
        edge_keyboard_scan=edge_scan,
        keyboard_shortcuts_used=("CTRL+V",) if safety.ctrl_v_pressed else (),
        forbidden_keyboard_shortcuts_used=(),
        file_clipboard_written=safety.file_clipboard_written,
        ctrl_v_pressed=safety.ctrl_v_pressed,
        enter_key_pressed=safety.enter_key_pressed,
        file_picker_used=safety.file_picker_used,
        file_path_written=safety.file_path_written,
        open_button_clicked=safety.open_button_clicked,
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


def run_keyboard_upload_no_send(
    *,
    config_payload: Mapping[str, Any] | None,
    config_path: Path = DEFAULT_CONFIG_PATH,
    provider: str = "fake-ready",
    live_browser: bool,
    confirmation_text: str | None,
    self_report_path: str | None,
    expected_self_report_sha256: str | None = None,
    repo_root: Path | None = None,
) -> KeyboardUploadResult:
    config_ok, url_hash, target_hash, config_issues = validate_config(config_payload)
    confirmation_matched = confirmation_text == CONFIRM_CHROME_KEYBOARD_SELF_REPORT_UPLOAD_NO_SEND
    edge_scan = scan_edge_keyboard_shortcuts(repo_root)
    if not config_ok:
        label = BLOCKED_CHROME_KEYBOARD_CONFIG_MISSING
        if any("browser_lane" in issue for issue in config_issues):
            label = BLOCKED_CHROME_KEYBOARD_BROWSER_MISMATCH
        elif any("target_url" in issue for issue in config_issues):
            label = BLOCKED_CHROME_KEYBOARD_URL_INVALID
        return make_result(ok=False, result_label=label, config_path=config_path, status_chat_configured=False, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=live_browser, confirmation_text=confirmation_text, confirmation_matched=confirmation_matched, report_path=Path(self_report_path) if self_report_path else None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=KeyboardProbe(False, False, False, False, False, None, edge_scan), provider=provider, issues=config_issues)
    if confirmation_text is None:
        return make_result(ok=False, result_label=BLOCKED_CHROME_KEYBOARD_CONFIRMATION_REQUIRED, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=live_browser, confirmation_text=None, confirmation_matched=False, report_path=Path(self_report_path) if self_report_path else None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=KeyboardProbe(False, False, False, False, False, None, edge_scan), provider=provider, issues=("live keyboard upload confirmation is required",))
    if not confirmation_matched:
        return make_result(ok=False, result_label=BLOCKED_CHROME_KEYBOARD_CONFIRMATION_MISMATCH, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=live_browser, confirmation_text=confirmation_text, confirmation_matched=False, report_path=Path(self_report_path) if self_report_path else None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=KeyboardProbe(False, False, False, False, False, None, edge_scan), provider=provider, issues=(f"confirmation must exactly match {CONFIRM_CHROME_KEYBOARD_SELF_REPORT_UPLOAD_NO_SEND}",))
    if not live_browser:
        return make_result(ok=False, result_label=BLOCKED_CHROME_KEYBOARD_LIVE_BROWSER_REQUIRED, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=False, confirmation_text=confirmation_text, confirmation_matched=True, report_path=Path(self_report_path) if self_report_path else None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=KeyboardProbe(False, False, False, False, False, None, edge_scan), provider=provider, issues=("--live-browser is required",))
    if not self_report_path:
        return make_result(ok=False, result_label=BLOCKED_CHROME_KEYBOARD_REPORT_MISSING, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=None, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=KeyboardProbe(False, False, False, False, False, None, edge_scan), provider=provider, issues=("self report path is required",))
    report_path = Path(self_report_path)
    if not report_path.exists() or not report_path.is_file():
        return make_result(ok=False, result_label=BLOCKED_CHROME_KEYBOARD_REPORT_MISSING, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=report_path, report_sha256=expected_self_report_sha256, computed_report_sha256=None, probe=KeyboardProbe(False, False, False, False, False, None, edge_scan), provider=provider, issues=(f"self report not found: {report_path}",))
    computed_hash = sha256_file(report_path)
    if expected_self_report_sha256 and expected_self_report_sha256 != computed_hash:
        return make_result(ok=False, result_label=BLOCKED_CHROME_KEYBOARD_REPORT_HASH_MISMATCH, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=report_path, report_sha256=expected_self_report_sha256, computed_report_sha256=computed_hash, probe=KeyboardProbe(False, False, False, False, False, None, edge_scan), provider=provider, issues=("self report hash mismatch",))

    try:
        adapter = build_adapter(provider)
        probe = adapter.attach_by_keyboard(report_path, edge_keyboard_scan=edge_scan)
    except Exception as exc:
        return make_result(ok=False, result_label=BLOCKED_CHROME_KEYBOARD_TARGET_NOT_READY, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=report_path, report_sha256=computed_hash, computed_report_sha256=computed_hash, probe=KeyboardProbe(False, False, False, False, False, None, edge_scan), provider=provider, issues=(str(exc),))

    if not probe.chrome_target_ready or not probe.chrome_target_focused:
        label = BLOCKED_CHROME_KEYBOARD_TARGET_NOT_READY
    elif not probe.file_clipboard_written:
        label = BLOCKED_CHROME_KEYBOARD_CLIPBOARD_FAILED
    elif not probe.ctrl_v_pressed:
        label = BLOCKED_CHROME_KEYBOARD_PASTE_FAILED
    elif not probe.attachment_verified:
        label = BLOCKED_CHROME_KEYBOARD_ATTACHMENT_NOT_VERIFIED
    else:
        label = PASS_CHROME_SELF_REPORT_KEYBOARD_ATTACHED_NO_SEND

    return make_result(ok=label == PASS_CHROME_SELF_REPORT_KEYBOARD_ATTACHED_NO_SEND, result_label=label, config_path=config_path, status_chat_configured=True, status_chat_url_hash_or_redacted=url_hash, target_url_sha256=target_hash, live_browser=True, confirmation_text=confirmation_text, confirmation_matched=True, report_path=report_path, report_sha256=computed_hash, computed_report_sha256=computed_hash, probe=probe, provider=adapter.provider_name, issues=probe.issues)


def render_text(result: KeyboardUploadResult) -> str:
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
        f"file_clipboard_written: {str(result.file_clipboard_written).lower()}",
        f"ctrl_v_pressed: {str(result.ctrl_v_pressed).lower()}",
        f"enter_key_pressed: {str(result.enter_key_pressed).lower()}",
        f"file_picker_used: {str(result.file_picker_used).lower()}",
        f"file_path_written: {str(result.file_path_written).lower()}",
        f"open_button_clicked: {str(result.open_button_clicked).lower()}",
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
        f"edge_keyboard_scan: {json.dumps(result.edge_keyboard_scan, sort_keys=True)}",
        f"created_at: {result.created_at}",
    ]
    if result.issues:
        lines.append("issues:")
        for issue in result.issues:
            lines.append(f"- {issue}")
    else:
        lines.append("issues: none")
    return "\n".join(lines) + "\n"


def write_evidence(result: KeyboardUploadResult, *, json_output_path: Path = DEFAULT_JSON_OUTPUT_PATH, txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_text(result), encoding="utf-8")
    return json_output_path, txt_output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Keyboard-paste a self report file into Chrome ChatGPT without Enter or Send")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-clipboard-failed", "fake-paste-failed", "fake-not-verified", "pywinauto"), default="fake-ready")
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
    result = run_keyboard_upload_no_send(
        config_payload=config_payload,
        config_path=config_path,
        provider=args.provider,
        live_browser=bool(args.live_browser),
        confirmation_text=args.confirm_live_browser_text,
        self_report_path=args.self_report_path,
        expected_self_report_sha256=args.self_report_sha256,
        repo_root=Path.cwd(),
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