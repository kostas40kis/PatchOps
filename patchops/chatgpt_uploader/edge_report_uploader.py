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

PATCH_NAME = "u3_c35_edge_fail_report_upload_no_send_probe"

ACTION_UPLOAD_OPERATOR_REPORT = "upload_operator_report"
CONFIRM_EDGE_FAIL_REPORT_UPLOAD_NO_SEND = "PATCHOPS_CONFIRM_EDGE_FAIL_REPORT_UPLOAD_NO_SEND"

PASS_EDGE_FAIL_REPORT_ATTACHED_NO_SEND = "PASS_EDGE_FAIL_REPORT_ATTACHED_NO_SEND"
BLOCKED_OPERATOR_REPORT_MISSING = "BLOCKED_OPERATOR_REPORT_MISSING"
BLOCKED_OPERATOR_REPORT_HASH_MISMATCH = "BLOCKED_OPERATOR_REPORT_HASH_MISMATCH"
BLOCKED_EDGE_TARGET_NOT_READY = "BLOCKED_EDGE_TARGET_NOT_READY"
BLOCKED_ATTACHMENT_NOT_VERIFIED = "BLOCKED_ATTACHMENT_NOT_VERIFIED"
BLOCKED_EDGE_UPLOAD_CONFIRMATION_REQUIRED = "BLOCKED_EDGE_UPLOAD_CONFIRMATION_REQUIRED"
BLOCKED_EDGE_UPLOAD_CONFIRMATION_MISMATCH = "BLOCKED_EDGE_UPLOAD_CONFIRMATION_MISMATCH"
BLOCKED_EDGE_UPLOAD_ROUTE_MISMATCH = "BLOCKED_EDGE_UPLOAD_ROUTE_MISMATCH"
BLOCKED_SEND_RISK = "BLOCKED_SEND_RISK"

DEFAULT_ARMED_GATE_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_reporter_armed_gate.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_edge_fail_report_upload_no_send_probe.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_edge_fail_report_upload_no_send_probe.txt")

CHATGPT_TITLE_TOKENS = ("chatgpt", "openai")
EDGE_TITLE_TOKENS = ("microsoft edge", "edge")
ATTACH_BUTTON_NAME_TOKENS = ("attach", "upload", "add files", "add photos", "paperclip")
FILE_DIALOG_TITLE_TOKENS = ("open", "upload", "choose file", "file upload")
ATTACHMENT_READY_TOKENS = ("uploaded", "attached", "file")


@dataclass(frozen=True)
class EdgeReportUploaderSafety:
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
class EdgeFailReportUploadNoSendResult:
    ok: bool
    result_label: str
    patch_name: str | None
    patch_result: str | None
    selected_action: str | None
    browser_lane: str | None
    live_browser: bool
    stop_before_send: bool
    confirmation_text_supplied: str | None
    confirmation_matched: bool
    operator_report_path: str | None
    operator_report_sha256: str | None
    expected_operator_report_sha256: str | None
    operator_report_size_bytes: int | None
    edge_target_ready: bool
    edge_target_focused: bool
    upload_trigger_attempted: bool
    file_picker_used: bool
    file_path_written: bool
    attachment_ready: bool
    attachment_verified: bool
    send_risk_detected: bool
    browser_action_performed: bool
    chatgpt_submit_performed: bool
    operator_report_uploaded: bool
    status_message_posted: bool
    send_button_pressed: bool
    file_upload_attempted: bool
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
    attachment_candidate_count: int = 0
    provider: str = "fake-ready"
    issues: tuple[str, ...] = ()
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    safety: EdgeReportUploaderSafety = field(default_factory=EdgeReportUploaderSafety)

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
    attachment_candidate_count: int
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class UploadAttempt:
    trigger_attempted: bool
    file_picker_used: bool
    file_path_written: bool
    attachment_ready: bool
    attachment_verified: bool
    send_risk_detected: bool
    issues: tuple[str, ...] = ()


