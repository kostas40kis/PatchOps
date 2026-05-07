from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol, Sequence

PATCH_NAME = "u3_c30_chrome_status_message_send_test"

ACTION_POST_STATUS_MESSAGE = "post_status_message"
CONFIRM_CHROME_STATUS_MESSAGE_NO_SEND = "PATCHOPS_CONFIRM_CHROME_STATUS_MESSAGE_NO_SEND"
CONFIRM_CHROME_STATUS_MESSAGE_SEND = "PATCHOPS_CONFIRM_CHROME_STATUS_MESSAGE_SEND"

PASS_CHROME_STATUS_MESSAGE_COMPOSER_READY_NO_SEND = "PASS_CHROME_STATUS_MESSAGE_COMPOSER_READY_NO_SEND"
PASS_CHROME_STATUS_MESSAGE_SENT = "PASS_CHROME_STATUS_MESSAGE_SENT"
BLOCKED_CHROME_STATUS_TARGET_NOT_READY = "BLOCKED_CHROME_STATUS_TARGET_NOT_READY"
BLOCKED_STATUS_MESSAGE_MISMATCH = "BLOCKED_STATUS_MESSAGE_MISMATCH"
BLOCKED_SEND_RISK = "BLOCKED_SEND_RISK"
BLOCKED_CHROME_STATUS_SEND_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_STATUS_SEND_CONFIRMATION_REQUIRED"
BLOCKED_CHROME_STATUS_SEND_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_STATUS_SEND_CONFIRMATION_MISMATCH"
BLOCKED_CHROME_STATUS_SEND_NOT_VERIFIED = "BLOCKED_CHROME_STATUS_SEND_NOT_VERIFIED"

DEFAULT_ARMED_GATE_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_reporter_armed_gate.json")
DEFAULT_NO_SEND_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_status_message_no_send_probe.json")
DEFAULT_NO_SEND_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_status_message_no_send_probe.txt")
DEFAULT_SEND_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_status_message_send_test.json")
DEFAULT_SEND_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_status_message_send_test.txt")

CHATGPT_TITLE_TOKENS = ("chatgpt", "openai")
COMPOSER_NAME_TOKENS = (
    "message chatgpt",
    "message",
    "ask anything",
    "send a message",
    "prompt",
)
SEND_BUTTON_NAME_TOKENS = ("send", "submit")


@dataclass(frozen=True)
class ChromeStatusReporterSafety:
    browser_action_performed: bool = False
    chatgpt_submit_performed: bool = False
    operator_report_uploaded: bool = False
    status_message_posted: bool = False
    send_button_pressed: bool = False
    file_upload_attempted: bool = False
    raw_conversation_text_available: bool = False
    selenium_used: bool = False
    webdriver_used: bool = False
    browser_dom_automation_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False


