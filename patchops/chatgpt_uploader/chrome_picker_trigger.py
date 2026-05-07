from __future__ import annotations

import ctypes
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

PASS_NO_PICKER = "PASS_NO_PICKER"
PASS_ONE_PICKER_DETECTED = "PASS_ONE_PICKER_DETECTED"
BLOCKED_AMBIGUOUS_PICKER = "BLOCKED_AMBIGUOUS_PICKER"
BLOCKED_PICKER_ERROR_MODAL = "BLOCKED_PICKER_ERROR_MODAL"
BLOCKED_LIVE_BROWSER_CONFIRMATION_MISSING = "BLOCKED_LIVE_BROWSER_CONFIRMATION_MISSING"
PASS_CHROME_PICKER_OPENED_NO_UPLOAD = "PASS_CHROME_PICKER_OPENED_NO_UPLOAD"
FAIL_CHROME_PICKER_NOT_OPENED = "FAIL_CHROME_PICKER_NOT_OPENED"
BLOCKED_UNSAFE_TRIGGER = "BLOCKED_UNSAFE_TRIGGER"
BLOCKED_CHROME_TARGET_NOT_READY = "BLOCKED_CHROME_TARGET_NOT_READY"
LIVE_CONFIRM_TEXT = "PATCHOPS_CONFIRM_LIVE_BROWSER"
EXPECTED_BROWSER = "chrome"
SAFE_TRIGGER_NAME = "safe_slash_enter_once"

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
    "picker_open_attempted": False,
    "live_browser_used": False,
}

FORBIDDEN_TRIGGER_BACKENDS = {
    "ctrl_u",
    "tab_ladder",
    "random_click_ladder",
    "unbounded_retries",
    "unknown_keyboard_shortcut",
    "dom_query",
    "selenium",
    "webdriver",
    "browser_dom_automation",
    "plus_menu_crawling",
    "multi_picker_blind_selection",
}


@dataclass(frozen=True)
class ChromePickerCandidate:
    handle: int | None
    owner_handle: int | None
    class_name: str
    title_sha256: str | None
    title_length: int
    visible: bool
    enabled: bool
    filename_control_detected: bool
    open_button_or_shell_detected: bool
    owned_by_expected_chrome_flow: bool | None
    selected: bool = False


@dataclass(frozen=True)
class ChromePickerEvidence:
    ok: bool
    result: str
    expected_browser: str
    live_browser_used: bool
    picker_detected: bool
    picker_count: int
    ambiguous: bool
    error_modal_detected: bool
    error_modal_count: int
    picker_owned_by_expected_chrome_flow: bool | None
    selected_picker: dict[str, Any] | None
    picker_candidates: list[ChromePickerCandidate]
    error_modal_candidates: list[ChromePickerCandidate]
    observed_window_count: int
    raw_conversation_text_logged: bool
    file_upload_attempted: bool
    file_path_written: bool
    open_button_pressed: bool
    chatgpt_submit_performed: bool
    safety_flags: dict[str, bool]
    reason: str

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["picker_candidates"] = [asdict(candidate) for candidate in self.picker_candidates]
        payload["error_modal_candidates"] = [asdict(candidate) for candidate in self.error_modal_candidates]
        return payload