class EdgeReportUploadAdapter(Protocol):
    provider_name: str

    def focus_target(self) -> EdgeTargetProbe:
        ...

    def attach_report_no_send(self, report_path: Path) -> UploadAttempt:
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


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def report_values_from_armed_gate_payload(payload: dict[str, Any]) -> tuple[str | None, str | None, str | None, str | None, str | None, str | None]:
    patch_name = normalize_optional_text(payload.get("patch_name"))
    patch_result = normalize_optional_text(payload.get("patch_result"))
    selected_action = normalize_optional_text(payload.get("selected_action"))
    browser_lane = normalize_optional_text(payload.get("browser_lane"))
    if browser_lane:
        browser_lane = browser_lane.lower()
    operator_report_path = normalize_optional_text(payload.get("operator_report_path"))
    operator_report_sha256 = normalize_optional_text(payload.get("operator_report_sha256"))
    return patch_name, patch_result, selected_action, browser_lane, operator_report_path, operator_report_sha256


def read_report_values_from_gate(path: Path) -> tuple[str | None, str | None, str | None, str | None, str | None, str | None]:
    if not path.exists():
        return None, None, ACTION_UPLOAD_OPERATOR_REPORT, "edge", None, None
    return report_values_from_armed_gate_payload(load_json_object(path))


class FakeEdgeReportUploadAdapter:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.provider_name = f"fake-{mode}"
        self.attached_path: str | None = None

    def focus_target(self) -> EdgeTargetProbe:
        if self.mode == "no-target":
            return EdgeTargetProbe(False, False, 0, 0, None, 0, ("no fake Edge target",))
        if self.mode == "ambiguous-target":
            return EdgeTargetProbe(False, False, 2, 2, None, 0, ("multiple fake Edge targets",))
        if self.mode == "no-attach-button":
            return EdgeTargetProbe(False, True, 1, 1, "ChatGPT - Microsoft Edge", 0, ("no fake Edge attachment button",))
        return EdgeTargetProbe(True, True, 1, 1, "ChatGPT - Microsoft Edge", 1, ())

    def attach_report_no_send(self, report_path: Path) -> UploadAttempt:
        if self.mode == "send-risk":
            return UploadAttempt(False, False, False, False, False, True, ("fake Edge send risk detected",))
        if self.mode == "picker-fails":
            return UploadAttempt(True, True, False, False, False, False, ("fake Edge picker path write failed",))
        if self.mode == "attachment-not-verified":
            self.attached_path = str(report_path)
            return UploadAttempt(True, True, True, True, False, False, ("fake Edge attachment not verified",))
        self.attached_path = str(report_path)
        return UploadAttempt(True, True, True, True, True, False, ())


class PywinautoEdgeReportUploadAdapter:
    provider_name = "pywinauto"

    def __init__(self, *, settle_seconds: float = 0.5) -> None:
        self.settle_seconds = settle_seconds
        self._selected_window: Any | None = None

    def _desktop(self) -> Any:
        try:
            from pywinauto import Desktop  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"pywinauto is required for live Edge report upload probing: {exc}") from exc
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
        candidates = self._find_attachment_buttons(selected)
        if not candidates:
            return EdgeTargetProbe(False, True, len(windows), 1, _safe_window_title(selected), 0, ("no safe Edge attachment button candidate",))
        return EdgeTargetProbe(True, True, len(windows), 1, _safe_window_title(selected), len(candidates), ())

    def _find_attachment_buttons(self, window: Any) -> list[Any]:
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
            if enabled and visible and control_type == "button" and any(token in name for token in ATTACH_BUTTON_NAME_TOKENS):
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

    def _find_file_name_edit(self, dialog: Any) -> Any | None:
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
            if expected_lower in text:
                return True
            if expected_lower and any(token in text for token in ATTACHMENT_READY_TOKENS) and expected_lower.split(".")[0] in text:
                return True
        return False

    def attach_report_no_send(self, report_path: Path) -> UploadAttempt:
        if self._selected_window is None:
            return UploadAttempt(False, False, False, False, False, False, ("Edge target was not focused first",))

        buttons = self._find_attachment_buttons(self._selected_window)
        if not buttons:
            return UploadAttempt(False, False, False, False, False, False, ("no safe Edge attachment button candidate",))
        if len(buttons) > 1:
            return UploadAttempt(False, False, False, False, False, True, ("multiple Edge attachment buttons; refusing to choose",))

        try:
            buttons[0].click_input()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return UploadAttempt(True, False, False, False, False, False, (f"Edge attachment button click failed: {exc}",))

        dialog = self._find_file_dialog()
        if dialog is None:
            return UploadAttempt(True, False, False, False, False, False, ("Edge file picker did not appear",))

        edit = self._find_file_name_edit(dialog)
        if edit is None:
            return UploadAttempt(True, True, False, False, False, False, ("Edge file picker filename edit not found",))

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
                send_keys("{ENTER}", pause=0.05)
            time.sleep(self.settle_seconds * 2)
        except Exception as exc:
            return UploadAttempt(True, True, False, False, False, False, (f"Edge file picker path write failed: {exc}",))

        ready = self._attachment_ready(report_path.name)
        if not ready:
            return UploadAttempt(True, True, True, False, False, False, ("Edge attachment readiness was not verified",))
        return UploadAttempt(True, True, True, True, True, False, ())


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
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p

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


