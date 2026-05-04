from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from pywinauto import keyboard  # type: ignore

from patchops.edge_rpa.edge_upload_safe_report_copy_gate import (
    REQUESTED_CHAT_URL,
    _candidate_from_control,
    _canonical_url,
    _click_control,
    _edge_window,
    _ensure_target_loaded,
    _find_file_dialog,
    _find_plus_control,
    _get_clipboard_text,
    _hash_text,
    _info_text,
    _is_onedrive_path,
    _make_upload_safe_copy,
    _redact_path,
    _select_source_report,
    _set_file_picker_path,
    _verify_direct_composer_focus,
)
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_12f_soft_composer_edge_scoped_upload_menu_repair"
_EDGE_UPLOAD_LABELS = (
    "upload files", "upload file", "upload from computer", "add photos and files", "add photos & files",
    "attach files", "browse files", "browse", "from computer", "local file", "file upload"
)
_EDGE_REJECT_WORDS = (
    "onedrive", "uploading", "kb/s", "remaining", "sync", "tray", "notification", "status", "composer-plus-btn", "add files and more"
)


@dataclass(frozen=True)
class SoftComposerEdgeUploadResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    target_url_is_requested_chat: bool = False
    current_url_matches_target: bool = False
    navigation_skipped_existing_target: bool = False
    navigation_attempted: bool = False
    target_page_ready: bool = False
    composer_candidate_found: bool = False
    composer_focus_verified: bool = False
    composer_focus_soft_failure_allowed: bool = False
    source_report_found: bool = False
    source_report_hash: str = ""
    source_report_size_bytes: int = 0
    source_report_is_text: bool = False
    upload_safe_copy_created: bool = False
    upload_safe_copy_name: str = ""
    upload_safe_copy_hash: str = ""
    upload_safe_copy_size_bytes: int = 0
    upload_safe_copy_closed: bool = False
    safe_copy_outside_onedrive: bool = False
    allow_report_upload_requested: bool = False
    plus_button_found: bool = False
    plus_button_clicked: bool = False
    edge_scoped_menu_search_used: bool = False
    upload_menu_item_found: bool = False
    upload_menu_item_clicked: bool = False
    upload_menu_candidate_name_redacted: str = ""
    upload_menu_candidate_control_type: str = ""
    rejected_desktop_status_controls: bool = False
    file_picker_opened: bool = False
    file_picker_path_entered: bool = False
    file_picker_confirmed: bool = False
    upload_staging_observed: bool = False
    staged_file_name_hash: str = ""
    staging_observation_method: str = ""
    report_upload_attempted: bool = False
    file_attach_attempted: bool = False
    live_report_path: str = ""
    json_path: str = ""
    chatgpt_enter_key_sent: bool = False
    send_submit_performed: bool = False
    chatgpt_prompt_submitted: bool = False
    download_click_performed: bool = False
    run_package_invoked: bool = False
    pasteback_or_send_performed: bool = False
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    prompt_text_logged: bool = False
    file_content_logged: bool = False
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_dom_automation_used: bool = False
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def _score_edge_upload_candidate(control_type: str, raw_name: str, automation_id: str, class_name: str) -> int:
    blob = " ".join([control_type, raw_name, automation_id, class_name]).lower()
    if any(word in blob for word in _EDGE_REJECT_WORDS):
        return 0
    score = 0
    if control_type in {"Button", "MenuItem", "ListItem"}:
        score += 35
    elif control_type in {"Text", "Custom", "Hyperlink"}:
        score += 10
    for label in _EDGE_UPLOAD_LABELS:
        if label in blob:
            score += 120
    if "upload" in blob and ("file" in blob or "photo" in blob or "computer" in blob):
        score += 90
    if "attach" in blob and "file" in blob:
        score += 80
    return score