@dataclass(frozen=True)
class ChromePickerTriggerPlan:
    ok: bool
    result: str
    trigger_name: str
    sequence: tuple[str, ...]
    forbidden_backend_detected: str | None
    safe_click_x_ratio: float
    safe_click_y_ratio: float
    max_attempts: int
    allow_path_write: bool
    allow_open_press: bool
    allow_send: bool
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChromePickerTriggerEvidence:
    ok: bool
    result: str
    expected_browser: str
    live_browser_used: bool
    trigger_plan: dict[str, Any]
    preflight_ready: bool
    safe_click_performed: bool
    slash_trigger_attempted: bool
    enter_pressed_for_picker_command: bool
    picker_detected_after_trigger: bool
    picker_result_after_trigger: str | None
    file_path_written: bool
    open_button_pressed: bool
    file_upload_attempted: bool
    chatgpt_submit_performed: bool
    raw_conversation_text_logged: bool
    safety_flags: dict[str, bool]
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _truthy(value: object) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _as_payload(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "to_payload"):
        payload = value.to_payload()
        if isinstance(payload, dict):
            return dict(payload)
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def build_picker_candidate(
    *,
    handle: int | None = None,
    owner_handle: int | None = None,
    class_name: str = "#32770",
    title_sha256: str | None = "synthetic-title-sha256",
    title_length: int = 4,
    visible: bool = True,
    enabled: bool = True,
    filename_control_detected: bool = True,
    open_button_or_shell_detected: bool = True,
    expected_chrome_hwnd: int | None = None,
    selected: bool = False,
) -> ChromePickerCandidate:
    owned: bool | None
    if expected_chrome_hwnd is None or owner_handle is None:
        owned = None
    else:
        owned = int(owner_handle) == int(expected_chrome_hwnd)
    return ChromePickerCandidate(
        handle=handle,
        owner_handle=owner_handle,
        class_name=class_name,
        title_sha256=title_sha256,
        title_length=int(title_length or 0),
        visible=bool(visible),
        enabled=bool(enabled),
        filename_control_detected=bool(filename_control_detected),
        open_button_or_shell_detected=bool(open_button_or_shell_detected),
        owned_by_expected_chrome_flow=owned,
        selected=bool(selected),
    )


def candidate_from_windows_descriptor(payload: Mapping[str, Any], *, expected_chrome_hwnd: int | None = None, selected: bool = False) -> ChromePickerCandidate:
    child_counts = dict(payload.get("child_class_counts") or {})
    child_classes = {str(key).lower() for key in child_counts}
    filename_control = bool(child_classes.intersection({"edit", "combobox", "comboboxex32"}))
    open_or_shell = bool(child_classes.intersection({"button", "directuihwnd", "shelldll_defview"}))
    return build_picker_candidate(
        handle=payload.get("handle"),
        owner_handle=payload.get("owner_handle"),
        class_name=str(payload.get("class_name") or ""),
        title_sha256=payload.get("title_sha256"),
        title_length=int(payload.get("title_length") or 0),
        visible=_truthy(payload.get("visible")),
        enabled=_truthy(payload.get("enabled")),
        filename_control_detected=filename_control,
        open_button_or_shell_detected=open_or_shell,
        expected_chrome_hwnd=expected_chrome_hwnd,
        selected=selected,
    )


