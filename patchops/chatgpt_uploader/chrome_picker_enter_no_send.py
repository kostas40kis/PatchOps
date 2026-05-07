from __future__ import annotations

import ctypes
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from patchops.chatgpt_uploader.chrome_picker_path_entry import (
    BLOCKED_CANONICAL_REPORT_MISSING,
    BLOCKED_PATH_NOT_CANONICAL_REPORT,
    hash_path,
    validate_canonical_report_path,
)

PASS_CHROME_PICKER_ENTERED_NO_SEND = "PASS_CHROME_PICKER_ENTERED_NO_SEND"
FAIL_PICKER_NOT_CLOSED_AFTER_ENTER = "FAIL_PICKER_NOT_CLOSED_AFTER_ENTER"
FAIL_PATH_ENTER_FAILED = "FAIL_PATH_ENTER_FAILED"
BLOCKED_PICKER_NOT_READY = "BLOCKED_PICKER_NOT_READY"
BLOCKED_PATH_NOT_WRITTEN = "BLOCKED_PATH_NOT_WRITTEN"
BLOCKED_PICKER_ENTER_CONFIRMATION_MISSING = "BLOCKED_PICKER_ENTER_CONFIRMATION_MISSING"
BLOCKED_PICKER_HWND_MISSING = "BLOCKED_PICKER_HWND_MISSING"

EXPECTED_BROWSER = "chrome"
LIVE_CONFIRM_TEXT = "PATCHOPS_CONFIRM_PICKER_ENTER_NO_SEND"

SAFETY_FLAGS = {
    "selenium_used": False,
    "webdriver_used": False,
    "browser_dom_automation_used": False,
    "cloudflare_bypass_attempted": False,
    "captcha_bypass_attempted": False,
    "conversation_text_logged": False,
    "raw_conversation_text_logged": False,
    "random_page_click_performed": False,
    "chatgpt_submit_performed": False,
    "file_upload_attempted": False,
    "file_path_written": False,
    "open_button_pressed": False,
    "enter_pressed": False,
    "file_selected": False,
    "attachment_confirmed": False,
    "live_browser_used": False,
}


@dataclass(frozen=True)
class PickerEnterNoSendPlan:
    ok: bool
    result: str
    expected_browser: str
    canonical_report: dict[str, Any]
    sequence: tuple[str, ...]
    allow_enter_press: bool
    allow_open_button_press: bool
    allow_send: bool
    allow_attachment_claim: bool
    max_enter_presses: int
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PickerEnterNoSendEvidence:
    ok: bool
    result: str
    expected_browser: str
    live_browser_used: bool
    picker_ready: bool
    picker_hwnd: int | None
    path_written_before_enter: bool
    canonical_report: dict[str, Any]
    enter_plan: dict[str, Any]
    report_path_hash: str | None
    report_basename: str | None
    enter_pressed: bool
    picker_closed_after_enter: bool
    file_upload_attempted: bool
    open_button_pressed: bool
    chatgpt_submit_performed: bool
    attachment_confirmed: bool
    raw_conversation_text_logged: bool
    safety_flags: dict[str, bool]
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def build_picker_enter_plan(canonical_report_path: Path | str) -> PickerEnterNoSendPlan:
    report = validate_canonical_report_path(canonical_report_path)
    if not report.ok:
        return PickerEnterNoSendPlan(
            ok=False,
            result=report.result,
            expected_browser=EXPECTED_BROWSER,
            canonical_report=report.to_payload(),
            sequence=(),
            allow_enter_press=False,
            allow_open_button_press=False,
            allow_send=False,
            allow_attachment_claim=False,
            max_enter_presses=0,
            reason=report.reason,
        )
    return PickerEnterNoSendPlan(
        ok=True,
        result="PASS_PICKER_ENTER_PLAN_READY",
        expected_browser=EXPECTED_BROWSER,
        canonical_report=report.to_payload(),
        sequence=(
            "validate_canonical_report_path",
            "require_picker_ready",
            "require_path_written_before_enter",
            "press_enter_once_inside_picker",
            "wait_for_picker_close",
            "stop_before_send",
        ),
        allow_enter_press=True,
        allow_open_button_press=False,
        allow_send=False,
        allow_attachment_claim=False,
        max_enter_presses=1,
        reason="Picker Enter plan validated; one Enter press is allowed only inside a confirmed picker and send remains blocked.",
    )