def build_adapter(provider: str) -> EdgeReportUploadAdapter:
    if provider.startswith("fake-"):
        return FakeEdgeReportUploadAdapter(provider.removeprefix("fake-"))
    if provider == "pywinauto":
        return PywinautoEdgeReportUploadAdapter()
    raise ValueError(f"Unknown provider: {provider}")


def make_result(
    *,
    ok: bool,
    result_label: str,
    patch_name: str | None,
    patch_result: str | None,
    selected_action: str | None,
    browser_lane: str | None,
    live_browser: bool,
    stop_before_send: bool,
    confirmation_text_supplied: str | None,
    confirmation_matched: bool,
    operator_report_path: str | None,
    operator_report_sha256: str | None,
    expected_operator_report_sha256: str | None,
    operator_report_size_bytes: int | None,
    edge_target_ready: bool,
    edge_target_focused: bool,
    upload_trigger_attempted: bool,
    file_picker_used: bool,
    file_path_written: bool,
    attachment_ready: bool,
    attachment_verified: bool,
    send_risk_detected: bool,
    provider: str,
    target_window_count: int = 0,
    matching_target_count: int = 0,
    selected_target_title: str | None = None,
    attachment_candidate_count: int = 0,
    issues: Sequence[str] = (),
) -> EdgeFailReportUploadNoSendResult:
    safety = EdgeReportUploaderSafety(
        browser_action_performed=bool(edge_target_focused or upload_trigger_attempted or file_picker_used or file_path_written),
        chatgpt_submit_performed=False,
        operator_report_uploaded=False,
        status_message_posted=False,
        send_button_pressed=False,
        file_upload_attempted=bool(upload_trigger_attempted or file_picker_used or file_path_written),
        raw_conversation_text_available=False,
        selenium_used=False,
        webdriver_used=False,
        browser_dom_automation_used=False,
        cloudflare_bypass_attempted=False,
        captcha_bypass_attempted=False,
        conversation_text_logged=False,
        random_page_click_performed=False,
    )
    return EdgeFailReportUploadNoSendResult(
        ok=ok,
        result_label=result_label,
        patch_name=patch_name,
        patch_result=patch_result,
        selected_action=selected_action,
        browser_lane=browser_lane,
        live_browser=live_browser,
        stop_before_send=stop_before_send,
        confirmation_text_supplied=confirmation_text_supplied,
        confirmation_matched=confirmation_matched,
        operator_report_path=operator_report_path,
        operator_report_sha256=operator_report_sha256,
        expected_operator_report_sha256=expected_operator_report_sha256,
        operator_report_size_bytes=operator_report_size_bytes,
        edge_target_ready=edge_target_ready,
        edge_target_focused=edge_target_focused,
        upload_trigger_attempted=upload_trigger_attempted,
        file_picker_used=file_picker_used,
        file_path_written=file_path_written,
        attachment_ready=attachment_ready,
        attachment_verified=attachment_verified,
        send_risk_detected=send_risk_detected,
        browser_action_performed=safety.browser_action_performed,
        chatgpt_submit_performed=safety.chatgpt_submit_performed,
        operator_report_uploaded=safety.operator_report_uploaded,
        status_message_posted=safety.status_message_posted,
        send_button_pressed=safety.send_button_pressed,
        file_upload_attempted=safety.file_upload_attempted,
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
        attachment_candidate_count=attachment_candidate_count,
        provider=provider,
        issues=tuple(issues),
        safety=safety,
    )