def evaluate_chrome_picker_detection(
    picker_candidates: Sequence[ChromePickerCandidate],
    *,
    error_modal_candidates: Sequence[ChromePickerCandidate] = (),
    observed_window_count: int | None = None,
    expected_chrome_hwnd: int | None = None,
    live_browser_used: bool = False,
    reason: str | None = None,
) -> ChromePickerEvidence:
    pickers = list(picker_candidates)
    errors = list(error_modal_candidates)
    safety = dict(SAFETY_FLAGS)
    safety["live_browser_used"] = bool(live_browser_used)
    selected_picker: dict[str, Any] | None = None
    owned: bool | None = None

    if errors:
        result = BLOCKED_PICKER_ERROR_MODAL
        ok = False
        final_reason = reason or "picker_error_modal_detected"
    elif len(pickers) == 0:
        result = PASS_NO_PICKER
        ok = True
        final_reason = reason or "no_picker_detected"
    elif len(pickers) > 1:
        result = BLOCKED_AMBIGUOUS_PICKER
        ok = False
        final_reason = reason or "multiple_picker_candidates_detected"
    else:
        result = PASS_ONE_PICKER_DETECTED
        ok = True
        candidate = pickers[0]
        owned = candidate.owned_by_expected_chrome_flow
        selected = ChromePickerCandidate(
            handle=candidate.handle,
            owner_handle=candidate.owner_handle,
            class_name=candidate.class_name,
            title_sha256=candidate.title_sha256,
            title_length=candidate.title_length,
            visible=candidate.visible,
            enabled=candidate.enabled,
            filename_control_detected=candidate.filename_control_detected,
            open_button_or_shell_detected=candidate.open_button_or_shell_detected,
            owned_by_expected_chrome_flow=candidate.owned_by_expected_chrome_flow,
            selected=True,
        )
        selected_picker = asdict(selected)
        pickers = [selected]
        final_reason = reason or "single_picker_detected"

    if result != PASS_ONE_PICKER_DETECTED:
        pickers = [
            ChromePickerCandidate(
                handle=c.handle,
                owner_handle=c.owner_handle,
                class_name=c.class_name,
                title_sha256=c.title_sha256,
                title_length=c.title_length,
                visible=c.visible,
                enabled=c.enabled,
                filename_control_detected=c.filename_control_detected,
                open_button_or_shell_detected=c.open_button_or_shell_detected,
                owned_by_expected_chrome_flow=c.owned_by_expected_chrome_flow,
                selected=False,
            )
            for c in pickers
        ]

    return ChromePickerEvidence(
        ok=ok,
        result=result,
        expected_browser=EXPECTED_BROWSER,
        live_browser_used=bool(live_browser_used),
        picker_detected=bool(pickers),
        picker_count=len(pickers),
        ambiguous=len(pickers) > 1,
        error_modal_detected=bool(errors),
        error_modal_count=len(errors),
        picker_owned_by_expected_chrome_flow=owned,
        selected_picker=selected_picker,
        picker_candidates=list(pickers),
        error_modal_candidates=list(errors),
        observed_window_count=int(observed_window_count if observed_window_count is not None else len(pickers) + len(errors)),
        raw_conversation_text_logged=False,
        file_upload_attempted=False,
        file_path_written=False,
        open_button_pressed=False,
        chatgpt_submit_performed=False,
        safety_flags=safety,
        reason=final_reason,
    )


def adapt_windows_picker_detection(detection: Any, *, expected_chrome_hwnd: int | None = None, live_browser_used: bool = False) -> ChromePickerEvidence:
    payload = _as_payload(detection)
    picker_payloads = list(payload.get("picker_candidates") or [])
    error_payloads = list(payload.get("error_modal_candidates") or [])
    selected_payload = payload.get("selected_picker")
    if selected_payload and not picker_payloads:
        picker_payloads = [selected_payload]
    pickers = [candidate_from_windows_descriptor(item, expected_chrome_hwnd=expected_chrome_hwnd) for item in picker_payloads]
    errors = [candidate_from_windows_descriptor(item, expected_chrome_hwnd=expected_chrome_hwnd) for item in error_payloads]
    if payload.get("error_modal_detected") and not errors:
        errors = [build_picker_candidate(handle=None, class_name="#32770", title_sha256=None, title_length=0, expected_chrome_hwnd=expected_chrome_hwnd)]
    return evaluate_chrome_picker_detection(
        pickers,
        error_modal_candidates=errors,
        observed_window_count=int(payload.get("observed_window_count") or len(pickers) + len(errors)),
        expected_chrome_hwnd=expected_chrome_hwnd,
        live_browser_used=live_browser_used,
        reason=str(payload.get("reason") or payload.get("status") or "windows_picker_detection_adapted"),
    )


def detect_live_windows_picker(*, wait_seconds: float = 0.0, poll_interval_seconds: float = 0.5, expected_chrome_hwnd: int | None = None) -> ChromePickerEvidence:
    from patchops.chatgpt_uploader.windows_file_picker import detect_file_picker
    detection = detect_file_picker(wait_seconds=wait_seconds, poll_interval_seconds=poll_interval_seconds)
    return adapt_windows_picker_detection(detection, expected_chrome_hwnd=expected_chrome_hwnd, live_browser_used=True)


