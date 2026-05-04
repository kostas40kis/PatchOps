from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pywinauto import keyboard  # type: ignore

from patchops.edge_rpa.edge_report_upload_dry_run_gate import AttachCandidate, find_latest_patchops_report, run_l26_11_report_upload_dry_run_gate
from patchops.edge_rpa.edge_uia_tree_report import safe_text
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_12_report_upload_staging_gate"
REQUESTED_CHAT_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"
_ATTACH_WORDS = ("add files", "attach", "upload", "paperclip", "composer-plus", "add photos", "add file")
_CHROME_WORDS = ("omnibox", "address and search bar", "search or enter web address", "tab strip", "toolbar")


@dataclass(frozen=True)
class ReportUploadStagingResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    target_url_is_requested_chat: bool = False
    requested_chat_accessible_by_composer: bool = False
    composer_focus_verified: bool = False
    allow_report_upload_requested: bool = False
    report_discovery_completed: bool = False
    report_candidate_found: bool = False
    report_candidate_path_redacted: str = ""
    report_candidate_name: str = ""
    report_candidate_hash: str = ""
    report_candidate_size_bytes: int = 0
    report_candidate_is_text: bool = False
    attach_candidate_found: bool = False
    attach_candidate_kind: str = ""
    attach_candidate_automation_id_redacted: str = ""
    attach_candidate_name_redacted: str = ""
    attach_candidate_is_in_page_scope: bool = False
    report_upload_attempted: bool = False
    file_attach_attempted: bool = False
    attach_button_clicked: bool = False
    file_picker_opened: bool = False
    file_picker_path_entered: bool = False
    file_picker_open_invoked: bool = False
    upload_staging_observed: bool = False
    staged_file_name_hash: str = ""
    staged_file_name_length: int = 0
    staging_observation_method: str = ""
    live_report_path: str = ""
    json_path: str = ""
    precondition_json_path: str = ""
    enter_key_sent: bool = False
    send_submit_performed: bool = False
    chatgpt_prompt_submitted: bool = False
    download_click_performed: bool = False
    run_package_invoked: bool = False
    pasteback_or_send_performed: bool = False
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    prompt_text_logged: bool = False
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_dom_automation_used: bool = False
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _hash_text(value: object) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def _redact_path(path: Path) -> str:
    parts = list(path.parts)
    if len(parts) >= 2:
        return str(Path("...") / parts[-2] / parts[-1])
    return path.name


def _info_text(info: object, name: str) -> str:
    try:
        value = getattr(info, name)
        return "" if value is None else str(value)
    except Exception:
        return ""


def _is_root_web_area(control_type: str, class_name: str, name: str, automation_id: str) -> bool:
    text = " ".join([control_type, class_name, name, automation_id]).lower()
    return automation_id == "RootWebArea" or "rootwebarea" in text or control_type == "Document"


def _is_browser_chrome(control_type: str, class_name: str, name: str, automation_id: str) -> bool:
    text = " ".join([control_type, class_name, name, automation_id]).lower()
    return any(word in text for word in _CHROME_WORDS)


def _score_attach(control_type: str, class_name: str, name: str, automation_id: str, page_scope: bool, chrome: bool) -> tuple[str, int]:
    if chrome or not page_scope:
        return "none", 0
    text = " ".join([control_type, class_name, name, automation_id]).lower()
    score = 0
    kind = "none"
    if automation_id == "composer-plus-btn":
        kind = "composer_plus_attach_candidate"
        score += 170
    if any(word in text for word in _ATTACH_WORDS):
        kind = "attach_upload_candidate"
        score += 100
    if control_type == "Button":
        score += 30
    if kind == "none" or score < 90:
        return "none", 0
    return kind, score


def _find_attach_control(max_depth: int = 16, max_controls: int = 1400) -> tuple[AttachCandidate, object]:
    import pywinauto  # type: ignore
    edge_pids = edge_process_ids()
    desktop = pywinauto.Desktop(backend="uia")
    _windows, wrappers = discover_edge_windows(desktop, edge_pids)
    if not wrappers:
        raise RuntimeError("No normal Edge window wrapper was found.")
    window = wrappers[0]
    window.set_focus()
    queue: list[tuple[object, int, bool]] = [(window, 0, False)]
    found: list[tuple[AttachCandidate, object]] = []
    scanned = 0
    while queue and scanned < max_controls:
        control, depth, inherited_page_scope = queue.pop(0)
        scanned += 1
        try:
            info = control.element_info
            control_type = _info_text(info, "control_type")
            class_name = _info_text(info, "class_name")
            raw_name = _info_text(info, "name")
            automation_id = _info_text(info, "automation_id")
        except Exception:
            control_type = class_name = raw_name = automation_id = ""
        page_scope = bool(inherited_page_scope or _is_root_web_area(control_type, class_name, raw_name, automation_id))
        chrome = _is_browser_chrome(control_type, class_name, raw_name, automation_id)
        kind, score = _score_attach(control_type, class_name, raw_name, automation_id, page_scope, chrome)
        if kind != "none":
            class_redacted, _, _ = safe_text(class_name, control_type="Button", max_chars=80)
            name_redacted, _, _ = safe_text(raw_name, control_type=control_type, max_chars=80)
            auto_redacted, _, _ = safe_text(automation_id, control_type="Button", max_chars=80)
            found.append((AttachCandidate(
                candidate_kind=kind,
                control_type=control_type,
                class_name_redacted=class_redacted,
                name_redacted=name_redacted,
                automation_id_redacted=auto_redacted,
                is_in_page_scope=page_scope,
                is_browser_chrome=chrome,
                score=score,
                depth=depth,
                rectangle="",
            ), control))
        if depth >= max_depth:
            continue
        try:
            children = list(control.children())
        except Exception:
            children = []
        for child in children[: max(0, max_controls - scanned)]:
            queue.append((child, depth + 1, page_scope))
    if not found:
        raise RuntimeError("No attach/upload control was found.")
    found.sort(key=lambda item: -item[0].score)
    return found[0]


