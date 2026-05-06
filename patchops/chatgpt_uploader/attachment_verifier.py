from __future__ import annotations

import importlib.util
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from patchops.chatgpt_uploader.config import load_config
from patchops.chatgpt_uploader.edge_target import focus_chatgpt_edge_target


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def pywinauto_available() -> bool:
    return importlib.util.find_spec("pywinauto") is not None


@dataclass(frozen=True)
class AttachmentVerificationResult:
    status: str
    reason: str
    expected_filename: str
    expected_extension: str
    edge_status: str
    match_count: int
    matched_control_types: list[str]
    matched_name_samples: list[str]
    safety_flags: dict[str, bool]
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def attachment_verifier_safety_flags(*, inspected: bool = False) -> dict[str, bool]:
    return {
        "attachment_verification_attempted": bool(inspected),
        "edge_uia_inspected": bool(inspected),
        "expected_filename_only": True,
        "conversation_text_logged": False,
        "chatgpt_submit_performed": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
        "random_page_click_performed": False,
        "file_picker_open_attempted": False,
        "file_path_written": False,
        "picker_enter_pressed": False,
        "file_upload_attempted": False,
    }


def _result(
    *,
    status: str,
    reason: str,
    expected_filename: str,
    expected_extension: str,
    edge_status: str = "NOT_RUN",
    match_count: int = 0,
    matched_control_types: Iterable[str] = (),
    matched_name_samples: Iterable[str] = (),
    inspected: bool = False,
) -> AttachmentVerificationResult:
    return AttachmentVerificationResult(
        status=status,
        reason=reason,
        expected_filename=expected_filename,
        expected_extension=expected_extension,
        edge_status=edge_status,
        match_count=int(match_count),
        matched_control_types=list(matched_control_types)[:10],
        matched_name_samples=list(matched_name_samples)[:5],
        safety_flags=attachment_verifier_safety_flags(inspected=inspected),
        created_at=utc_now_iso(),
    )


def _desktop():
    from pywinauto import Desktop  # type: ignore
    return Desktop(backend="uia")


def _control_name(control: Any) -> tuple[str, str]:
    try:
        info = control.element_info
    except Exception:
        info = None
    name = ""
    control_type = ""
    try:
        name = str(getattr(info, "name", "") or control.window_text() or "")
    except Exception:
        name = ""
    try:
        control_type = str(getattr(info, "control_type", "") or "")
    except Exception:
        control_type = ""
    return name, control_type


def _edge_window_from_focus(target_config_path: str | Path, *, timeout_seconds: int = 10) -> tuple[str, Any | None]:
    cfg = load_config(target_config_path)
    result = focus_chatgpt_edge_target(target_url=cfg.target_url, allow_launch=False, timeout_seconds=max(1, int(timeout_seconds)))
    status = str(result.get("status") or "UNKNOWN")
    selected = result.get("selected_target_window") or {}
    handle = selected.get("handle")
    if status != "PASS" or handle is None:
        return status, None
    try:
        return status, _desktop().window(handle=int(handle))
    except Exception:
        return "FAIL_EDGE_WINDOW_ATTACH", None


def _iter_relevant_controls(edge_window: Any) -> Iterable[Any]:
    # UIA-only, no DOM/browser automation. We inspect accessible names for the expected filename only.
    for control_type in ("Text", "Button", "ListItem", "Custom", "DataItem", "Edit", "Pane"):
        try:
            for control in edge_window.descendants(control_type=control_type):
                yield control
        except Exception:
            continue