def validate_trigger_backend(trigger_backend: str) -> ChromePickerTriggerPlan:
    normalized = str(trigger_backend or "").strip().lower()
    sequence = ("focus_chrome_target", "safe_composer_focus_once", "slash_once", "enter_once", "detect_picker", "stop")
    if normalized != SAFE_TRIGGER_NAME:
        forbidden = normalized if normalized in FORBIDDEN_TRIGGER_BACKENDS or normalized else "unknown_keyboard_shortcut"
        return ChromePickerTriggerPlan(
            ok=False,
            result=BLOCKED_UNSAFE_TRIGGER,
            trigger_name=normalized or "<missing>",
            sequence=(),
            forbidden_backend_detected=forbidden,
            safe_click_x_ratio=0.0,
            safe_click_y_ratio=0.0,
            max_attempts=0,
            allow_path_write=False,
            allow_open_press=False,
            allow_send=False,
            reason=f"Blocked unsafe picker trigger backend: {forbidden}",
        )
    return ChromePickerTriggerPlan(
        ok=True,
        result="PASS_TRIGGER_POLICY_VALIDATED",
        trigger_name=SAFE_TRIGGER_NAME,
        sequence=sequence,
        forbidden_backend_detected=None,
        safe_click_x_ratio=0.50,
        safe_click_y_ratio=0.34,
        max_attempts=1,
        allow_path_write=False,
        allow_open_press=False,
        allow_send=False,
        reason="Single safe slash-enter picker trigger policy validated.",
    )


def _blocked_trigger_evidence(*, result: str, plan: ChromePickerTriggerPlan, reason: str, live_browser_used: bool = False, preflight_ready: bool = False) -> ChromePickerTriggerEvidence:
    safety = dict(SAFETY_FLAGS)
    safety["live_browser_used"] = bool(live_browser_used)
    return ChromePickerTriggerEvidence(
        ok=False,
        result=result,
        expected_browser=EXPECTED_BROWSER,
        live_browser_used=bool(live_browser_used),
        trigger_plan=plan.to_payload(),
        preflight_ready=bool(preflight_ready),
        safe_click_performed=False,
        slash_trigger_attempted=False,
        enter_pressed_for_picker_command=False,
        picker_detected_after_trigger=False,
        picker_result_after_trigger=None,
        file_path_written=False,
        open_button_pressed=False,
        file_upload_attempted=False,
        chatgpt_submit_performed=False,
        raw_conversation_text_logged=False,
        safety_flags=safety,
        reason=reason,
    )


def _get_window_rect(hwnd: int) -> tuple[int, int, int, int]:
    rect = ctypes.wintypes.RECT()
    user32 = ctypes.windll.user32
    if not user32.GetWindowRect(int(hwnd), ctypes.byref(rect)):
        raise RuntimeError("GetWindowRect failed")
    return int(rect.left), int(rect.top), int(rect.right), int(rect.bottom)


def _safe_click_window_point(hwnd: int, x_ratio: float, y_ratio: float) -> None:
    user32 = ctypes.windll.user32
    left, top, right, bottom = _get_window_rect(hwnd)
    x = left + int((right - left) * float(x_ratio))
    y = top + int((bottom - top) * float(y_ratio))
    user32.SetForegroundWindow(int(hwnd))
    time.sleep(0.25)
    user32.SetCursorPos(int(x), int(y))
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    user32.mouse_event(0x0004, 0, 0, 0, 0)


def _press_key(vk: int) -> None:
    user32 = ctypes.windll.user32
    user32.keybd_event(int(vk), 0, 0, 0)
    user32.keybd_event(int(vk), 0, 0x0002, 0)


def _press_slash_enter_once() -> None:
    _press_key(0xBF)
    time.sleep(0.20)
    _press_key(0x0D)