def _find_edge_scoped_upload_item(timeout_seconds: float = 12.0, max_controls: int = 2800) -> tuple[object, str, str, bool]:
    import pywinauto  # type: ignore
    deadline = time.time() + timeout_seconds
    rejected_status = False
    while time.time() < deadline:
        desktop = pywinauto.Desktop(backend="uia")
        edge_pids = edge_process_ids()
        _windows, wrappers = discover_edge_windows(desktop, edge_pids)
        best: tuple[int, object, str, str] | None = None
        for window in wrappers or []:
            try:
                queue = [(window, 0)]
            except Exception:
                queue = []
            scanned = 0
            while queue and scanned < max_controls:
                control, depth = queue.pop(0)
                scanned += 1
                try:
                    info = control.element_info
                    control_type = _info_text(info, "control_type")
                    raw_name = _info_text(info, "name")
                    automation_id = _info_text(info, "automation_id")
                    class_name = _info_text(info, "class_name")
                except Exception:
                    control_type = raw_name = automation_id = class_name = ""
                blob = " ".join([control_type, raw_name, automation_id, class_name]).lower()
                rejected_status = rejected_status or any(word in blob for word in _EDGE_REJECT_WORDS)
                score = _score_edge_upload_candidate(control_type, raw_name, automation_id, class_name)
                if score >= 100:
                    name_redacted = _hash_text(raw_name) if raw_name else ""
                    # Keep only hash/length-ish redaction in JSON; no raw menu text.
                    safe_label = f"hash:{name_redacted};len:{len(raw_name)}"
                    if best is None or score > best[0]:
                        best = (score, control, safe_label, control_type)
                if depth < 10:
                    try:
                        for child in list(control.children())[:120]:
                            queue.append((child, depth + 1))
                    except Exception:
                        pass
        if best is not None:
            return best[1], best[2], best[3], rejected_status
        time.sleep(0.25)
    raise RuntimeError("No Edge-scoped ChatGPT upload files menu item was found after plus click.")