def scan_attachment_visible_once(
    *,
    target_config_path: str | Path,
    expected_report_path: str | Path,
    timeout_seconds: int = 10,
) -> AttachmentVerificationResult:
    expected = Path(expected_report_path).name
    extension = Path(expected_report_path).suffix.lower()
    if not expected:
        return _result(status="BLOCKED_EXPECTED_FILENAME_EMPTY", reason="expected report filename is empty", expected_filename="", expected_extension=extension)
    if not pywinauto_available():
        return _result(status="BLOCKED_MISSING_PYWINAUTO", reason="pywinauto is required for UIA attachment verification", expected_filename=expected, expected_extension=extension)
    edge_status, edge_window = _edge_window_from_focus(target_config_path, timeout_seconds=timeout_seconds)
    if edge_window is None:
        return _result(status="FAIL_EDGE_NOT_FOCUSED", reason=edge_status, expected_filename=expected, expected_extension=extension, edge_status=edge_status, inspected=False)
    needle = expected.lower()
    match_types: list[str] = []
    samples: list[str] = []
    seen_samples: set[str] = set()
    count = 0
    try:
        controls = list(_iter_relevant_controls(edge_window))
    except Exception as exc:
        return _result(status="FAIL_EDGE_UIA_SCAN", reason=str(exc), expected_filename=expected, expected_extension=extension, edge_status=edge_status, inspected=True)
    for control in controls:
        name, control_type = _control_name(control)
        if not name:
            continue
        # Do not log arbitrary conversation text. Only keep names that contain the expected filename.
        if needle in name.lower():
            count += 1
            if control_type and control_type not in match_types:
                match_types.append(control_type)
            if name not in seen_samples:
                seen_samples.add(name)
                samples.append(name[:240])
    if count > 0:
        return _result(
            status="PASS_ATTACHMENT_VISIBLE_NO_SEND",
            reason="expected report filename is visible in Edge UIA tree; ChatGPT send not performed",
            expected_filename=expected,
            expected_extension=extension,
            edge_status=edge_status,
            match_count=count,
            matched_control_types=match_types,
            matched_name_samples=samples,
            inspected=True,
        )
    return _result(
        status="FAIL_ATTACHMENT_NOT_VISIBLE_NO_SEND",
        reason="expected report filename was not found in Edge UIA tree before timeout",
        expected_filename=expected,
        expected_extension=extension,
        edge_status=edge_status,
        match_count=0,
        inspected=True,
    )


def wait_for_attachment_visible(
    *,
    target_config_path: str | Path,
    expected_report_path: str | Path,
    wait_seconds: float = 20.0,
    poll_interval_seconds: float = 0.75,
    focus_timeout_seconds: int = 10,
) -> AttachmentVerificationResult:
    deadline = time.monotonic() + max(0.0, float(wait_seconds))
    last = scan_attachment_visible_once(
        target_config_path=target_config_path,
        expected_report_path=expected_report_path,
        timeout_seconds=focus_timeout_seconds,
    )
    if last.status == "PASS_ATTACHMENT_VISIBLE_NO_SEND" or last.status.startswith("BLOCKED_"):
        return last
    while time.monotonic() < deadline:
        time.sleep(max(0.1, float(poll_interval_seconds)))
        last = scan_attachment_visible_once(
            target_config_path=target_config_path,
            expected_report_path=expected_report_path,
            timeout_seconds=focus_timeout_seconds,
        )
        if last.status == "PASS_ATTACHMENT_VISIBLE_NO_SEND" or last.status.startswith("BLOCKED_"):
            return last
    return last


def write_attachment_verification_evidence(result: AttachmentVerificationResult, evidence_dir: str | Path, *, basename: str = "u2_07_attachment_verification") -> tuple[Path, Path]:
    root = Path(evidence_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    safe_base = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in basename).strip("_") or "attachment_verification"
    json_path = root / f"{safe_base}.json"
    txt_path = root / f"{safe_base}.txt"
    json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "PATCHOPS CHATGPT UPLOADER ATTACHMENT VERIFICATION",
        "==================================================",
        f"Status                         : {result.status}",
        f"Reason                         : {result.reason}",
        f"ExpectedFilename               : {result.expected_filename}",
        f"ExpectedExtension              : {result.expected_extension}",
        f"EdgeStatus                     : {result.edge_status}",
        f"MatchCount                     : {result.match_count}",
        f"MatchedControlTypes            : {result.matched_control_types}",
        f"AttachmentVerificationAttempted: {str(result.safety_flags['attachment_verification_attempted']).lower()}",
        f"EdgeUiaInspected               : {str(result.safety_flags['edge_uia_inspected']).lower()}",
        "ConversationTextLogged         : false",
        "ChatGPTSubmitPerformed         : false",
        "SeleniumUsed                   : false",
        "WebDriverUsed                  : false",
        "BrowserDomAutomation           : false",
        "RandomPageClick                : false",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path
