from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from pywinauto import keyboard  # type: ignore

from patchops.edge_rpa.edge_soft_composer_edge_upload_gate import (
    REQUESTED_CHAT_URL,
    SoftComposerEdgeUploadResult,
    _hash_file,
    _score_edge_upload_candidate,
)
from patchops.edge_rpa.edge_upload_safe_report_copy_gate import (
    _canonical_url,
    _click_control,
    _ensure_target_loaded,
    _find_file_dialog,
    _find_plus_control,
    _get_clipboard_text,
    _hash_text,
    _info_text,
    _is_onedrive_path,
    _make_upload_safe_copy,
    _select_source_report,
    _set_file_picker_path,
    _verify_direct_composer_focus,
    _observe_staged_file,
)
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_12g_upload_menu_candidate_retry_fingerprint_repair"


@dataclass(frozen=True)
class MenuCandidateFingerprint:
    fingerprint: str
    control_type: str
    score: int
    name_length: int
    automation_id_length: int
    class_name_length: int
    depth: int

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class UploadMenuCandidateRetryResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    target_url_is_requested_chat: bool = False
    current_url_matches_target: bool = False
    navigation_skipped_existing_target: bool = False
    navigation_attempted: bool = False
    target_page_ready: bool = False
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
    composer_candidate_found: bool = False
    composer_focus_verified: bool = False
    allow_report_upload_requested: bool = False
    plus_button_found: bool = False
    plus_button_clicked: bool = False
    edge_scoped_candidate_retry_used: bool = False
    candidate_count: int = 0
    candidate_attempt_count: int = 0
    candidate_fingerprints: list[dict[str, object]] = field(default_factory=list)
    failed_candidate_fingerprints: list[str] = field(default_factory=list)
    successful_candidate_fingerprint: str = ""
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


def _fingerprint(control_type: str, name: str, automation_id: str, class_name: str, score: int, depth: int) -> MenuCandidateFingerprint:
    raw = "|".join([control_type, name, automation_id, class_name])
    return MenuCandidateFingerprint(
        fingerprint=_hash_text(raw),
        control_type=control_type,
        score=score,
        name_length=len(name or ""),
        automation_id_length=len(automation_id or ""),
        class_name_length=len(class_name or ""),
        depth=depth,
    )


def _collect_edge_scoped_upload_candidates(max_controls: int = 3200, max_candidates: int = 8) -> list[tuple[MenuCandidateFingerprint, object]]:
    import pywinauto  # type: ignore
    desktop = pywinauto.Desktop(backend="uia")
    edge_pids = edge_process_ids()
    _windows, wrappers = discover_edge_windows(desktop, edge_pids)
    candidates: list[tuple[MenuCandidateFingerprint, object]] = []
    seen: set[str] = set()
    for window in wrappers or []:
        queue: list[tuple[object, int]] = [(window, 0)]
        scanned = 0
        while queue and scanned < max_controls:
            control, depth = queue.pop(0)
            scanned += 1
            try:
                info = control.element_info
                control_type = _info_text(info, "control_type")
                name = _info_text(info, "name")
                automation_id = _info_text(info, "automation_id")
                class_name = _info_text(info, "class_name")
            except Exception:
                control_type = name = automation_id = class_name = ""
            score = _score_edge_upload_candidate(control_type, name, automation_id, class_name)
            if score >= 70 and control_type in {"Button", "MenuItem", "ListItem", "Custom", "Text", "Hyperlink"}:
                fp = _fingerprint(control_type, name, automation_id, class_name, score, depth)
                if fp.fingerprint not in seen:
                    candidates.append((fp, control))
                    seen.add(fp.fingerprint)
            if depth < 10:
                try:
                    for child in list(control.children())[:120]:
                        queue.append((child, depth + 1))
                except Exception:
                    pass
    candidates.sort(key=lambda item: (-item[0].score, item[0].depth, item[0].name_length))
    return candidates[:max_candidates]


def _open_plus_menu() -> None:
    try:
        keyboard.send_keys("{ESC}")
        time.sleep(0.15)
    except Exception:
        pass
    plus, plus_control = _find_plus_control()
    _click_control(plus_control)
    time.sleep(0.8)


def _try_candidate_open_file_picker(control: object, timeout_seconds: float = 3.5) -> object | None:
    try:
        control.set_focus()
    except Exception:
        pass
    try:
        control.click_input()
    except Exception:
        try:
            control.invoke()
        except Exception:
            return None
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            return _find_file_dialog(timeout_seconds=0.4)
        except Exception:
            time.sleep(0.2)
    return None