@dataclass(frozen=True)
class ChromeStatusMessageNoSendProbeResult:
    ok: bool
    result_label: str
    patch_name: str
    selected_action: str
    browser_lane: str
    pass_status_message: str
    pass_status_message_sha256: str
    live_browser: bool
    stop_before_send: bool
    confirmation_text_supplied: str | None
    confirmation_matched: bool
    chrome_target_ready: bool
    chrome_target_focused: bool
    composer_focus_attempted: bool
    composer_text_placed: bool
    composer_text_verified: bool
    send_risk_detected: bool
    browser_action_performed: bool
    chatgpt_submit_performed: bool
    operator_report_uploaded: bool
    status_message_posted: bool
    send_button_pressed: bool
    raw_conversation_text_available: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    cloudflare_bypass_attempted: bool
    captcha_bypass_attempted: bool
    target_window_count: int = 0
    matching_target_count: int = 0
    selected_target_title_hash: str | None = None
    selected_target_title_length: int | None = None
    composer_candidate_count: int = 0
    provider: str = "fake-ready"
    issues: tuple[str, ...] = ()
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    safety: ChromeStatusReporterSafety = field(default_factory=ChromeStatusReporterSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        return payload


@dataclass(frozen=True)
class ChromeStatusMessageSendResult:
    ok: bool
    result_label: str
    patch_name: str
    selected_action: str
    browser_lane: str
    pass_status_message: str
    pass_status_message_sha256: str
    live_browser: bool
    send_confirmation_text_supplied: str | None
    send_confirmation_matched: bool
    no_send_probe_required: bool
    no_send_probe_ok: bool
    chrome_target_ready: bool
    chrome_target_focused: bool
    composer_text_verified_before_send: bool
    send_attempted: bool
    send_verified: bool
    browser_action_performed: bool
    chatgpt_submit_performed: bool
    operator_report_uploaded: bool
    status_message_posted: bool
    send_button_pressed: bool
    raw_conversation_text_available: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    cloudflare_bypass_attempted: bool
    captcha_bypass_attempted: bool
    target_window_count: int = 0
    matching_target_count: int = 0
    selected_target_title_hash: str | None = None
    selected_target_title_length: int | None = None
    composer_candidate_count: int = 0
    provider: str = "fake-ready"
    issues: tuple[str, ...] = ()
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    safety: ChromeStatusReporterSafety = field(default_factory=ChromeStatusReporterSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        return payload


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def expected_pass_status_message(patch_name: str) -> str:
    return f"{patch_name} has passed"


def message_from_armed_gate_payload(payload: dict[str, Any], *, fallback_patch_name: str = PATCH_NAME) -> tuple[str, str, str, str]:
    patch_name = normalize_optional_text(payload.get("patch_name")) or fallback_patch_name
    selected_action = normalize_optional_text(payload.get("selected_action")) or ACTION_POST_STATUS_MESSAGE
    browser_lane = (normalize_optional_text(payload.get("browser_lane")) or "chrome").lower()
    pass_status_message = normalize_optional_text(payload.get("pass_status_message")) or expected_pass_status_message(patch_name)
    return patch_name, selected_action, browser_lane, pass_status_message


def read_expected_message_from_gate(path: Path, *, fallback_patch_name: str = PATCH_NAME) -> tuple[str, str, str, str]:
    if not path.exists():
        return fallback_patch_name, ACTION_POST_STATUS_MESSAGE, "chrome", expected_pass_status_message(fallback_patch_name)
    return message_from_armed_gate_payload(load_json_object(path), fallback_patch_name=fallback_patch_name)


@dataclass(frozen=True)
class TargetProbe:
    ready: bool
    focused: bool
    target_window_count: int
    matching_target_count: int
    selected_target_title: str | None
    composer_candidate_count: int
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class ComposerPlacement:
    focus_attempted: bool
    text_placed: bool
    text_verified: bool
    readback_text: str | None
    send_risk_detected: bool
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class SendAttempt:
    attempted: bool
    verified: bool
    send_button_pressed: bool
    chatgpt_submit_performed: bool
    status_message_posted: bool
    send_risk_detected: bool
    issues: tuple[str, ...] = ()


class ChromeStatusMessageAdapter(Protocol):
    provider_name: str

    def focus_target(self) -> TargetProbe:
        ...

    def place_message_no_send(self, message: str) -> ComposerPlacement:
        ...

    def send_prepared_message(self, message: str) -> SendAttempt:
        ...


class FakeChromeStatusMessageAdapter:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.provider_name = f"fake-{mode}"
        self.placed_text: str | None = None
        self.sent_text: str | None = None

    def focus_target(self) -> TargetProbe:
        if self.mode == "no-target":
            return TargetProbe(False, False, 0, 0, None, 0, ("no fake Chrome target",))
        if self.mode == "ambiguous-target":
            return TargetProbe(False, False, 2, 2, None, 0, ("multiple fake Chrome targets",))
        return TargetProbe(True, True, 1, 1, "ChatGPT - Google Chrome", 1, ())

    def place_message_no_send(self, message: str) -> ComposerPlacement:
        if self.mode == "send-risk":
            return ComposerPlacement(True, False, False, None, True, ("fake send risk detected",))
        if self.mode == "mismatch":
            self.placed_text = f"{message} extra"
            return ComposerPlacement(True, True, False, self.placed_text, False, ("fake composer text mismatch",))
        self.placed_text = message
        return ComposerPlacement(True, True, True, self.placed_text, False, ())

    def send_prepared_message(self, message: str) -> SendAttempt:
        if self.mode == "send-fails":
            return SendAttempt(True, False, True, False, False, False, ("fake send verification failed",))
        if self.placed_text != message:
            return SendAttempt(False, False, False, False, False, True, ("prepared text mismatch before fake send",))
        self.sent_text = message
        return SendAttempt(True, True, True, True, True, False, ())


class PywinautoChromeStatusMessageAdapter:
    provider_name = "pywinauto"

    def __init__(self, *, settle_seconds: float = 0.4) -> None:
        self.settle_seconds = settle_seconds
        self._selected_window: Any | None = None
        self._selected_composer: Any | None = None
        self._last_prepared_message: str | None = None

    def _desktop(self) -> Any:
        try:
            from pywinauto import Desktop  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"pywinauto is required for live Chrome probing: {exc}") from exc
        return Desktop(backend="uia")

    def _looks_like_chrome_window(self, window: Any) -> bool:
        try:
            title = str(window.window_text() or "")
        except Exception:
            title = ""
        lowered = title.lower()
        return "chrome" in lowered and any(token in lowered for token in CHATGPT_TITLE_TOKENS)

    def focus_target(self) -> TargetProbe:
        try:
            desktop = self._desktop()
            windows = list(desktop.windows())
        except Exception as exc:
            return TargetProbe(False, False, 0, 0, None, 0, (str(exc),))

        matches = [window for window in windows if self._looks_like_chrome_window(window)]
        if not matches:
            return TargetProbe(False, False, len(windows), 0, None, 0, ("no visible Chrome ChatGPT target window",))
        if len(matches) > 1:
            return TargetProbe(False, False, len(windows), len(matches), None, 0, ("multiple Chrome ChatGPT target windows",))

        selected = matches[0]
        try:
            selected.set_focus()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return TargetProbe(False, False, len(windows), 1, _safe_window_title(selected), 0, (f"Chrome focus failed: {exc}",))

        self._selected_window = selected
        composer_candidates = self._find_composer_candidates(selected)
        return TargetProbe(True, True, len(windows), 1, _safe_window_title(selected), len(composer_candidates), ())

    def _find_composer_candidates(self, window: Any) -> list[Any]:
        candidates: list[Any] = []
        try:
            descendants = window.descendants()
        except Exception:
            return candidates
        for element in descendants:
            try:
                control_type = str(element.element_info.control_type or "").lower()
                name = str(element.window_text() or element.element_info.name or "").strip()
                lowered = name.lower()
                enabled = bool(element.is_enabled())
                visible = bool(element.is_visible())
            except Exception:
                continue
            if enabled and visible and control_type in {"edit", "document"} and any(token in lowered for token in COMPOSER_NAME_TOKENS):
                candidates.append(element)
        return candidates

    def _find_send_button_candidates(self, window: Any) -> list[Any]:
        candidates: list[Any] = []
        try:
            descendants = window.descendants()
        except Exception:
            return candidates
        for element in descendants:
            try:
                control_type = str(element.element_info.control_type or "").lower()
                name = str(element.window_text() or element.element_info.name or "").strip()
                lowered = name.lower()
                enabled = bool(element.is_enabled())
                visible = bool(element.is_visible())
            except Exception:
                continue
            if enabled and visible and control_type == "button" and any(token == lowered or token in lowered for token in SEND_BUTTON_NAME_TOKENS):
                candidates.append(element)
        return candidates

    def place_message_no_send(self, message: str) -> ComposerPlacement:
        issues: list[str] = []
        if self._selected_window is None:
            return ComposerPlacement(False, False, False, None, False, ("Chrome target was not focused first",))
        candidates = self._find_composer_candidates(self._selected_window)
        if not candidates:
            return ComposerPlacement(False, False, False, None, False, ("no safe ChatGPT composer candidate",))
        if len(candidates) > 1:
            return ComposerPlacement(False, False, False, None, True, ("multiple composer candidates; refusing to type",))
        composer = candidates[0]
        self._selected_composer = composer
        try:
            composer.set_focus()
            composer.click_input()
            time.sleep(self.settle_seconds)
            focus_attempted = True
        except Exception as exc:
            return ComposerPlacement(True, False, False, None, False, (f"composer focus failed: {exc}",))
        try:
            _set_windows_clipboard_text(message)
            try:
                from pywinauto.keyboard import send_keys  # type: ignore
            except Exception as exc:  # pragma: no cover
                raise RuntimeError(f"pywinauto keyboard helper unavailable: {exc}") from exc
            send_keys("^v", pause=0.05)
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return ComposerPlacement(focus_attempted, False, False, None, False, (f"message paste failed: {exc}",))
        readback = _try_read_element_text(composer)
        verified = readback == message
        if verified:
            self._last_prepared_message = message
        else:
            issues.append("composer text readback did not exactly match the expected message")
        return ComposerPlacement(focus_attempted, True, verified, readback, False, tuple(issues))

    def send_prepared_message(self, message: str) -> SendAttempt:
        if self._selected_window is None or self._selected_composer is None:
            return SendAttempt(False, False, False, False, False, True, ("target/composer not prepared before send",))
        if self._last_prepared_message != message:
            return SendAttempt(False, False, False, False, False, True, ("prepared message mismatch before send",))
        try:
            self._selected_composer.set_focus()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return SendAttempt(False, False, False, False, False, True, (f"failed to refocus composer before send: {exc}",))
        buttons = self._find_send_button_candidates(self._selected_window)
        if len(buttons) > 1:
            return SendAttempt(False, False, False, False, False, True, ("multiple enabled send-like buttons; refusing to send",))
        try:
            if len(buttons) == 1:
                buttons[0].click_input()
                send_button_pressed = True
            else:
                try:
                    from pywinauto.keyboard import send_keys  # type: ignore
                except Exception as exc:  # pragma: no cover
                    raise RuntimeError(f"pywinauto keyboard helper unavailable: {exc}") from exc
                send_keys("{ENTER}", pause=0.05)
                send_button_pressed = False
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return SendAttempt(True, False, send_button_pressed if "send_button_pressed" in locals() else False, False, False, False, (f"send action failed: {exc}",))
        after_text = _try_read_element_text(self._selected_composer)
        verified = after_text is None or after_text == "" or after_text != message
        if not verified:
            return SendAttempt(True, False, send_button_pressed, False, False, False, ("composer still contains the exact message after send",))
        return SendAttempt(True, True, send_button_pressed, True, True, False, ())


def _safe_window_title(window: Any) -> str | None:
    try:
        title = str(window.window_text() or "")
        return title or None
    except Exception:
        return None


def _try_read_element_text(element: Any) -> str | None:
    readers = []
    try:
        readers.append(lambda: element.get_value())
    except Exception:
        pass
    try:
        readers.append(lambda: element.window_text())
    except Exception:
        pass
    try:
        readers.append(lambda: element.iface_value.CurrentValue)
    except Exception:
        pass
    for reader in readers:
        try:
            value = reader()
        except Exception:
            continue
        text = normalize_optional_text(value)
        if text is not None:
            return text
    return None


def _set_windows_clipboard_text(text: str) -> None:
    if not hasattr(ctypes, "windll"):
        raise RuntimeError("Windows clipboard is unavailable on this platform")
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
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


def build_adapter(provider: str) -> ChromeStatusMessageAdapter:
    if provider.startswith("fake-"):
        return FakeChromeStatusMessageAdapter(provider.removeprefix("fake-"))
    if provider == "pywinauto":
        return PywinautoChromeStatusMessageAdapter()
    raise ValueError(f"Unknown provider: {provider}")


def _make_no_send_result(
    *,
    ok: bool,
    result_label: str,
    patch_name: str,
    selected_action: str,
    browser_lane: str,
    pass_status_message: str,
    live_browser: bool,
    stop_before_send: bool,
    confirmation_text_supplied: str | None,
    confirmation_matched: bool,
    chrome_target_ready: bool,
    chrome_target_focused: bool,
    composer_focus_attempted: bool,
    composer_text_placed: bool,
    composer_text_verified: bool,
    send_risk_detected: bool,
    provider: str,
    target_window_count: int = 0,
    matching_target_count: int = 0,
    selected_target_title: str | None = None,
    composer_candidate_count: int = 0,
    issues: Sequence[str] = (),
) -> ChromeStatusMessageNoSendProbeResult:
    safety = ChromeStatusReporterSafety(
        browser_action_performed=bool(chrome_target_focused or composer_focus_attempted or composer_text_placed),
        chatgpt_submit_performed=False,
        operator_report_uploaded=False,
        status_message_posted=False,
        send_button_pressed=False,
        file_upload_attempted=False,
        raw_conversation_text_available=False,
        selenium_used=False,
        webdriver_used=False,
        browser_dom_automation_used=False,
        cloudflare_bypass_attempted=False,
        captcha_bypass_attempted=False,
        conversation_text_logged=False,
        random_page_click_performed=False,
    )
    return ChromeStatusMessageNoSendProbeResult(
        ok=ok,
        result_label=result_label,
        patch_name=patch_name,
        selected_action=selected_action,
        browser_lane=browser_lane,
        pass_status_message=pass_status_message,
        pass_status_message_sha256=sha256_text(pass_status_message),
        live_browser=live_browser,
        stop_before_send=stop_before_send,
        confirmation_text_supplied=confirmation_text_supplied,
        confirmation_matched=confirmation_matched,
        chrome_target_ready=chrome_target_ready,
        chrome_target_focused=chrome_target_focused,
        composer_focus_attempted=composer_focus_attempted,
        composer_text_placed=composer_text_placed,
        composer_text_verified=composer_text_verified,
        send_risk_detected=send_risk_detected,
        browser_action_performed=safety.browser_action_performed,
        chatgpt_submit_performed=safety.chatgpt_submit_performed,
        operator_report_uploaded=safety.operator_report_uploaded,
        status_message_posted=safety.status_message_posted,
        send_button_pressed=safety.send_button_pressed,
        raw_conversation_text_available=safety.raw_conversation_text_available,
        selenium_used=safety.selenium_used,
        webdriver_used=safety.webdriver_used,
        browser_dom_automation_used=safety.browser_dom_automation_used,
        cloudflare_bypass_attempted=safety.cloudflare_bypass_attempted,
        captcha_bypass_attempted=safety.captcha_bypass_attempted,
        target_window_count=target_window_count,
        matching_target_count=matching_target_count,
        selected_target_title_hash=sha256_text(selected_target_title) if selected_target_title else None,
        selected_target_title_length=len(selected_target_title) if selected_target_title else None,
        composer_candidate_count=composer_candidate_count,
        provider=provider,
        issues=tuple(issues),
        safety=safety,
    )


def _validate_common_message_inputs(
    *,
    patch_name: str,
    selected_action: str,
    browser_lane: str,
    pass_status_message: str,
) -> list[str]:
    issues: list[str] = []
    if selected_action != ACTION_POST_STATUS_MESSAGE:
        issues.append(f"selected_action must be {ACTION_POST_STATUS_MESSAGE}")
    if browser_lane != "chrome":
        issues.append("browser_lane must be chrome")
    expected_message = expected_pass_status_message(patch_name)
    if pass_status_message != expected_message:
        issues.append("pass_status_message must exactly equal '<patch_name> has passed'")
    return issues


def run_chrome_status_message_no_send_probe(
    *,
    patch_name: str,
    selected_action: str,
    browser_lane: str,
    pass_status_message: str,
    live_browser: bool,
    confirmation_text: str | None,
    stop_before_send: bool,
    provider: str,
) -> ChromeStatusMessageNoSendProbeResult:
    hard_gate_issues: list[str] = []
    confirmation_matched = confirmation_text == CONFIRM_CHROME_STATUS_MESSAGE_NO_SEND
    if not live_browser:
        hard_gate_issues.append("--live-browser is required for C29/C30")
    if not confirmation_matched:
        hard_gate_issues.append(f"confirmation must exactly match {CONFIRM_CHROME_STATUS_MESSAGE_NO_SEND}")
    if not stop_before_send:
        hard_gate_issues.append("--stop-before-send is required for no-send probe")
    if hard_gate_issues:
        return _make_no_send_result(
            ok=False,
            result_label=BLOCKED_SEND_RISK,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=confirmation_matched,
            chrome_target_ready=False,
            chrome_target_focused=False,
            composer_focus_attempted=False,
            composer_text_placed=False,
            composer_text_verified=False,
            send_risk_detected=True,
            provider=provider,
            issues=hard_gate_issues,
        )

    message_issues = _validate_common_message_inputs(
        patch_name=patch_name,
        selected_action=selected_action,
        browser_lane=browser_lane,
        pass_status_message=pass_status_message,
    )
    if message_issues:
        return _make_no_send_result(
            ok=False,
            result_label=BLOCKED_STATUS_MESSAGE_MISMATCH,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=confirmation_matched,
            chrome_target_ready=False,
            chrome_target_focused=False,
            composer_focus_attempted=False,
            composer_text_placed=False,
            composer_text_verified=False,
            send_risk_detected=True,
            provider=provider,
            issues=message_issues,
        )

    try:
        adapter = build_adapter(provider)
    except Exception as exc:
        return _make_no_send_result(
            ok=False,
            result_label=BLOCKED_CHROME_STATUS_TARGET_NOT_READY,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=confirmation_matched,
            chrome_target_ready=False,
            chrome_target_focused=False,
            composer_focus_attempted=False,
            composer_text_placed=False,
            composer_text_verified=False,
            send_risk_detected=False,
            provider=provider,
            issues=(str(exc),),
        )
    target = adapter.focus_target()
    if not target.ready or not target.focused:
        return _make_no_send_result(
            ok=False,
            result_label=BLOCKED_CHROME_STATUS_TARGET_NOT_READY,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=confirmation_matched,
            chrome_target_ready=target.ready,
            chrome_target_focused=target.focused,
            composer_focus_attempted=False,
            composer_text_placed=False,
            composer_text_verified=False,
            send_risk_detected=False,
            target_window_count=target.target_window_count,
            matching_target_count=target.matching_target_count,
            selected_target_title=target.selected_target_title,
            composer_candidate_count=target.composer_candidate_count,
            provider=adapter.provider_name,
            issues=target.issues,
        )
    placement = adapter.place_message_no_send(pass_status_message)
    combined_issues = tuple(target.issues + placement.issues)
    if placement.send_risk_detected:
        return _make_no_send_result(
            ok=False,
            result_label=BLOCKED_SEND_RISK,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=confirmation_matched,
            chrome_target_ready=target.ready,
            chrome_target_focused=target.focused,
            composer_focus_attempted=placement.focus_attempted,
            composer_text_placed=placement.text_placed,
            composer_text_verified=placement.text_verified,
            send_risk_detected=True,
            target_window_count=target.target_window_count,
            matching_target_count=target.matching_target_count,
            selected_target_title=target.selected_target_title,
            composer_candidate_count=target.composer_candidate_count,
            provider=adapter.provider_name,
            issues=combined_issues,
        )
    if not placement.text_placed or not placement.text_verified:
        return _make_no_send_result(
            ok=False,
            result_label=BLOCKED_STATUS_MESSAGE_MISMATCH,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=confirmation_matched,
            chrome_target_ready=target.ready,
            chrome_target_focused=target.focused,
            composer_focus_attempted=placement.focus_attempted,
            composer_text_placed=placement.text_placed,
            composer_text_verified=placement.text_verified,
            send_risk_detected=False,
            target_window_count=target.target_window_count,
            matching_target_count=target.matching_target_count,
            selected_target_title=target.selected_target_title,
            composer_candidate_count=target.composer_candidate_count,
            provider=adapter.provider_name,
            issues=combined_issues,
        )
    return _make_no_send_result(
        ok=True,
        result_label=PASS_CHROME_STATUS_MESSAGE_COMPOSER_READY_NO_SEND,
        patch_name=patch_name,
        selected_action=selected_action,
        browser_lane=browser_lane,
        pass_status_message=pass_status_message,
        live_browser=live_browser,
        stop_before_send=stop_before_send,
        confirmation_text_supplied=confirmation_text,
        confirmation_matched=confirmation_matched,
        chrome_target_ready=True,
        chrome_target_focused=True,
        composer_focus_attempted=placement.focus_attempted,
        composer_text_placed=True,
        composer_text_verified=True,
        send_risk_detected=False,
        target_window_count=target.target_window_count,
        matching_target_count=target.matching_target_count,
        selected_target_title=target.selected_target_title,
        composer_candidate_count=target.composer_candidate_count,
        provider=adapter.provider_name,
        issues=combined_issues,
    )


def _make_send_result(
    *,
    ok: bool,
    result_label: str,
    patch_name: str,
    selected_action: str,
    browser_lane: str,
    pass_status_message: str,
    live_browser: bool,
    send_confirmation_text_supplied: str | None,
    send_confirmation_matched: bool,
    no_send_probe_required: bool,
    no_send_probe_ok: bool,
    chrome_target_ready: bool,
    chrome_target_focused: bool,
    composer_text_verified_before_send: bool,
    send_attempted: bool,
    send_verified: bool,
    send_button_pressed: bool,
    chatgpt_submit_performed: bool,
    status_message_posted: bool,
    provider: str,
    target_window_count: int = 0,
    matching_target_count: int = 0,
    selected_target_title: str | None = None,
    composer_candidate_count: int = 0,
    issues: Sequence[str] = (),
) -> ChromeStatusMessageSendResult:
    safety = ChromeStatusReporterSafety(
        browser_action_performed=bool(chrome_target_focused or composer_text_verified_before_send or send_attempted),
        chatgpt_submit_performed=chatgpt_submit_performed,
        operator_report_uploaded=False,
        status_message_posted=status_message_posted,
        send_button_pressed=send_button_pressed,
        file_upload_attempted=False,
        raw_conversation_text_available=False,
        selenium_used=False,
        webdriver_used=False,
        browser_dom_automation_used=False,
        cloudflare_bypass_attempted=False,
        captcha_bypass_attempted=False,
        conversation_text_logged=False,
        random_page_click_performed=False,
    )
    return ChromeStatusMessageSendResult(
        ok=ok,
        result_label=result_label,
        patch_name=patch_name,
        selected_action=selected_action,
        browser_lane=browser_lane,
        pass_status_message=pass_status_message,
        pass_status_message_sha256=sha256_text(pass_status_message),
        live_browser=live_browser,
        send_confirmation_text_supplied=send_confirmation_text_supplied,
        send_confirmation_matched=send_confirmation_matched,
        no_send_probe_required=no_send_probe_required,
        no_send_probe_ok=no_send_probe_ok,
        chrome_target_ready=chrome_target_ready,
        chrome_target_focused=chrome_target_focused,
        composer_text_verified_before_send=composer_text_verified_before_send,
        send_attempted=send_attempted,
        send_verified=send_verified,
        browser_action_performed=safety.browser_action_performed,
        chatgpt_submit_performed=safety.chatgpt_submit_performed,
        operator_report_uploaded=safety.operator_report_uploaded,
        status_message_posted=safety.status_message_posted,
        send_button_pressed=safety.send_button_pressed,
        raw_conversation_text_available=safety.raw_conversation_text_available,
        selenium_used=safety.selenium_used,
        webdriver_used=safety.webdriver_used,
        browser_dom_automation_used=safety.browser_dom_automation_used,
        cloudflare_bypass_attempted=safety.cloudflare_bypass_attempted,
        captcha_bypass_attempted=safety.captcha_bypass_attempted,
        target_window_count=target_window_count,
        matching_target_count=matching_target_count,
        selected_target_title_hash=sha256_text(selected_target_title) if selected_target_title else None,
        selected_target_title_length=len(selected_target_title) if selected_target_title else None,
        composer_candidate_count=composer_candidate_count,
        provider=provider,
        issues=tuple(issues),
        safety=safety,
    )


def run_chrome_status_message_send_test(
    *,
    patch_name: str,
    selected_action: str,
    browser_lane: str,
    pass_status_message: str,
    live_browser: bool,
    no_send_confirmation_text: str | None,
    send_confirmation_text: str | None,
    provider: str,
) -> ChromeStatusMessageSendResult:
    if not live_browser:
        return _make_send_result(
            ok=False,
            result_label=BLOCKED_SEND_RISK,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=send_confirmation_text == CONFIRM_CHROME_STATUS_MESSAGE_SEND,
            no_send_probe_required=True,
            no_send_probe_ok=False,
            chrome_target_ready=False,
            chrome_target_focused=False,
            composer_text_verified_before_send=False,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            provider=provider,
            issues=("--live-browser is required for C30",),
        )

    if send_confirmation_text is None:
        return _make_send_result(
            ok=False,
            result_label=BLOCKED_CHROME_STATUS_SEND_CONFIRMATION_REQUIRED,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=False,
            no_send_probe_required=True,
            no_send_probe_ok=False,
            chrome_target_ready=False,
            chrome_target_focused=False,
            composer_text_verified_before_send=False,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            provider=provider,
            issues=("send confirmation is required",),
        )

    send_confirmation_matched = send_confirmation_text == CONFIRM_CHROME_STATUS_MESSAGE_SEND
    if not send_confirmation_matched:
        return _make_send_result(
            ok=False,
            result_label=BLOCKED_CHROME_STATUS_SEND_CONFIRMATION_MISMATCH,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=False,
            no_send_probe_required=True,
            no_send_probe_ok=False,
            chrome_target_ready=False,
            chrome_target_focused=False,
            composer_text_verified_before_send=False,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            provider=provider,
            issues=(f"send confirmation must exactly match {CONFIRM_CHROME_STATUS_MESSAGE_SEND}",),
        )

    message_issues = _validate_common_message_inputs(
        patch_name=patch_name,
        selected_action=selected_action,
        browser_lane=browser_lane,
        pass_status_message=pass_status_message,
    )
    if message_issues:
        return _make_send_result(
            ok=False,
            result_label=BLOCKED_STATUS_MESSAGE_MISMATCH,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=True,
            no_send_probe_required=True,
            no_send_probe_ok=False,
            chrome_target_ready=False,
            chrome_target_focused=False,
            composer_text_verified_before_send=False,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            provider=provider,
            issues=message_issues,
        )

    no_send = run_chrome_status_message_no_send_probe(
        patch_name=patch_name,
        selected_action=selected_action,
        browser_lane=browser_lane,
        pass_status_message=pass_status_message,
        live_browser=live_browser,
        confirmation_text=no_send_confirmation_text,
        stop_before_send=True,
        provider=provider,
    )
    if not no_send.ok:
        return _make_send_result(
            ok=False,
            result_label=no_send.result_label,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=True,
            no_send_probe_required=True,
            no_send_probe_ok=False,
            chrome_target_ready=no_send.chrome_target_ready,
            chrome_target_focused=no_send.chrome_target_focused,
            composer_text_verified_before_send=no_send.composer_text_verified,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            target_window_count=no_send.target_window_count,
            matching_target_count=no_send.matching_target_count,
            selected_target_title=None,
            composer_candidate_count=no_send.composer_candidate_count,
            provider=no_send.provider,
            issues=no_send.issues,
        )

    adapter = build_adapter(provider)
    target = adapter.focus_target()
    if not target.ready or not target.focused:
        return _make_send_result(
            ok=False,
            result_label=BLOCKED_CHROME_STATUS_TARGET_NOT_READY,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=True,
            no_send_probe_required=True,
            no_send_probe_ok=True,
            chrome_target_ready=target.ready,
            chrome_target_focused=target.focused,
            composer_text_verified_before_send=False,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            target_window_count=target.target_window_count,
            matching_target_count=target.matching_target_count,
            selected_target_title=target.selected_target_title,
            composer_candidate_count=target.composer_candidate_count,
            provider=adapter.provider_name,
            issues=target.issues,
        )

    placement = adapter.place_message_no_send(pass_status_message)
    if placement.send_risk_detected or not placement.text_placed or not placement.text_verified:
        return _make_send_result(
            ok=False,
            result_label=BLOCKED_SEND_RISK if placement.send_risk_detected else BLOCKED_STATUS_MESSAGE_MISMATCH,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=live_browser,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=True,
            no_send_probe_required=True,
            no_send_probe_ok=True,
            chrome_target_ready=target.ready,
            chrome_target_focused=target.focused,
            composer_text_verified_before_send=placement.text_verified,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            target_window_count=target.target_window_count,
            matching_target_count=target.matching_target_count,
            selected_target_title=target.selected_target_title,
            composer_candidate_count=target.composer_candidate_count,
            provider=adapter.provider_name,
            issues=tuple(target.issues + placement.issues),
        )

    send = adapter.send_prepared_message(pass_status_message)
    if send.send_risk_detected:
        label = BLOCKED_SEND_RISK
    elif not send.attempted or not send.verified:
        label = BLOCKED_CHROME_STATUS_SEND_NOT_VERIFIED
    else:
        label = PASS_CHROME_STATUS_MESSAGE_SENT

    return _make_send_result(
        ok=send.verified and send.chatgpt_submit_performed and send.status_message_posted,
        result_label=label,
        patch_name=patch_name,
        selected_action=selected_action,
        browser_lane=browser_lane,
        pass_status_message=pass_status_message,
        live_browser=live_browser,
        send_confirmation_text_supplied=send_confirmation_text,
        send_confirmation_matched=True,
        no_send_probe_required=True,
        no_send_probe_ok=True,
        chrome_target_ready=target.ready,
        chrome_target_focused=target.focused,
        composer_text_verified_before_send=placement.text_verified,
        send_attempted=send.attempted,
        send_verified=send.verified,
        send_button_pressed=send.send_button_pressed,
        chatgpt_submit_performed=send.chatgpt_submit_performed,
        status_message_posted=send.status_message_posted,
        target_window_count=target.target_window_count,
        matching_target_count=target.matching_target_count,
        selected_target_title=target.selected_target_title,
        composer_candidate_count=target.composer_candidate_count,
        provider=adapter.provider_name,
        issues=tuple(target.issues + placement.issues + send.issues),
    )


def render_no_send_text(result: ChromeStatusMessageNoSendProbeResult) -> str:
    lines = [
        f"result_label: {result.result_label}",
        f"ok: {str(result.ok).lower()}",
        f"patch_name: {result.patch_name}",
        f"selected_action: {result.selected_action}",
        f"browser_lane: {result.browser_lane}",
        f"pass_status_message: {result.pass_status_message}",
        f"pass_status_message_sha256: {result.pass_status_message_sha256}",
        f"live_browser: {str(result.live_browser).lower()}",
        f"stop_before_send: {str(result.stop_before_send).lower()}",
        f"confirmation_text_supplied: {result.confirmation_text_supplied}",
        f"confirmation_matched: {str(result.confirmation_matched).lower()}",
        f"chrome_target_ready: {str(result.chrome_target_ready).lower()}",
        f"chrome_target_focused: {str(result.chrome_target_focused).lower()}",
        f"composer_focus_attempted: {str(result.composer_focus_attempted).lower()}",
        f"composer_text_placed: {str(result.composer_text_placed).lower()}",
        f"composer_text_verified: {str(result.composer_text_verified).lower()}",
        f"send_risk_detected: {str(result.send_risk_detected).lower()}",
        f"browser_action_performed: {str(result.browser_action_performed).lower()}",
        f"chatgpt_submit_performed: {str(result.chatgpt_submit_performed).lower()}",
        f"operator_report_uploaded: {str(result.operator_report_uploaded).lower()}",
        f"status_message_posted: {str(result.status_message_posted).lower()}",
        f"send_button_pressed: {str(result.send_button_pressed).lower()}",
        f"raw_conversation_text_available: {str(result.raw_conversation_text_available).lower()}",
        f"selenium_used: {str(result.selenium_used).lower()}",
        f"webdriver_used: {str(result.webdriver_used).lower()}",
        f"browser_dom_automation_used: {str(result.browser_dom_automation_used).lower()}",
        f"cloudflare_bypass_attempted: {str(result.cloudflare_bypass_attempted).lower()}",
        f"captcha_bypass_attempted: {str(result.captcha_bypass_attempted).lower()}",
        f"target_window_count: {result.target_window_count}",
        f"matching_target_count: {result.matching_target_count}",
        f"selected_target_title_hash: {result.selected_target_title_hash}",
        f"selected_target_title_length: {result.selected_target_title_length}",
        f"composer_candidate_count: {result.composer_candidate_count}",
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


def render_send_text(result: ChromeStatusMessageSendResult) -> str:
    lines = [
        f"result_label: {result.result_label}",
        f"ok: {str(result.ok).lower()}",
        f"patch_name: {result.patch_name}",
        f"selected_action: {result.selected_action}",
        f"browser_lane: {result.browser_lane}",
        f"pass_status_message: {result.pass_status_message}",
        f"pass_status_message_sha256: {result.pass_status_message_sha256}",
        f"live_browser: {str(result.live_browser).lower()}",
        f"send_confirmation_text_supplied: {result.send_confirmation_text_supplied}",
        f"send_confirmation_matched: {str(result.send_confirmation_matched).lower()}",
        f"no_send_probe_required: {str(result.no_send_probe_required).lower()}",
        f"no_send_probe_ok: {str(result.no_send_probe_ok).lower()}",
        f"chrome_target_ready: {str(result.chrome_target_ready).lower()}",
        f"chrome_target_focused: {str(result.chrome_target_focused).lower()}",
        f"composer_text_verified_before_send: {str(result.composer_text_verified_before_send).lower()}",
        f"send_attempted: {str(result.send_attempted).lower()}",
        f"send_verified: {str(result.send_verified).lower()}",
        f"browser_action_performed: {str(result.browser_action_performed).lower()}",
        f"chatgpt_submit_performed: {str(result.chatgpt_submit_performed).lower()}",
        f"operator_report_uploaded: {str(result.operator_report_uploaded).lower()}",
        f"status_message_posted: {str(result.status_message_posted).lower()}",
        f"send_button_pressed: {str(result.send_button_pressed).lower()}",
        f"raw_conversation_text_available: {str(result.raw_conversation_text_available).lower()}",
        f"selenium_used: {str(result.selenium_used).lower()}",
        f"webdriver_used: {str(result.webdriver_used).lower()}",
        f"browser_dom_automation_used: {str(result.browser_dom_automation_used).lower()}",
        f"cloudflare_bypass_attempted: {str(result.cloudflare_bypass_attempted).lower()}",
        f"captcha_bypass_attempted: {str(result.captcha_bypass_attempted).lower()}",
        f"target_window_count: {result.target_window_count}",
        f"matching_target_count: {result.matching_target_count}",
        f"selected_target_title_hash: {result.selected_target_title_hash}",
        f"selected_target_title_length: {result.selected_target_title_length}",
        f"composer_candidate_count: {result.composer_candidate_count}",
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


def write_probe_evidence(
    result: ChromeStatusMessageNoSendProbeResult,
    *,
    json_output_path: Path = DEFAULT_NO_SEND_JSON_OUTPUT_PATH,
    txt_output_path: Path = DEFAULT_NO_SEND_TXT_OUTPUT_PATH,
) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_no_send_text(result), encoding="utf-8")
    return json_output_path, txt_output_path


def write_send_evidence(
    result: ChromeStatusMessageSendResult,
    *,
    json_output_path: Path = DEFAULT_SEND_JSON_OUTPUT_PATH,
    txt_output_path: Path = DEFAULT_SEND_TXT_OUTPUT_PATH,
) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_send_text(result), encoding="utf-8")
    return json_output_path, txt_output_path


def build_no_send_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chrome status message no-send probe")
    parser.add_argument("--armed-gate-path", default=str(DEFAULT_ARMED_GATE_PATH))
    parser.add_argument("--patch-name", default=None)
    parser.add_argument("--pass-status-message", default=None)
    parser.add_argument("--selected-action", default=None)
    parser.add_argument("--browser-lane", default=None)
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-ambiguous-target", "fake-mismatch", "fake-send-risk", "fake-send-fails", "pywinauto"), default="fake-ready")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--stop-before-send", action="store_true")
    parser.add_argument("--json-output-path", default=str(DEFAULT_NO_SEND_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_NO_SEND_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def build_send_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chrome status message send test")
    parser.add_argument("--armed-gate-path", default=str(DEFAULT_ARMED_GATE_PATH))
    parser.add_argument("--patch-name", default=None)
    parser.add_argument("--pass-status-message", default=None)
    parser.add_argument("--selected-action", default=None)
    parser.add_argument("--browser-lane", default=None)
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-ambiguous-target", "fake-mismatch", "fake-send-risk", "fake-send-fails", "pywinauto"), default="fake-ready")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-no-send-text", default=None)
    parser.add_argument("--confirm-send-text", default=None)
    parser.add_argument("--json-output-path", default=str(DEFAULT_SEND_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_SEND_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def _resolve_cli_values(args: argparse.Namespace) -> tuple[str, str, str, str]:
    gate_patch_name, gate_selected_action, gate_browser_lane, gate_message = read_expected_message_from_gate(Path(args.armed_gate_path))
    patch_name = normalize_optional_text(args.patch_name) or gate_patch_name
    selected_action = normalize_optional_text(args.selected_action) or gate_selected_action
    browser_lane = (normalize_optional_text(args.browser_lane) or gate_browser_lane).lower()
    pass_status_message = normalize_optional_text(args.pass_status_message) or gate_message
    return patch_name, selected_action, browser_lane, pass_status_message


def no_send_main(argv: Sequence[str] | None = None) -> int:
    args = build_no_send_parser().parse_args(argv)
    patch_name, selected_action, browser_lane, pass_status_message = _resolve_cli_values(args)
    result = run_chrome_status_message_no_send_probe(
        patch_name=patch_name,
        selected_action=selected_action,
        browser_lane=browser_lane,
        pass_status_message=pass_status_message,
        live_browser=bool(args.live_browser),
        confirmation_text=args.confirm_live_browser_text,
        stop_before_send=bool(args.stop_before_send),
        provider=args.provider,
    )
    if not args.no_write_evidence:
        write_probe_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))
    if args.json:
        print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_no_send_text(result), end="")
    return 0 if result.ok else 2


def send_main(argv: Sequence[str] | None = None) -> int:
    args = build_send_parser().parse_args(argv)
    patch_name, selected_action, browser_lane, pass_status_message = _resolve_cli_values(args)
    result = run_chrome_status_message_send_test(
        patch_name=patch_name,
        selected_action=selected_action,
        browser_lane=browser_lane,
        pass_status_message=pass_status_message,
        live_browser=bool(args.live_browser),
        no_send_confirmation_text=args.confirm_no_send_text,
        send_confirmation_text=args.confirm_send_text,
        provider=args.provider,
    )
    if not args.no_write_evidence:
        write_send_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))
    if args.json:
        print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_send_text(result), end="")
    return 0 if result.ok else 2


def main(argv: Sequence[str] | None = None) -> int:
    return send_main(argv)


if __name__ == "__main__":
    raise SystemExit(send_main())