def _blocked_evidence(*, result: str, plan: PickerEnterNoSendPlan, reason: str, picker_ready: bool = False, picker_hwnd: int | None = None, path_written_before_enter: bool = False, live_browser_used: bool = False) -> PickerEnterNoSendEvidence:
    safety = dict(SAFETY_FLAGS)
    safety["live_browser_used"] = bool(live_browser_used)
    report_payload = plan.canonical_report
    return PickerEnterNoSendEvidence(
        ok=False,
        result=result,
        expected_browser=EXPECTED_BROWSER,
        live_browser_used=bool(live_browser_used),
        picker_ready=bool(picker_ready),
        picker_hwnd=picker_hwnd,
        path_written_before_enter=bool(path_written_before_enter),
        canonical_report=report_payload,
        enter_plan=plan.to_payload(),
        report_path_hash=report_payload.get("path_hash") if isinstance(report_payload, dict) else None,
        report_basename=report_payload.get("basename") if isinstance(report_payload, dict) else None,
        enter_pressed=False,
        picker_closed_after_enter=False,
        file_upload_attempted=False,
        open_button_pressed=False,
        chatgpt_submit_performed=False,
        attachment_confirmed=False,
        raw_conversation_text_logged=False,
        safety_flags=safety,
        reason=reason,
    )


def _press_enter_once() -> bool:
    user32 = ctypes.windll.user32
    VK_RETURN = 0x0D
    user32.keybd_event(VK_RETURN, 0, 0, 0)
    user32.keybd_event(VK_RETURN, 0, 0x0002, 0)
    return True


def _window_exists(hwnd: int) -> bool:
    return bool(ctypes.windll.user32.IsWindow(int(hwnd)))


def _wait_for_picker_close(picker_hwnd: int, timeout_seconds: float, poll_interval_seconds: float) -> bool:
    deadline = time.time() + max(0.0, float(timeout_seconds))
    while time.time() <= deadline:
        if not _window_exists(int(picker_hwnd)):
            return True
        time.sleep(max(0.05, float(poll_interval_seconds)))
    return not _window_exists(int(picker_hwnd))