def _find_file_dialog(timeout_seconds: float = 8.0) -> object:
    import pywinauto  # type: ignore
    desktop = pywinauto.Desktop(backend="uia")
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            for window in desktop.windows():
                try:
                    title = str(window.window_text() or "")
                    class_name = str(window.element_info.class_name or "")
                    if (title.lower() in {"open", "choose file to upload", "file upload"}) or ("#32770" in class_name and title):
                        return window
                except Exception:
                    continue
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError("File picker dialog was not observed after attach click.")


def _set_file_picker_path(dialog: object, file_path: Path) -> None:
    path_text = str(file_path)
    try:
        dialog.set_focus()
    except Exception:
        pass
    # The Windows file picker reliably accepts full-path paste into the filename box via Ctrl+L or the focused filename edit.
    keyboard.send_keys("%n")
    time.sleep(0.2)
    keyboard.send_keys(path_text, with_spaces=True, pause=0.001)
    time.sleep(0.2)
    keyboard.send_keys("{ENTER}")


def _observe_staged_file(file_name: str, timeout_seconds: float = 20.0) -> tuple[bool, str]:
    import pywinauto  # type: ignore
    desktop = pywinauto.Desktop(backend="uia")
    needle = file_name.lower()
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            edge_pids = edge_process_ids()
            _windows, wrappers = discover_edge_windows(desktop, edge_pids)
            wrappers = wrappers or []
            for window in wrappers:
                try:
                    queue = list(window.children())
                except Exception:
                    queue = []
                seen = 0
                while queue and seen < 1500:
                    control = queue.pop(0)
                    seen += 1
                    try:
                        info = control.element_info
                        name = _info_text(info, "name")
                        automation_id = _info_text(info, "automation_id")
                        class_name = _info_text(info, "class_name")
                    except Exception:
                        name = automation_id = class_name = ""
                    blob = " ".join([name, automation_id, class_name]).lower()
                    if needle and needle in blob:
                        return True, "uia_filename_match"
                    try:
                        queue.extend(list(control.children())[:80])
                    except Exception:
                        pass
        except Exception:
            pass
        time.sleep(0.5)
    return False, "not_observed"