def _write_report(path: Path, result: UploadMenuCandidateRetryResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.12G upload-menu candidate retry fingerprint repair",
        f"current_url_matches_target: {result.current_url_matches_target}",
        f"navigation_skipped_existing_target: {result.navigation_skipped_existing_target}",
        f"upload_safe_copy_created: {result.upload_safe_copy_created}",
        f"plus_button_clicked: {result.plus_button_clicked}",
        f"edge_scoped_candidate_retry_used: {result.edge_scoped_candidate_retry_used}",
        f"candidate_count: {result.candidate_count}",
        f"candidate_attempt_count: {result.candidate_attempt_count}",
        f"successful_candidate_fingerprint: {result.successful_candidate_fingerprint}",
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


def _write_json(path: Path, result: UploadMenuCandidateRetryResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_12g_upload_menu_candidate_retry_gate(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 10.0, allow_report_upload: bool = False) -> UploadMenuCandidateRetryResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_12g_upload_menu_retry_result.json"
    report_path = out_dir / "normal_edge_l26_12g_upload_menu_retry_report.txt"
    target_ok = _canonical_url(target_url) == _canonical_url(REQUESTED_CHAT_URL)
    state: dict[str, object] = {
        "target_url_is_requested_chat": target_ok,
        "allow_report_upload_requested": allow_report_upload,
        "live_report_path": str(report_path),
        "json_path": str(json_path),
    }
    try:
        if not allow_report_upload:
            raise RuntimeError("L26.12G requires explicit --allow-report-upload.")
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
        state.update({"composer_candidate_found": composer_found, "composer_focus_verified": focus_verified})
        if not composer_found:
            raise RuntimeError("No composer candidate found; cannot safely locate upload controls.")

        plus, plus_control = _find_plus_control()
        state.update({"plus_button_found": True})
        _click_control(plus_control)
        time.sleep(0.8)
        state.update({"plus_button_clicked": True, "edge_scoped_candidate_retry_used": True})
        candidates = _collect_edge_scoped_upload_candidates()
        state.update({"candidate_count": len(candidates), "candidate_fingerprints": [fp.to_payload() for fp, _ in candidates]})
        if not candidates:
            raise RuntimeError("No Edge-scoped upload candidate fingerprints were collected after plus click.")
        failed: list[str] = []
        dialog = None
        successful_fp = ""
        for index, (fp, control) in enumerate(candidates, start=1):
            if index > 1:
                _open_plus_menu()
                time.sleep(0.3)
            dialog = _try_candidate_open_file_picker(control)
            state.update({"candidate_attempt_count": index})
            if dialog is not None:
                successful_fp = fp.fingerprint
                break
            failed.append(fp.fingerprint)
        state.update({"failed_candidate_fingerprints": failed, "successful_candidate_fingerprint": successful_fp})
        if dialog is None:
            raise RuntimeError(f"No tested Edge-scoped upload candidate opened the file picker; attempted={len(failed)}")
        state.update({"file_picker_opened": True, "report_upload_attempted": True, "file_attach_attempted": True})
        _set_file_picker_path(dialog, safe_copy)
        state.update({"file_picker_path_entered": True, "file_picker_confirmed": True})
        staged, method = _observe_staged_file(safe_copy.name)
        state.update({
            "upload_staging_observed": staged,
            "staged_file_name_hash": _hash_text(safe_copy.name),
            "staging_observation_method": method,
            "result": "PASS" if staged else "FAIL",
            "failure_layer": "" if staged else "upload_menu_candidate_retry_staging_observation",
            "error": "" if staged else "File picker opened and safe copy was selected, but staged attachment was not observed.",
        })
    except Exception as exc:
        state.update({
            "result": "FAIL",
            "failure_layer": "upload_menu_candidate_retry_fingerprint_repair",
            "error": f"{type(exc).__name__}: {exc}",
        })
    result = UploadMenuCandidateRetryResult(**state)
    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_12g_acceptance(result: UploadMenuCandidateRetryResult) -> None:
    payload = result.to_payload()
    required_true = [
        "target_url_is_requested_chat",
        "current_url_matches_target",
        "navigation_skipped_existing_target",
        "target_page_ready",
        "source_report_found",
        "source_report_is_text",
        "upload_safe_copy_created",
        "upload_safe_copy_closed",
        "safe_copy_outside_onedrive",
        "composer_candidate_found",
        "allow_report_upload_requested",
        "plus_button_found",
        "plus_button_clicked",
        "edge_scoped_candidate_retry_used",
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
    if payload.get("candidate_count", 0) <= 0:
        missing_true.append("candidate_count>0")
    if payload.get("candidate_attempt_count", 0) <= 0:
        missing_true.append("candidate_attempt_count>0")
    for key in ("source_report_hash", "upload_safe_copy_hash", "successful_candidate_fingerprint", "staged_file_name_hash"):
        if not payload.get(key):
            missing_true.append(key + "_nonempty")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.12G acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