def run_edge_fail_report_upload_no_send_probe(
    *,
    patch_name: str | None,
    patch_result: str | None,
    selected_action: str | None,
    browser_lane: str | None,
    operator_report_path: str | None,
    expected_operator_report_sha256: str | None,
    live_browser: bool,
    confirmation_text: str | None,
    stop_before_send: bool,
    provider: str,
) -> EdgeFailReportUploadNoSendResult:
    confirmation_matched = confirmation_text == CONFIRM_EDGE_FAIL_REPORT_UPLOAD_NO_SEND

    if confirmation_text is None:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_UPLOAD_CONFIRMATION_REQUIRED,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=None,
            confirmation_matched=False,
            operator_report_path=operator_report_path,
            operator_report_sha256=None,
            expected_operator_report_sha256=expected_operator_report_sha256,
            operator_report_size_bytes=None,
            edge_target_ready=False,
            edge_target_focused=False,
            upload_trigger_attempted=False,
            file_picker_used=False,
            file_path_written=False,
            attachment_ready=False,
            attachment_verified=False,
            send_risk_detected=True,
            provider=provider,
            issues=("upload confirmation is required",),
        )

    if not confirmation_matched:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_UPLOAD_CONFIRMATION_MISMATCH,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=False,
            operator_report_path=operator_report_path,
            operator_report_sha256=None,
            expected_operator_report_sha256=expected_operator_report_sha256,
            operator_report_size_bytes=None,
            edge_target_ready=False,
            edge_target_focused=False,
            upload_trigger_attempted=False,
            file_picker_used=False,
            file_path_written=False,
            attachment_ready=False,
            attachment_verified=False,
            send_risk_detected=True,
            provider=provider,
            issues=(f"upload confirmation must exactly match {CONFIRM_EDGE_FAIL_REPORT_UPLOAD_NO_SEND}",),
        )

    hard_gate_issues: list[str] = []
    if not live_browser:
        hard_gate_issues.append("--live-browser is required for C35")
    if not stop_before_send:
        hard_gate_issues.append("--stop-before-send is required for C35")
    if hard_gate_issues:
        return make_result(
            ok=False,
            result_label=BLOCKED_SEND_RISK,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=True,
            operator_report_path=operator_report_path,
            operator_report_sha256=None,
            expected_operator_report_sha256=expected_operator_report_sha256,
            operator_report_size_bytes=None,
            edge_target_ready=False,
            edge_target_focused=False,
            upload_trigger_attempted=False,
            file_picker_used=False,
            file_path_written=False,
            attachment_ready=False,
            attachment_verified=False,
            send_risk_detected=True,
            provider=provider,
            issues=hard_gate_issues,
        )

    route_issues: list[str] = []
    if selected_action != ACTION_UPLOAD_OPERATOR_REPORT:
        route_issues.append(f"selected_action must be {ACTION_UPLOAD_OPERATOR_REPORT}")
    if browser_lane != "edge":
        route_issues.append("browser_lane must be edge")
    if route_issues:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_UPLOAD_ROUTE_MISMATCH,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=True,
            operator_report_path=operator_report_path,
            operator_report_sha256=None,
            expected_operator_report_sha256=expected_operator_report_sha256,
            operator_report_size_bytes=None,
            edge_target_ready=False,
            edge_target_focused=False,
            upload_trigger_attempted=False,
            file_picker_used=False,
            file_path_written=False,
            attachment_ready=False,
            attachment_verified=False,
            send_risk_detected=True,
            provider=provider,
            issues=route_issues,
        )

    if operator_report_path is None:
        return make_result(
            ok=False,
            result_label=BLOCKED_OPERATOR_REPORT_MISSING,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=True,
            operator_report_path=None,
            operator_report_sha256=None,
            expected_operator_report_sha256=expected_operator_report_sha256,
            operator_report_size_bytes=None,
            edge_target_ready=False,
            edge_target_focused=False,
            upload_trigger_attempted=False,
            file_picker_used=False,
            file_path_written=False,
            attachment_ready=False,
            attachment_verified=False,
            send_risk_detected=True,
            provider=provider,
            issues=("operator_report_path is required",),
        )

    report_path = Path(operator_report_path)
    if not report_path.exists() or not report_path.is_file():
        return make_result(
            ok=False,
            result_label=BLOCKED_OPERATOR_REPORT_MISSING,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=True,
            operator_report_path=str(report_path),
            operator_report_sha256=None,
            expected_operator_report_sha256=expected_operator_report_sha256,
            operator_report_size_bytes=None,
            edge_target_ready=False,
            edge_target_focused=False,
            upload_trigger_attempted=False,
            file_picker_used=False,
            file_path_written=False,
            attachment_ready=False,
            attachment_verified=False,
            send_risk_detected=True,
            provider=provider,
            issues=(f"operator report file not found: {report_path}",),
        )

    actual_hash = sha256_file(report_path)
    size_bytes = report_path.stat().st_size
    if expected_operator_report_sha256 and expected_operator_report_sha256 != actual_hash:
        return make_result(
            ok=False,
            result_label=BLOCKED_OPERATOR_REPORT_HASH_MISMATCH,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=True,
            operator_report_path=str(report_path),
            operator_report_sha256=actual_hash,
            expected_operator_report_sha256=expected_operator_report_sha256,
            operator_report_size_bytes=size_bytes,
            edge_target_ready=False,
            edge_target_focused=False,
            upload_trigger_attempted=False,
            file_picker_used=False,
            file_path_written=False,
            attachment_ready=False,
            attachment_verified=False,
            send_risk_detected=True,
            provider=provider,
            issues=("operator_report_sha256 does not match operator_report_path",),
        )

    try:
        adapter = build_adapter(provider)
    except Exception as exc:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_TARGET_NOT_READY,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=True,
            operator_report_path=str(report_path),
            operator_report_sha256=actual_hash,
            expected_operator_report_sha256=expected_operator_report_sha256,
            operator_report_size_bytes=size_bytes,
            edge_target_ready=False,
            edge_target_focused=False,
            upload_trigger_attempted=False,
            file_picker_used=False,
            file_path_written=False,
            attachment_ready=False,
            attachment_verified=False,
            send_risk_detected=False,
            provider=provider,
            issues=(str(exc),),
        )

    target = adapter.focus_target()
    if not target.ready or not target.focused:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_TARGET_NOT_READY,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            live_browser=live_browser,
            stop_before_send=stop_before_send,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=True,
            operator_report_path=str(report_path),
            operator_report_sha256=actual_hash,
            expected_operator_report_sha256=expected_operator_report_sha256,
            operator_report_size_bytes=size_bytes,
            edge_target_ready=target.ready,
            edge_target_focused=target.focused,
            upload_trigger_attempted=False,
            file_picker_used=False,
            file_path_written=False,
            attachment_ready=False,
            attachment_verified=False,
            send_risk_detected=False,
            target_window_count=target.target_window_count,
            matching_target_count=target.matching_target_count,
            selected_target_title=target.selected_target_title,
            attachment_candidate_count=target.attachment_candidate_count,
            provider=adapter.provider_name,
            issues=target.issues,
        )

    upload = adapter.attach_report_no_send(report_path)
    if upload.send_risk_detected:
        label = BLOCKED_SEND_RISK
    elif not upload.attachment_verified:
        label = BLOCKED_ATTACHMENT_NOT_VERIFIED
    else:
        label = PASS_EDGE_FAIL_REPORT_ATTACHED_NO_SEND

    return make_result(
        ok=upload.attachment_verified,
        result_label=label,
        patch_name=patch_name,
        patch_result=patch_result,
        selected_action=selected_action,
        browser_lane=browser_lane,
        live_browser=live_browser,
        stop_before_send=stop_before_send,
        confirmation_text_supplied=confirmation_text,
        confirmation_matched=True,
        operator_report_path=str(report_path),
        operator_report_sha256=actual_hash,
        expected_operator_report_sha256=expected_operator_report_sha256,
        operator_report_size_bytes=size_bytes,
        edge_target_ready=target.ready,
        edge_target_focused=target.focused,
        upload_trigger_attempted=upload.trigger_attempted,
        file_picker_used=upload.file_picker_used,
        file_path_written=upload.file_path_written,
        attachment_ready=upload.attachment_ready,
        attachment_verified=upload.attachment_verified,
        send_risk_detected=upload.send_risk_detected,
        target_window_count=target.target_window_count,
        matching_target_count=target.matching_target_count,
        selected_target_title=target.selected_target_title,
        attachment_candidate_count=target.attachment_candidate_count,
        provider=adapter.provider_name,
        issues=tuple(target.issues + upload.issues),
    )


