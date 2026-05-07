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

PATCH_NAME = "u3_c34_edge_status_message_send_test"

ACTION_POST_STATUS_MESSAGE = "post_status_message"
CONFIRM_EDGE_STATUS_MESSAGE_SEND = "PATCHOPS_CONFIRM_EDGE_STATUS_MESSAGE_SEND"

PASS_EDGE_STATUS_MESSAGE_SENT = "PASS_EDGE_STATUS_MESSAGE_SENT"
BLOCKED_EDGE_EXACT_MESSAGE_CONFIRMATION_MISSING = "BLOCKED_EDGE_EXACT_MESSAGE_CONFIRMATION_MISSING"
BLOCKED_EDGE_EXACT_MESSAGE_CONFIRMATION_MISMATCH = "BLOCKED_EDGE_EXACT_MESSAGE_CONFIRMATION_MISMATCH"
BLOCKED_EDGE_STATUS_SEND_CONFIRMATION_REQUIRED = "BLOCKED_EDGE_STATUS_SEND_CONFIRMATION_REQUIRED"
BLOCKED_EDGE_STATUS_SEND_CONFIRMATION_MISMATCH = "BLOCKED_EDGE_STATUS_SEND_CONFIRMATION_MISMATCH"
BLOCKED_EDGE_STATUS_TARGET_NOT_READY = "BLOCKED_EDGE_STATUS_TARGET_NOT_READY"
BLOCKED_EDGE_STATUS_MESSAGE_MISMATCH = "BLOCKED_EDGE_STATUS_MESSAGE_MISMATCH"
BLOCKED_EDGE_SEND_RISK = "BLOCKED_EDGE_SEND_RISK"
FAIL_EDGE_STATUS_MESSAGE_SEND_NOT_PROVEN = "FAIL_EDGE_STATUS_MESSAGE_SEND_NOT_PROVEN"

DEFAULT_ARMED_GATE_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_reporter_armed_gate.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_edge_status_message_send_test.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_edge_status_message_send_test.txt")

CHATGPT_TITLE_TOKENS = ("chatgpt", "openai")
EDGE_TITLE_TOKENS = ("microsoft edge", "edge")
COMPOSER_NAME_TOKENS = ("message chatgpt", "message", "ask anything", "send a message", "prompt")
SEND_BUTTON_NAME_TOKENS = ("send", "submit")


