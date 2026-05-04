from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.edge_rpa.edge_requested_chat_false_challenge_filter import run_l26_10c_false_challenge_filter_gate
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids
from patchops.edge_rpa.edge_uia_tree_report import safe_text

PATCH_NAME = "l26_11_report_upload_dry_run_gate"
REQUESTED_CHAT_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"
_ATTACH_WORDS = ("add files", "attach", "upload", "paperclip", "composer-plus", "add photos", "add file")
_CHROME_WORDS = ("omnibox", "address and search bar", "search or enter web address", "tab strip", "toolbar")


@dataclass(frozen=True)
class AttachCandidate:
    candidate_kind: str = ""
    control_type: str = ""
    class_name_redacted: str = ""
    name_redacted: str = ""
    automation_id_redacted: str = ""
    is_in_page_scope: bool = False
    is_browser_chrome: bool = False
    score: int = 0
    depth: int = 0
    rectangle: str = ""


@dataclass(frozen=True)
class ReportUploadDryRunResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    target_url_is_requested_chat: bool = False
    requested_chat_accessible_by_composer: bool = False
    composer_focus_verified: bool = False
    report_discovery_completed: bool = False
    report_candidate_found: bool = False
    report_candidate_path_redacted: str = ""
    report_candidate_name: str = ""
    report_candidate_hash: str = ""
    report_candidate_size_bytes: int = 0
    report_candidate_is_text: bool = False
    attach_discovery_completed: bool = False
    attach_candidate_found: bool = False
    attach_candidate_kind: str = ""
    attach_candidate_automation_id_redacted: str = ""
    attach_candidate_name_redacted: str = ""
    attach_candidate_is_in_page_scope: bool = False
    attach_candidate: AttachCandidate | None = None
    allow_report_upload_requested: bool = False
    report_upload_attempted: bool = False
    file_attach_attempted: bool = False
    attach_button_clicked: bool = False
    file_picker_opened: bool = False
    live_report_path: str = ""
    json_path: str = ""
    precondition_json_path: str = ""
    enter_key_sent: bool = False
    send_submit_performed: bool = False
    chatgpt_prompt_submitted: bool = False
    page_click_performed: bool = False
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
        payload = asdict(self)
        if self.attach_candidate is not None:
            payload["attach_candidate"] = asdict(self.attach_candidate)
        return payload


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def _hash_text(value: object) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def _redact_path(path: Path) -> str:
    parts = list(path.parts)
    if len(parts) >= 2:
        return str(Path("...") / parts[-2] / parts[-1])
    return path.name


def _desktop_dirs() -> list[Path]:
    home = Path.home()
    dirs = [home / "Desktop", home / "OneDrive - OTE" / "Desktop", home / "OneDrive" / "Desktop"]
    seen: list[Path] = []
    for item in dirs:
        if item.exists() and item not in seen:
            seen.append(item)
    return seen


def find_latest_patchops_report() -> Path:
    candidates: list[Path] = []
    patterns = ("l26_*.txt", "patchops_*.txt", "*requested_chat*.txt")
    for root in _desktop_dirs():
        for pattern in patterns:
            candidates.extend(path for path in root.glob(pattern) if path.is_file())
    if not candidates:
        raise RuntimeError("No Desktop PatchOps report candidate was found.")
    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[0]


def _info_text(info: object, name: str) -> str:
    try:
        value = getattr(info, name)
        return "" if value is None else str(value)
    except Exception:
        return ""


def _rect_text(control: object) -> str:
    try:
        rect = control.rectangle()
        return f"L{rect.left} T{rect.top} R{rect.right} B{rect.bottom}"
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
        score += 150
    if any(word in text for word in _ATTACH_WORDS):
        kind = "attach_upload_candidate"
        score += 90
    if control_type == "Button":
        score += 20
    if kind == "none" or score < 80:
        return "none", 0
    return kind, score


def discover_attach_candidate(*, max_depth: int = 16, max_controls: int = 1400) -> AttachCandidate:
    import pywinauto  # type: ignore
    edge_pids = edge_process_ids()
    desktop = pywinauto.Desktop(backend="uia")
    _windows, wrappers = discover_edge_windows(desktop, edge_pids)
    if not wrappers:
        raise RuntimeError("No normal Edge window wrapper was found.")
    window = wrappers[0]
    window.set_focus()
    queue: list[tuple[object, int, bool]] = [(window, 0, False)]
    found: list[AttachCandidate] = []
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
            found.append(AttachCandidate(
                candidate_kind=kind,
                control_type=control_type,
                class_name_redacted=class_redacted,
                name_redacted=name_redacted,
                automation_id_redacted=auto_redacted,
                is_in_page_scope=page_scope,
                is_browser_chrome=chrome,
                score=score,
                depth=depth,
                rectangle=_rect_text(control),
            ))
        if depth >= max_depth:
            continue
        try:
            children = list(control.children())
        except Exception:
            children = []
        for child in children[: max(0, max_controls - scanned)]:
            queue.append((child, depth + 1, page_scope))
    if not found:
        raise RuntimeError("No attach/upload candidate was found in requested chat.")
    found.sort(key=lambda item: -item.score)
    return found[0]