def _write_report(path: Path, result: ReportUploadStagingResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.12 report upload staging gate",
        "report_upload_attempted:true" if result.report_upload_attempted else "report_upload_attempted:false",
        "file_attach_attempted:true" if result.file_attach_attempted else "file_attach_attempted:false",
        "attach_button_clicked:true" if result.attach_button_clicked else "attach_button_clicked:false",
        "file_picker_opened:true" if result.file_picker_opened else "file_picker_opened:false",
        "enter_key_sent:false",
        "send_submit_performed:false",
        "chatgpt_prompt_submitted:false",
        "download_click_performed:false",
        "run_package_invoked:false",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "prompt_text_logged:false",
        "No full file path, prompt, or conversation text is logged.",
        "",
        f"target_url_is_requested_chat: {result.target_url_is_requested_chat}",
        f"requested_chat_accessible_by_composer: {result.requested_chat_accessible_by_composer}",
        f"report_candidate_path_redacted: {result.report_candidate_path_redacted}",
        f"report_candidate_name: {result.report_candidate_name}",
        f"report_candidate_hash: {result.report_candidate_hash}",
        f"report_candidate_size_bytes: {result.report_candidate_size_bytes}",
        f"attach_candidate_found: {result.attach_candidate_found}",
        f"attach_candidate_automation_id_redacted: {result.attach_candidate_automation_id_redacted}",
        f"upload_staging_observed: {result.upload_staging_observed}",
        f"staged_file_name_hash: {result.staged_file_name_hash}",
        f"staged_file_name_length: {result.staged_file_name_length}",
        f"staging_observation_method: {result.staging_observation_method}",
        f"failure_layer: {result.failure_layer}",
        f"error: {result.error}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: ReportUploadStagingResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_12_report_upload_staging_gate(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 10.0, allow_report_upload: bool = False) -> ReportUploadStagingResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_12_report_upload_staging_result.json"
    report_path = out_dir / "normal_edge_l26_12_report_upload_staging_report.txt"
    precondition_dir = out_dir / "report_upload_dry_run"
    precondition_json = precondition_dir / "normal_edge_l26_11_report_upload_dry_run_result.json"
    target_ok = target_url.rstrip("/") == REQUESTED_CHAT_URL.rstrip("/")
    try:
        if not allow_report_upload:
            raise RuntimeError("L26.12 requires explicit --allow-report-upload to attach the report file.")
        precondition = run_l26_11_report_upload_dry_run_gate(output_dir=precondition_dir, target_url=target_url, start_if_missing=start_if_missing, settle_seconds=settle_seconds, allow_report_upload=False)
        pre = precondition.to_payload()
        accessible = bool(pre.get("result") == "PASS" and pre.get("requested_chat_accessible_by_composer") and pre.get("composer_focus_verified"))
        if not (target_ok and accessible):
            raise RuntimeError("Requested chat/report-upload dry-run precondition did not pass.")
        report_file = find_latest_patchops_report()
        stat = report_file.stat()
        report_hash = _hash_file(report_file)
        report_is_text = report_file.suffix.lower() == ".txt"
        if not report_is_text or stat.st_size <= 0:
            raise RuntimeError("Latest report candidate is not a non-empty txt file.")
        attach, attach_control = _find_attach_control()
        if not attach.is_in_page_scope or attach.is_browser_chrome:
            raise RuntimeError("Attach control is not a safe in-page candidate.")
        attach_control.click_input()
        time.sleep(0.8)
        dialog = _find_file_dialog()
        _set_file_picker_path(dialog, report_file)
        staged, method = _observe_staged_file(report_file.name)
        result = ReportUploadStagingResult(
            target_url_is_requested_chat=target_ok,
            requested_chat_accessible_by_composer=accessible,
            composer_focus_verified=bool(pre.get("composer_focus_verified")),
            allow_report_upload_requested=True,
            report_discovery_completed=True,
            report_candidate_found=True,
            report_candidate_path_redacted=_redact_path(report_file),
            report_candidate_name=report_file.name,
            report_candidate_hash=report_hash,
            report_candidate_size_bytes=int(stat.st_size),
            report_candidate_is_text=report_is_text,
            attach_candidate_found=True,
            attach_candidate_kind=attach.candidate_kind,
            attach_candidate_automation_id_redacted=attach.automation_id_redacted,
            attach_candidate_name_redacted=attach.name_redacted,
            attach_candidate_is_in_page_scope=attach.is_in_page_scope,
            report_upload_attempted=True,
            file_attach_attempted=True,
            attach_button_clicked=True,
            file_picker_opened=True,
            file_picker_path_entered=True,
            file_picker_open_invoked=True,
            upload_staging_observed=staged,
            staged_file_name_hash=_hash_text(report_file.name),
            staged_file_name_length=len(report_file.name),
            staging_observation_method=method,
            live_report_path=str(report_path),
            json_path=str(json_path),
            precondition_json_path=str(precondition_json),
            result="PASS" if staged else "FAIL",
            failure_layer="" if staged else "report_upload_staging_observation",
            error="" if staged else "File was selected but staged upload was not observed in ChatGPT UIA tree.",
        )
    except Exception as exc:
        result = ReportUploadStagingResult(
            target_url_is_requested_chat=target_ok,
            allow_report_upload_requested=allow_report_upload,
            live_report_path=str(report_path),
            json_path=str(json_path),
            precondition_json_path=str(precondition_json),
            result="FAIL",
            failure_layer="report_upload_staging_gate",
            error=f"{type(exc).__name__}: {exc}",
        )
    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_12_acceptance(result: ReportUploadStagingResult) -> None:
    payload = result.to_payload()
    required_true = [
        "target_url_is_requested_chat",
        "requested_chat_accessible_by_composer",
        "composer_focus_verified",
        "allow_report_upload_requested",
        "report_discovery_completed",
        "report_candidate_found",
        "report_candidate_is_text",
        "attach_candidate_found",
        "attach_candidate_is_in_page_scope",
        "report_upload_attempted",
        "file_attach_attempted",
        "attach_button_clicked",
        "file_picker_opened",
        "file_picker_path_entered",
        "file_picker_open_invoked",
        "upload_staging_observed",
    ]
    required_false = [
        "enter_key_sent",
        "send_submit_performed",
        "chatgpt_prompt_submitted",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
        "full_conversation_text_logged",
        "prompt_text_logged",
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if payload.get("report_candidate_size_bytes", 0) <= 0:
        missing_true.append("report_candidate_size_bytes>0")
    if not payload.get("report_candidate_hash"):
        missing_true.append("report_candidate_hash_nonempty")
    if not payload.get("staged_file_name_hash"):
        missing_true.append("staged_file_name_hash_nonempty")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.12 acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