def render_text(result: EdgeFailReportUploadNoSendResult) -> str:
    lines = [
        f"result_label: {result.result_label}",
        f"ok: {str(result.ok).lower()}",
        f"patch_name: {result.patch_name}",
        f"patch_result: {result.patch_result}",
        f"selected_action: {result.selected_action}",
        f"browser_lane: {result.browser_lane}",
        f"live_browser: {str(result.live_browser).lower()}",
        f"stop_before_send: {str(result.stop_before_send).lower()}",
        f"confirmation_text_supplied: {result.confirmation_text_supplied}",
        f"confirmation_matched: {str(result.confirmation_matched).lower()}",
        f"operator_report_path: {result.operator_report_path}",
        f"operator_report_sha256: {result.operator_report_sha256}",
        f"expected_operator_report_sha256: {result.expected_operator_report_sha256}",
        f"operator_report_size_bytes: {result.operator_report_size_bytes}",
        f"edge_target_ready: {str(result.edge_target_ready).lower()}",
        f"edge_target_focused: {str(result.edge_target_focused).lower()}",
        f"upload_trigger_attempted: {str(result.upload_trigger_attempted).lower()}",
        f"file_picker_used: {str(result.file_picker_used).lower()}",
        f"file_path_written: {str(result.file_path_written).lower()}",
        f"attachment_ready: {str(result.attachment_ready).lower()}",
        f"attachment_verified: {str(result.attachment_verified).lower()}",
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
        f"attachment_candidate_count: {result.attachment_candidate_count}",
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


def write_upload_evidence(
    result: EdgeFailReportUploadNoSendResult,
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
    parser = argparse.ArgumentParser(description="Edge FAIL/BLOCKED operator-report upload no-send probe")
    parser.add_argument("--armed-gate-path", default=str(DEFAULT_ARMED_GATE_PATH))
    parser.add_argument("--patch-name", default=None)
    parser.add_argument("--patch-result", default=None)
    parser.add_argument("--selected-action", default=None)
    parser.add_argument("--browser-lane", default=None)
    parser.add_argument("--operator-report-path", default=None)
    parser.add_argument("--operator-report-sha256", default=None)
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-ambiguous-target", "fake-no-attach-button", "fake-picker-fails", "fake-attachment-not-verified", "fake-send-risk", "pywinauto"), default="fake-ready")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--stop-before-send", action="store_true")
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    gate_patch_name, gate_patch_result, gate_selected_action, gate_browser_lane, gate_report_path, gate_report_hash = read_report_values_from_gate(Path(args.armed_gate_path))

    result = run_edge_fail_report_upload_no_send_probe(
        patch_name=normalize_optional_text(args.patch_name) or gate_patch_name,
        patch_result=normalize_optional_text(args.patch_result) or gate_patch_result,
        selected_action=normalize_optional_text(args.selected_action) or gate_selected_action,
        browser_lane=(normalize_optional_text(args.browser_lane) or gate_browser_lane or "edge").lower(),
        operator_report_path=normalize_optional_text(args.operator_report_path) or gate_report_path,
        expected_operator_report_sha256=normalize_optional_text(args.operator_report_sha256) or gate_report_hash,
        live_browser=bool(args.live_browser),
        confirmation_text=args.confirm_live_browser_text,
        stop_before_send=bool(args.stop_before_send),
        provider=args.provider,
    )

    if not args.no_write_evidence:
        write_upload_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))

    if args.json:
        print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(result), end="")

    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())