def _write_report(path: Path, result: SoftComposerEdgeUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.12F soft-composer Edge-scoped upload menu repair",
        f"current_url_matches_target: {result.current_url_matches_target}",
        f"navigation_skipped_existing_target: {result.navigation_skipped_existing_target}",
        f"composer_candidate_found: {result.composer_candidate_found}",
        f"composer_focus_verified: {result.composer_focus_verified}",
        f"composer_focus_soft_failure_allowed: {result.composer_focus_soft_failure_allowed}",
        f"upload_safe_copy_created: {result.upload_safe_copy_created}",
        f"upload_safe_copy_closed: {result.upload_safe_copy_closed}",
        f"safe_copy_outside_onedrive: {result.safe_copy_outside_onedrive}",
        f"edge_scoped_menu_search_used: {result.edge_scoped_menu_search_used}",
        f"upload_menu_item_clicked: {result.upload_menu_item_clicked}",
        f"file_picker_opened: {result.file_picker_opened}",
        f"upload_staging_observed: {result.upload_staging_observed}",
        "chatgpt_enter_key_sent:false",
        "send_submit_performed:false",
        "chatgpt_prompt_submitted:false",
        "conversation_text_logged:false",
        "prompt_text_logged:false",
        "file_content_logged:false",
        f"failure_layer: {result.failure_layer}",
        f"error: {result.error}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: SoftComposerEdgeUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_12f_soft_composer_edge_upload_gate(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 10.0, allow_report_upload: bool = False) -> SoftComposerEdgeUploadResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_12f_soft_composer_edge_upload_result.json"
    report_path = out_dir / "normal_edge_l26_12f_soft_composer_edge_upload_report.txt"
    target_ok = _canonical_url(target_url) == _canonical_url(REQUESTED_CHAT_URL)
    state: dict[str, object] = {
        "target_url_is_requested_chat": target_ok,
        "allow_report_upload_requested": allow_report_upload,
        "live_report_path": str(report_path),
        "json_path": str(json_path),
    }
    try:
        if not allow_report_upload:
            raise RuntimeError("L26.12F requires explicit --allow-report-upload.")
        current_observed, page_ready, skipped_nav, attempted_nav, current_url = _ensure_target_loaded(out_dir, target_url, start_if_missing, settle_seconds)
        state.update({
            "current_url_matches_target": _canonical_url(current_url) == _canonical_url(target_url),
            "navigation_skipped_existing_target": skipped_nav,
            "navigation_attempted": attempted_nav,
            "target_page_ready": page_ready,
        })
        if not (target_ok and page_ready):
            raise RuntimeError("Target chat page is not ready.")

        source = _select_source_report()
        safe_copy = _make_upload_safe_copy(source, out_dir)
        source_hash = _hash_file(source)
        copy_hash = _hash_file(safe_copy)
        source_size = source.stat().st_size
        copy_size = safe_copy.stat().st_size
        state.update({
            "source_report_found": True,
            "source_report_hash": source_hash,
            "source_report_size_bytes": int(source_size),
            "source_report_is_text": source.suffix.lower() == ".txt",
            "upload_safe_copy_created": True,
            "upload_safe_copy_name": safe_copy.name,
            "upload_safe_copy_hash": copy_hash,
            "upload_safe_copy_size_bytes": int(copy_size),
            "upload_safe_copy_closed": True,
            "safe_copy_outside_onedrive": not _is_onedrive_path(safe_copy),
        })
        if source_hash != copy_hash or source_size != copy_size:
            raise RuntimeError("Upload-safe copy hash/size mismatch.")

        composer_found, focus_verified = _verify_direct_composer_focus()
        state.update({
            "composer_candidate_found": composer_found,
            "composer_focus_verified": focus_verified,
            "composer_focus_soft_failure_allowed": bool(composer_found and not focus_verified),
        })
        if not composer_found:
            raise RuntimeError("No composer candidate found; cannot safely continue to upload controls.")

        plus, plus_control = _find_plus_control()
        state.update({"plus_button_found": True})
        _click_control(plus_control)
        state.update({"plus_button_clicked": True, "edge_scoped_menu_search_used": True})
        time.sleep(0.8)
        upload_control, label_redacted, control_type, rejected_status = _find_edge_scoped_upload_item()
        state.update({
            "upload_menu_item_found": True,
            "upload_menu_candidate_name_redacted": label_redacted,
            "upload_menu_candidate_control_type": control_type,
            "rejected_desktop_status_controls": rejected_status,
        })
        _click_control(upload_control)
        state.update({"upload_menu_item_clicked": True, "report_upload_attempted": True, "file_attach_attempted": True})
        time.sleep(0.8)
        dialog = _find_file_dialog()
        state.update({"file_picker_opened": True})
        _set_file_picker_path(dialog, safe_copy)
        state.update({"file_picker_path_entered": True, "file_picker_confirmed": True})
        staged, method = _observe_staged_file(safe_copy.name)
        state.update({
            "upload_staging_observed": staged,
            "staged_file_name_hash": _hash_text(safe_copy.name),
            "staging_observation_method": method,
            "result": "PASS" if staged else "FAIL",
            "failure_layer": "" if staged else "edge_scoped_upload_staging_observation",
            "error": "" if staged else "Upload-safe copy was selected but staged attachment was not observed.",
        })
    except Exception as exc:
        state.update({
            "result": "FAIL",
            "failure_layer": "soft_composer_edge_scoped_upload_menu_repair",
            "error": f"{type(exc).__name__}: {exc}",
        })
    result = SoftComposerEdgeUploadResult(**state)
    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_12f_acceptance(result: SoftComposerEdgeUploadResult) -> None:
    payload = result.to_payload()
    required_true = [
        "target_url_is_requested_chat",
        "current_url_matches_target",
        "navigation_skipped_existing_target",
        "target_page_ready",
        "composer_candidate_found",
        "source_report_found",
        "source_report_is_text",
        "upload_safe_copy_created",
        "upload_safe_copy_closed",
        "safe_copy_outside_onedrive",
        "allow_report_upload_requested",
        "plus_button_found",
        "plus_button_clicked",
        "edge_scoped_menu_search_used",
        "upload_menu_item_found",
        "upload_menu_item_clicked",
        "file_picker_opened",
        "file_picker_path_entered",
        "file_picker_confirmed",
        "upload_staging_observed",
        "report_upload_attempted",
        "file_attach_attempted",
    ]
    required_false = [
        "navigation_attempted",
        "chatgpt_enter_key_sent",
        "send_submit_performed",
        "chatgpt_prompt_submitted",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
        "full_conversation_text_logged",
        "prompt_text_logged",
        "file_content_logged",
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    for key in ("source_report_hash", "upload_safe_copy_hash", "staged_file_name_hash"):
        if not payload.get(key):
            missing_true.append(key + "_nonempty")
    if payload.get("source_report_size_bytes", 0) <= 0 or payload.get("upload_safe_copy_size_bytes", 0) <= 0:
        missing_true.append("report_sizes>0")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.12F acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