@dataclass(frozen=True)
class EdgeStatusReporterSafety:
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
class EdgeStatusMessageSendResult:
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
    exact_message_confirmation_supplied: str | None
    exact_message_confirmation_matched: bool
    edge_target_ready: bool
    edge_target_focused: bool
    composer_focus_attempted: bool
    composer_text_placed: bool
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
    safety: EdgeStatusReporterSafety = field(default_factory=EdgeStatusReporterSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        return payload


@dataclass(frozen=True)
class EdgeTargetProbe:
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


class EdgeStatusMessageAdapter(Protocol):
    provider_name: str

    def focus_target(self) -> EdgeTargetProbe:
        ...

    def place_message_no_send(self, message: str) -> ComposerPlacement:
        ...

    def send_prepared_message(self, message: str) -> SendAttempt:
        ...


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def expected_pass_status_message(patch_name: str) -> str:
    return f"{patch_name} has passed"


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def message_from_armed_gate_payload(payload: dict[str, Any], *, fallback_patch_name: str = PATCH_NAME) -> tuple[str, str, str, str]:
    patch_name = normalize_optional_text(payload.get("patch_name")) or fallback_patch_name
    selected_action = normalize_optional_text(payload.get("selected_action")) or ACTION_POST_STATUS_MESSAGE
    browser_lane = (normalize_optional_text(payload.get("browser_lane")) or "edge").lower()
    pass_status_message = normalize_optional_text(payload.get("pass_status_message")) or expected_pass_status_message(patch_name)
    return patch_name, selected_action, browser_lane, pass_status_message


def read_expected_message_from_gate(path: Path, *, fallback_patch_name: str = PATCH_NAME) -> tuple[str, str, str, str]:
    if not path.exists():
        return fallback_patch_name, ACTION_POST_STATUS_MESSAGE, "edge", expected_pass_status_message(fallback_patch_name)
    return message_from_armed_gate_payload(load_json_object(path), fallback_patch_name=fallback_patch_name)


class FakeEdgeStatusMessageAdapter:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.provider_name = f"fake-{mode}"
        self.placed_text: str | None = None
        self.sent_text: str | None = None

    def focus_target(self) -> EdgeTargetProbe:
        if self.mode == "no-target":
            return EdgeTargetProbe(False, False, 0, 0, None, 0, ("no fake Edge ChatGPT target",))
        if self.mode == "ambiguous-target":
            return EdgeTargetProbe(False, False, 2, 2, None, 0, ("multiple fake Edge ChatGPT targets",))
        if self.mode == "no-composer":
            return EdgeTargetProbe(False, True, 1, 1, "ChatGPT - Microsoft Edge", 0, ("no fake composer candidate",))
        return EdgeTargetProbe(True, True, 1, 1, "ChatGPT - Microsoft Edge", 1, ())

    def place_message_no_send(self, message: str) -> ComposerPlacement:
        if self.mode == "send-risk":
            return ComposerPlacement(True, False, False, None, True, ("fake Edge send risk detected",))
        if self.mode == "mismatch":
            self.placed_text = f"{message} extra"
            return ComposerPlacement(True, True, False, self.placed_text, False, ("fake Edge composer text mismatch",))
        self.placed_text = message
        return ComposerPlacement(True, True, True, self.placed_text, False, ())

    def send_prepared_message(self, message: str) -> SendAttempt:
        if self.mode == "send-fails":
            return SendAttempt(True, False, True, False, False, False, ("fake Edge send verification failed",))
        if self.placed_text != message:
            return SendAttempt(False, False, False, False, False, True, ("prepared Edge text mismatch before send",))
        self.sent_text = message
        return SendAttempt(True, True, True, True, True, False, ())


class PywinautoEdgeStatusMessageAdapter:
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
            raise RuntimeError(f"pywinauto is required for live Edge send test: {exc}") from exc
        return Desktop(backend="uia")

    def _looks_like_edge_chatgpt_window(self, window: Any) -> bool:
        title = _safe_window_title(window) or ""
        lowered = title.lower()
        return any(token in lowered for token in EDGE_TITLE_TOKENS) and any(token in lowered for token in CHATGPT_TITLE_TOKENS)

    def focus_target(self) -> EdgeTargetProbe:
        try:
            desktop = self._desktop()
            windows = list(desktop.windows())
        except Exception as exc:
            return EdgeTargetProbe(False, False, 0, 0, None, 0, (str(exc),))
        matches = [window for window in windows if self._looks_like_edge_chatgpt_window(window)]
        if not matches:
            return EdgeTargetProbe(False, False, len(windows), 0, None, 0, ("no visible Edge ChatGPT target window",))
        if len(matches) > 1:
            return EdgeTargetProbe(False, False, len(windows), len(matches), None, 0, ("multiple Edge ChatGPT target windows",))
        selected = matches[0]
        try:
            selected.set_focus()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return EdgeTargetProbe(False, False, len(windows), 1, _safe_window_title(selected), 0, (f"Edge focus failed: {exc}",))
        self._selected_window = selected
        candidates = self._find_composer_candidates(selected)
        if not candidates:
            return EdgeTargetProbe(False, True, len(windows), 1, _safe_window_title(selected), 0, ("no safe Edge ChatGPT composer candidate",))
        return EdgeTargetProbe(True, True, len(windows), 1, _safe_window_title(selected), len(candidates), ())

    def _find_composer_candidates(self, window: Any) -> list[Any]:
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
            if enabled and visible and control_type in {"edit", "document"} and any(token in name for token in COMPOSER_NAME_TOKENS):
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
                name = str(element.window_text() or element.element_info.name or "").strip().lower()
                enabled = bool(element.is_enabled())
                visible = bool(element.is_visible())
            except Exception:
                continue
            if enabled and visible and control_type == "button" and any(token == name or token in name for token in SEND_BUTTON_NAME_TOKENS):
                candidates.append(element)
        return candidates

    def place_message_no_send(self, message: str) -> ComposerPlacement:
        if self._selected_window is None:
            return ComposerPlacement(False, False, False, None, False, ("Edge target was not focused first",))
        candidates = self._find_composer_candidates(self._selected_window)
        if not candidates:
            return ComposerPlacement(False, False, False, None, False, ("no safe Edge ChatGPT composer candidate",))
        if len(candidates) > 1:
            return ComposerPlacement(False, False, False, None, True, ("multiple Edge composer candidates; refusing to type",))
        composer = candidates[0]
        self._selected_composer = composer
        try:
            composer.set_focus()
            composer.click_input()
            time.sleep(self.settle_seconds)
            focus_attempted = True
        except Exception as exc:
            return ComposerPlacement(True, False, False, None, False, (f"Edge composer focus failed: {exc}",))
        try:
            _set_windows_clipboard_text(message)
            try:
                from pywinauto.keyboard import send_keys  # type: ignore
            except Exception as exc:  # pragma: no cover
                raise RuntimeError(f"pywinauto keyboard helper unavailable: {exc}") from exc
            send_keys("^v", pause=0.05)
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return ComposerPlacement(focus_attempted, False, False, None, False, (f"Edge message paste failed: {exc}",))
        readback = _try_read_element_text(composer)
        verified = readback == message
        if verified:
            self._last_prepared_message = message
            return ComposerPlacement(focus_attempted, True, True, readback, False, ())
        return ComposerPlacement(focus_attempted, True, False, readback, False, ("Edge composer text readback did not exactly match expected message",))

    def send_prepared_message(self, message: str) -> SendAttempt:
        if self._selected_window is None or self._selected_composer is None:
            return SendAttempt(False, False, False, False, False, True, ("Edge target/composer not prepared before send",))
        if self._last_prepared_message != message:
            return SendAttempt(False, False, False, False, False, True, ("prepared Edge message mismatch before send",))
        try:
            self._selected_composer.set_focus()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return SendAttempt(False, False, False, False, False, True, (f"failed to refocus Edge composer before send: {exc}",))
        buttons = self._find_send_button_candidates(self._selected_window)
        if len(buttons) > 1:
            return SendAttempt(False, False, False, False, False, True, ("multiple enabled Edge send-like buttons; refusing to send",))
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
            return SendAttempt(True, False, send_button_pressed if "send_button_pressed" in locals() else False, False, False, False, (f"Edge send action failed: {exc}",))
        after_text = _try_read_element_text(self._selected_composer)
        verified = after_text is None or after_text == "" or after_text != message
        if not verified:
            return SendAttempt(True, False, send_button_pressed, False, False, False, ("Edge composer still contains exact message after send",))
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


def build_adapter(provider: str) -> EdgeStatusMessageAdapter:
    if provider.startswith("fake-"):
        return FakeEdgeStatusMessageAdapter(provider.removeprefix("fake-"))
    if provider == "pywinauto":
        return PywinautoEdgeStatusMessageAdapter()
    raise ValueError(f"Unknown provider: {provider}")


def make_result(
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
    exact_message_confirmation_supplied: str | None,
    exact_message_confirmation_matched: bool,
    edge_target_ready: bool,
    edge_target_focused: bool,
    composer_focus_attempted: bool,
    composer_text_placed: bool,
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
) -> EdgeStatusMessageSendResult:
    safety = EdgeStatusReporterSafety(
        browser_action_performed=bool(edge_target_focused or composer_focus_attempted or composer_text_placed or send_attempted),
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
    return EdgeStatusMessageSendResult(
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
        exact_message_confirmation_supplied=exact_message_confirmation_supplied,
        exact_message_confirmation_matched=exact_message_confirmation_matched,
        edge_target_ready=edge_target_ready,
        edge_target_focused=edge_target_focused,
        composer_focus_attempted=composer_focus_attempted,
        composer_text_placed=composer_text_placed,
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


def run_edge_status_message_send_test(
    *,
    patch_name: str,
    selected_action: str,
    browser_lane: str,
    pass_status_message: str,
    live_browser: bool,
    send_confirmation_text: str | None,
    exact_message_confirmation: str | None,
    provider: str,
) -> EdgeStatusMessageSendResult:
    expected_message = expected_pass_status_message(patch_name)

    if not live_browser:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_SEND_RISK,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=False,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=send_confirmation_text == CONFIRM_EDGE_STATUS_MESSAGE_SEND,
            exact_message_confirmation_supplied=exact_message_confirmation,
            exact_message_confirmation_matched=exact_message_confirmation == expected_message,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_focus_attempted=False,
            composer_text_placed=False,
            composer_text_verified_before_send=False,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            provider=provider,
            issues=("--live-browser is required for C34",),
        )

    if send_confirmation_text is None:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_SEND_CONFIRMATION_REQUIRED,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=True,
            send_confirmation_text_supplied=None,
            send_confirmation_matched=False,
            exact_message_confirmation_supplied=exact_message_confirmation,
            exact_message_confirmation_matched=exact_message_confirmation == expected_message,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_focus_attempted=False,
            composer_text_placed=False,
            composer_text_verified_before_send=False,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            provider=provider,
            issues=("send confirmation is required",),
        )

    send_confirmation_matched = send_confirmation_text == CONFIRM_EDGE_STATUS_MESSAGE_SEND
    if not send_confirmation_matched:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_SEND_CONFIRMATION_MISMATCH,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=True,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=False,
            exact_message_confirmation_supplied=exact_message_confirmation,
            exact_message_confirmation_matched=exact_message_confirmation == expected_message,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_focus_attempted=False,
            composer_text_placed=False,
            composer_text_verified_before_send=False,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            provider=provider,
            issues=(f"send confirmation must exactly match {CONFIRM_EDGE_STATUS_MESSAGE_SEND}",),
        )

    if exact_message_confirmation is None:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_EXACT_MESSAGE_CONFIRMATION_MISSING,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=True,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=True,
            exact_message_confirmation_supplied=None,
            exact_message_confirmation_matched=False,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_focus_attempted=False,
            composer_text_placed=False,
            composer_text_verified_before_send=False,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            provider=provider,
            issues=("exact message confirmation is required",),
        )

    exact_message_confirmation_matched = exact_message_confirmation == expected_message
    if not exact_message_confirmation_matched:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_EXACT_MESSAGE_CONFIRMATION_MISMATCH,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=True,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=True,
            exact_message_confirmation_supplied=exact_message_confirmation,
            exact_message_confirmation_matched=False,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_focus_attempted=False,
            composer_text_placed=False,
            composer_text_verified_before_send=False,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            provider=provider,
            issues=("exact message confirmation must match '<patch_name> has passed'",),
        )

    message_issues: list[str] = []
    if selected_action != ACTION_POST_STATUS_MESSAGE:
        message_issues.append(f"selected_action must be {ACTION_POST_STATUS_MESSAGE}")
    if browser_lane != "edge":
        message_issues.append("browser_lane must be edge")
    if pass_status_message != expected_message:
        message_issues.append("pass_status_message must exactly equal '<patch_name> has passed'")
    if message_issues:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_MESSAGE_MISMATCH,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=True,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=True,
            exact_message_confirmation_supplied=exact_message_confirmation,
            exact_message_confirmation_matched=True,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_focus_attempted=False,
            composer_text_placed=False,
            composer_text_verified_before_send=False,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            provider=provider,
            issues=message_issues,
        )

    try:
        adapter = build_adapter(provider)
    except Exception as exc:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_TARGET_NOT_READY,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=True,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=True,
            exact_message_confirmation_supplied=exact_message_confirmation,
            exact_message_confirmation_matched=True,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_focus_attempted=False,
            composer_text_placed=False,
            composer_text_verified_before_send=False,
            send_attempted=False,
            send_verified=False,
            send_button_pressed=False,
            chatgpt_submit_performed=False,
            status_message_posted=False,
            provider=provider,
            issues=(str(exc),),
        )

    target = adapter.focus_target()
    if not target.ready or not target.focused:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_TARGET_NOT_READY,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=True,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=True,
            exact_message_confirmation_supplied=exact_message_confirmation,
            exact_message_confirmation_matched=True,
            edge_target_ready=target.ready,
            edge_target_focused=target.focused,
            composer_focus_attempted=False,
            composer_text_placed=False,
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
    if placement.send_risk_detected:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_SEND_RISK,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=True,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=True,
            exact_message_confirmation_supplied=exact_message_confirmation,
            exact_message_confirmation_matched=True,
            edge_target_ready=target.ready,
            edge_target_focused=target.focused,
            composer_focus_attempted=placement.focus_attempted,
            composer_text_placed=placement.text_placed,
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
    if not placement.text_placed or not placement.text_verified:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_MESSAGE_MISMATCH,
            patch_name=patch_name,
            selected_action=selected_action,
            browser_lane=browser_lane,
            pass_status_message=pass_status_message,
            live_browser=True,
            send_confirmation_text_supplied=send_confirmation_text,
            send_confirmation_matched=True,
            exact_message_confirmation_supplied=exact_message_confirmation,
            exact_message_confirmation_matched=True,
            edge_target_ready=target.ready,
            edge_target_focused=target.focused,
            composer_focus_attempted=placement.focus_attempted,
            composer_text_placed=placement.text_placed,
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
        label = BLOCKED_EDGE_SEND_RISK
    elif not send.attempted or not send.verified:
        label = FAIL_EDGE_STATUS_MESSAGE_SEND_NOT_PROVEN
    else:
        label = PASS_EDGE_STATUS_MESSAGE_SENT

    return make_result(
        ok=send.verified and send.chatgpt_submit_performed and send.status_message_posted,
        result_label=label,
        patch_name=patch_name,
        selected_action=selected_action,
        browser_lane=browser_lane,
        pass_status_message=pass_status_message,
        live_browser=True,
        send_confirmation_text_supplied=send_confirmation_text,
        send_confirmation_matched=True,
        exact_message_confirmation_supplied=exact_message_confirmation,
        exact_message_confirmation_matched=True,
        edge_target_ready=target.ready,
        edge_target_focused=target.focused,
        composer_focus_attempted=placement.focus_attempted,
        composer_text_placed=placement.text_placed,
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


def render_text(result: EdgeStatusMessageSendResult) -> str:
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
        f"exact_message_confirmation_supplied: {result.exact_message_confirmation_supplied}",
        f"exact_message_confirmation_matched: {str(result.exact_message_confirmation_matched).lower()}",
        f"edge_target_ready: {str(result.edge_target_ready).lower()}",
        f"edge_target_focused: {str(result.edge_target_focused).lower()}",
        f"composer_focus_attempted: {str(result.composer_focus_attempted).lower()}",
        f"composer_text_placed: {str(result.composer_text_placed).lower()}",
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


def write_send_evidence(
    result: EdgeStatusMessageSendResult,
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
    parser = argparse.ArgumentParser(description="Edge status message send test")
    parser.add_argument("--armed-gate-path", default=str(DEFAULT_ARMED_GATE_PATH))
    parser.add_argument("--patch-name", default=None)
    parser.add_argument("--pass-status-message", default=None)
    parser.add_argument("--selected-action", default=None)
    parser.add_argument("--browser-lane", default=None)
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-ambiguous-target", "fake-no-composer", "fake-mismatch", "fake-send-risk", "fake-send-fails", "pywinauto"), default="fake-ready")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--confirm-exact-message", default=None)
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
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


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    patch_name, selected_action, browser_lane, pass_status_message = _resolve_cli_values(args)
    result = run_edge_status_message_send_test(
        patch_name=patch_name,
        selected_action=selected_action,
        browser_lane=browser_lane,
        pass_status_message=pass_status_message,
        live_browser=bool(args.live_browser),
        send_confirmation_text=args.confirm_live_browser_text,
        exact_message_confirmation=args.confirm_exact_message,
        provider=args.provider,
    )
    if not args.no_write_evidence:
        write_send_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))
    if args.json:
        print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(result), end="")
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())