def run_picker_enter_no_send(
    *,
    canonical_report_path: Path | str,
    picker_ready: bool = False,
    picker_hwnd: int | None = None,
    path_written_before_enter: bool = False,
    live_browser: bool = False,
    allow_picker_enter: bool = False,
    confirm_live_browser_text: str | None = None,
    mock_enter_success: bool = False,
    mock_picker_closed_after_enter: bool = False,
    wait_seconds: float = 8.0,
    poll_interval_seconds: float = 0.25,
) -> PickerEnterNoSendEvidence:
    plan = build_picker_enter_plan(canonical_report_path)
    if not plan.ok:
        return _blocked_evidence(result=plan.result, plan=plan, reason=plan.reason)

    if not picker_ready:
        return _blocked_evidence(
            result=BLOCKED_PICKER_NOT_READY,
            plan=plan,
            reason="Picker must be confirmed ready before pressing Enter.",
            picker_ready=False,
            picker_hwnd=picker_hwnd,
            path_written_before_enter=path_written_before_enter,
        )

    if not path_written_before_enter:
        return _blocked_evidence(
            result=BLOCKED_PATH_NOT_WRITTEN,
            plan=plan,
            reason="Exact canonical report path must already be written before pressing Enter.",
            picker_ready=True,
            picker_hwnd=picker_hwnd,
            path_written_before_enter=False,
        )

    report = validate_canonical_report_path(canonical_report_path)
    resolved = Path(canonical_report_path).expanduser().resolve()
    path_digest = hash_path(resolved)
    basename = resolved.name
    safety = dict(SAFETY_FLAGS)

    if live_browser:
        if confirm_live_browser_text != LIVE_CONFIRM_TEXT or not allow_picker_enter:
            return _blocked_evidence(
                result=BLOCKED_PICKER_ENTER_CONFIRMATION_MISSING,
                plan=plan,
                reason=f"Live Enter requires --allow-picker-enter and --confirm-live-browser-text {LIVE_CONFIRM_TEXT}.",
                picker_ready=True,
                picker_hwnd=picker_hwnd,
                path_written_before_enter=True,
                live_browser_used=False,
            )
        if picker_hwnd is None:
            return _blocked_evidence(
                result=BLOCKED_PICKER_HWND_MISSING,
                plan=plan,
                reason="Live Enter requires picker_hwnd from picker detection evidence.",
                picker_ready=True,
                picker_hwnd=None,
                path_written_before_enter=True,
                live_browser_used=False,
            )
        try:
            ctypes.windll.user32.SetForegroundWindow(int(picker_hwnd))
            time.sleep(0.15)
            enter_ok = _press_enter_once()
        except Exception as exc:
            return _blocked_evidence(
                result=FAIL_PATH_ENTER_FAILED,
                plan=plan,
                reason=f"Enter key press failed: {exc}",
                picker_ready=True,
                picker_hwnd=picker_hwnd,
                path_written_before_enter=True,
                live_browser_used=True,
            )
        closed = _wait_for_picker_close(int(picker_hwnd), wait_seconds, poll_interval_seconds) if enter_ok else False
        if not closed:
            safety["live_browser_used"] = True
            safety["enter_pressed"] = bool(enter_ok)
            safety["file_upload_attempted"] = bool(enter_ok)
            return PickerEnterNoSendEvidence(
                ok=False,
                result=FAIL_PICKER_NOT_CLOSED_AFTER_ENTER,
                expected_browser=EXPECTED_BROWSER,
                live_browser_used=True,
                picker_ready=True,
                picker_hwnd=picker_hwnd,
                path_written_before_enter=True,
                canonical_report=report.to_payload(),
                enter_plan=plan.to_payload(),
                report_path_hash=path_digest,
                report_basename=basename,
                enter_pressed=bool(enter_ok),
                picker_closed_after_enter=False,
                file_upload_attempted=bool(enter_ok),
                open_button_pressed=False,
                chatgpt_submit_performed=False,
                attachment_confirmed=False,
                raw_conversation_text_logged=False,
                safety_flags=safety,
                reason="Enter was pressed but the picker did not close before timeout; upload is not verified and send remains blocked.",
            )
        safety["live_browser_used"] = True
        safety["enter_pressed"] = True
        safety["file_upload_attempted"] = True
        return PickerEnterNoSendEvidence(
            ok=True,
            result=PASS_CHROME_PICKER_ENTERED_NO_SEND,
            expected_browser=EXPECTED_BROWSER,
            live_browser_used=True,
            picker_ready=True,
            picker_hwnd=picker_hwnd,
            path_written_before_enter=True,
            canonical_report=report.to_payload(),
            enter_plan=plan.to_payload(),
            report_path_hash=path_digest,
            report_basename=basename,
            enter_pressed=True,
            picker_closed_after_enter=True,
            file_upload_attempted=True,
            open_button_pressed=False,
            chatgpt_submit_performed=False,
            attachment_confirmed=False,
            raw_conversation_text_logged=False,
            safety_flags=safety,
            reason="Enter pressed inside picker and picker closed; stopped before send and before attachment verification claim.",
        )

    if mock_enter_success:
        result = PASS_CHROME_PICKER_ENTERED_NO_SEND if mock_picker_closed_after_enter else FAIL_PICKER_NOT_CLOSED_AFTER_ENTER
        safety["enter_pressed"] = True
        safety["file_upload_attempted"] = True
        return PickerEnterNoSendEvidence(
            ok=bool(mock_picker_closed_after_enter),
            result=result,
            expected_browser=EXPECTED_BROWSER,
            live_browser_used=False,
            picker_ready=True,
            picker_hwnd=picker_hwnd,
            path_written_before_enter=True,
            canonical_report=report.to_payload(),
            enter_plan=plan.to_payload(),
            report_path_hash=path_digest,
            report_basename=basename,
            enter_pressed=True,
            picker_closed_after_enter=bool(mock_picker_closed_after_enter),
            file_upload_attempted=True,
            open_button_pressed=False,
            chatgpt_submit_performed=False,
            attachment_confirmed=False,
            raw_conversation_text_logged=False,
            safety_flags=safety,
            reason="Mock Enter path exercised; no live UI action was performed.",
        )

    return _blocked_evidence(
        result=FAIL_PATH_ENTER_FAILED,
        plan=plan,
        reason="No live Enter confirmation or mock Enter success was provided.",
        picker_ready=True,
        picker_hwnd=picker_hwnd,
        path_written_before_enter=True,
    )


def write_picker_enter_no_send_evidence(evidence: PickerEnterNoSendEvidence, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evidence.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path