def _write_report(path: Path, result: ReportUploadDryRunResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.11 report upload dry-run gate",
        "report_upload_attempted:false",
        "file_attach_attempted:false",
        "attach_button_clicked:false",
        "file_picker_opened:false",
        "enter_key_sent:false",
        "send_submit_performed:false",
        "chatgpt_prompt_submitted:false",
        "page_click_performed:false",
        "download_click_performed:false",
        "run_package_invoked:false",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "prompt_text_logged:false",
        "No file path beyond redacted basename/parent is logged.",
        "",
        f"target_url_is_requested_chat: {result.target_url_is_requested_chat}",
        f"requested_chat_accessible_by_composer: {result.requested_chat_accessible_by_composer}",
        f"composer_focus_verified: {result.composer_focus_verified}",
        f"report_candidate_found: {result.report_candidate_found}",
        f"report_candidate_path_redacted: {result.report_candidate_path_redacted}",
        f"report_candidate_name: {result.report_candidate_name}",
        f"report_candidate_hash: {result.report_candidate_hash}",
        f"report_candidate_size_bytes: {result.report_candidate_size_bytes}",
        f"attach_candidate_found: {result.attach_candidate_found}",
        f"attach_candidate_kind: {result.attach_candidate_kind}",
        f"attach_candidate_automation_id_redacted: {result.attach_candidate_automation_id_redacted}",
        f"attach_candidate_name_redacted: {result.attach_candidate_name_redacted}",
        f"allow_report_upload_requested: {result.allow_report_upload_requested}",
        f"failure_layer: {result.failure_layer}",
        f"error: {result.error}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: ReportUploadDryRunResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_11_report_upload_dry_run_gate(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 10.0, allow_report_upload: bool = False) -> ReportUploadDryRunResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_11_report_upload_dry_run_result.json"
    report_path = out_dir / "normal_edge_l26_11_report_upload_dry_run_report.txt"
    precondition_dir = out_dir / "requested_chat_false_challenge_filter"
    precondition_json = precondition_dir / "normal_edge_l26_10c_false_challenge_filter_result.json"
    target_ok = target_url.rstrip("/") == REQUESTED_CHAT_URL.rstrip("/")
    try:
        if allow_report_upload:
            raise RuntimeError("L26.11 is dry-run only. Do not pass --allow-report-upload until a later explicit upload patch.")
        precondition = run_l26_10c_false_challenge_filter_gate(output_dir=precondition_dir, target_url=target_url, start_if_missing=start_if_missing, settle_seconds=settle_seconds, allow_send=False)
        pre = precondition.to_payload()
        accessible = bool(pre.get("result") == "PASS" and pre.get("requested_chat_accessible_by_composer") and pre.get("composer_focus_verified"))
        if not (target_ok and accessible):
            raise RuntimeError("Requested chat/composer precondition did not pass.")
        report_file = find_latest_patchops_report()
        stat = report_file.stat()
        report_hash = _hash_file(report_file)
        report_is_text = report_file.suffix.lower() == ".txt"
        attach = discover_attach_candidate()
        result_pass = bool(report_file.exists() and report_is_text and stat.st_size > 0 and attach.is_in_page_scope and not attach.is_browser_chrome)
        result = ReportUploadDryRunResult(
            target_url_is_requested_chat=target_ok,
            requested_chat_accessible_by_composer=accessible,
            composer_focus_verified=bool(pre.get("composer_focus_verified")),
            report_discovery_completed=True,
            report_candidate_found=True,
            report_candidate_path_redacted=_redact_path(report_file),
            report_candidate_name=report_file.name,
            report_candidate_hash=report_hash,
            report_candidate_size_bytes=int(stat.st_size),
            report_candidate_is_text=report_is_text,
            attach_discovery_completed=True,
            attach_candidate_found=True,
            attach_candidate_kind=attach.candidate_kind,
            attach_candidate_automation_id_redacted=attach.automation_id_redacted,
            attach_candidate_name_redacted=attach.name_redacted,
            attach_candidate_is_in_page_scope=attach.is_in_page_scope,
            attach_candidate=attach,
            allow_report_upload_requested=False,
            report_upload_attempted=False,
            file_attach_attempted=False,
            attach_button_clicked=False,
            file_picker_opened=False,
            live_report_path=str(report_path),
            json_path=str(json_path),
            precondition_json_path=str(precondition_json),
            result="PASS" if result_pass else "FAIL",
            failure_layer="" if result_pass else "report_upload_dry_run_gate",
            error="" if result_pass else "Report candidate or attach candidate did not satisfy dry-run requirements.",
        )
    except Exception as exc:
        result = ReportUploadDryRunResult(
            target_url_is_requested_chat=target_ok,
            allow_report_upload_requested=allow_report_upload,
            live_report_path=str(report_path),
            json_path=str(json_path),
            precondition_json_path=str(precondition_json),
            result="FAIL",
            failure_layer="report_upload_dry_run_gate",
            error=f"{type(exc).__name__}: {exc}",
        )
    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_11_acceptance(result: ReportUploadDryRunResult) -> None:
    payload = result.to_payload()
    required_true = [
        "target_url_is_requested_chat",
        "requested_chat_accessible_by_composer",
        "composer_focus_verified",
        "report_discovery_completed",
        "report_candidate_found",
        "report_candidate_is_text",
        "attach_discovery_completed",
        "attach_candidate_found",
        "attach_candidate_is_in_page_scope",
    ]
    required_false = [
        "allow_report_upload_requested",
        "report_upload_attempted",
        "file_attach_attempted",
        "attach_button_clicked",
        "file_picker_opened",
        "enter_key_sent",
        "send_submit_performed",
        "chatgpt_prompt_submitted",
        "page_click_performed",
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
    if not payload.get("attach_candidate_automation_id_redacted") and not payload.get("attach_candidate_name_redacted"):
        missing_true.append("attach_candidate_identity")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.11 acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