def run_chrome_picker_trigger(
    *,
    trigger_backend: str = SAFE_TRIGGER_NAME,
    preflight_ready: bool = False,
    expected_chrome_hwnd: int | None = None,
    live_browser: bool = False,
    confirm_live_browser_text: str | None = None,
    post_trigger_picker_evidence: ChromePickerEvidence | Mapping[str, Any] | None = None,
    wait_seconds: float = 4.0,
    poll_interval_seconds: float = 0.5,
) -> ChromePickerTriggerEvidence:
    plan = validate_trigger_backend(trigger_backend)
    if not plan.ok:
        return _blocked_trigger_evidence(result=BLOCKED_UNSAFE_TRIGGER, plan=plan, reason=plan.reason, live_browser_used=False, preflight_ready=False)

    if not preflight_ready:
        return _blocked_trigger_evidence(
            result=BLOCKED_CHROME_TARGET_NOT_READY,
            plan=plan,
            reason="Chrome target preflight is not ready.",
            live_browser_used=False,
            preflight_ready=False,
        )

    if live_browser and confirm_live_browser_text != LIVE_CONFIRM_TEXT:
        return _blocked_trigger_evidence(
            result=BLOCKED_LIVE_BROWSER_CONFIRMATION_MISSING,
            plan=plan,
            reason=f"Live picker trigger requires --confirm-live-browser-text {LIVE_CONFIRM_TEXT}.",
            live_browser_used=False,
            preflight_ready=True,
        )

    safety = dict(SAFETY_FLAGS)
    safety["picker_open_attempted"] = bool(live_browser)
    safety["live_browser_used"] = bool(live_browser)

    safe_click_performed = False
    slash_attempted = False
    enter_attempted = False

    if live_browser:
        if expected_chrome_hwnd is None:
            return _blocked_trigger_evidence(
                result=BLOCKED_CHROME_TARGET_NOT_READY,
                plan=plan,
                reason="Live picker trigger requires expected_chrome_hwnd from Chrome preflight.",
                live_browser_used=False,
                preflight_ready=True,
            )
        _safe_click_window_point(int(expected_chrome_hwnd), plan.safe_click_x_ratio, plan.safe_click_y_ratio)
        safe_click_performed = True
        _press_slash_enter_once()
        slash_attempted = True
        enter_attempted = True
        picker_evidence = detect_live_windows_picker(
            wait_seconds=wait_seconds,
            poll_interval_seconds=poll_interval_seconds,
            expected_chrome_hwnd=expected_chrome_hwnd,
        )
    else:
        if post_trigger_picker_evidence is None:
            picker_evidence = evaluate_chrome_picker_detection([], expected_chrome_hwnd=expected_chrome_hwnd)
        elif isinstance(post_trigger_picker_evidence, ChromePickerEvidence):
            picker_evidence = post_trigger_picker_evidence
        else:
            picker_evidence = adapt_windows_picker_detection(post_trigger_picker_evidence, expected_chrome_hwnd=expected_chrome_hwnd, live_browser_used=False)

    picker_detected = picker_evidence.result == PASS_ONE_PICKER_DETECTED
    result = PASS_CHROME_PICKER_OPENED_NO_UPLOAD if picker_detected else FAIL_CHROME_PICKER_NOT_OPENED
    ok = bool(picker_detected)
    reason = "Picker opened and detected; stopped before path write, Open/Enter file selection, upload, or send." if ok else f"Picker was not opened/detected; detector result was {picker_evidence.result}."

    return ChromePickerTriggerEvidence(
        ok=ok,
        result=result,
        expected_browser=EXPECTED_BROWSER,
        live_browser_used=bool(live_browser),
        trigger_plan=plan.to_payload(),
        preflight_ready=True,
        safe_click_performed=safe_click_performed,
        slash_trigger_attempted=slash_attempted,
        enter_pressed_for_picker_command=enter_attempted,
        picker_detected_after_trigger=picker_detected,
        picker_result_after_trigger=picker_evidence.result,
        file_path_written=False,
        open_button_pressed=False,
        file_upload_attempted=False,
        chatgpt_submit_performed=False,
        raw_conversation_text_logged=False,
        safety_flags=safety,
        reason=reason,
    )


def write_chrome_picker_evidence(evidence: ChromePickerEvidence, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evidence.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_chrome_picker_trigger_evidence(evidence: ChromePickerTriggerEvidence, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evidence.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path