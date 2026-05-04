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

from patchops.edge_rpa.edge_current_url_upload_menu_repair import (
    REQUESTED_CHAT_URL,
    UploadControlCandidate,
    _canonical_url,
    _click_control,
    _edge_window,
    _ensure_target_loaded,
    _find_file_dialog,
    _find_plus_control,
    _get_clipboard_text,
    _hash_text,
    _info_text,
    _redact_path,
    _set_clipboard_text,
    _set_file_picker_path,
    _snapshot_menu_inventory,
    _verify_direct_composer_focus,
    _candidate_from_control,
    _observe_staged_file,
)

PATCH_NAME = "l26_12e_upload_safe_report_copy_strict_menu_repair"
_STATUS_REJECT_WORDS = (
    "onedrive", "uploading", "kb/s", "remaining", "sync", "syncing", "status", "tray", "notification",
    "microsoft teams", "windows security", "battery", "network", "volume"
)
_UPLOAD_LABEL_HINTS = (
    "upload files", "upload file", "upload from computer", "add photos and files", "add photos & files",
    "attach files", "browse", "from computer", "local file", "file upload"
)


@dataclass(frozen=True)
class UploadSafeCopyResult:
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
    source_report_found: bool = False
    source_report_path_redacted: str = ""
    source_report_name: str = ""
    source_report_hash: str = ""
    source_report_size_bytes: int = 0
    source_report_is_text: bool = False
    upload_safe_copy_created: bool = False
    upload_safe_copy_path_redacted: str = ""
    upload_safe_copy_name: str = ""
    upload_safe_copy_hash: str = ""
    upload_safe_copy_size_bytes: int = 0
    upload_safe_copy_closed: bool = False
    safe_copy_outside_onedrive: bool = False
    allow_report_upload_requested: bool = False
    plus_button_found: bool = False
    plus_button_clicked: bool = False
    upload_menu_item_found: bool = False
    upload_menu_item_clicked: bool = False
    upload_menu_candidate_name_redacted: str = ""
    upload_menu_candidate_control_type: str = ""
    onedrive_status_candidate_rejected: bool = False
    upload_menu_inventory_written: bool = False
    upload_menu_inventory_count: int = 0
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
    menu_inventory_path: str = ""
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


def _desktop_roots() -> list[Path]:
    roots: list[Path] = []
    for key in ("USERPROFILE", "OneDrive", "OneDriveCommercial", "OneDriveConsumer"):
        value = os.environ.get(key)
        if value:
            roots.append(Path(value) / "Desktop")
            roots.append(Path(value))
    try:
        roots.append(Path.home() / "Desktop")
    except Exception:
        pass
    unique: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        try:
            resolved = str(root.resolve()).lower()
        except Exception:
            resolved = str(root).lower()
        if root.exists() and resolved not in seen:
            unique.append(root)
            seen.add(resolved)
    return unique


def _looks_like_patchops_report(path: Path) -> bool:
    name = path.name.lower()
    if path.suffix.lower() != ".txt":
        return False
    if any(skip in name for skip in ("upload_menu_inventory", "redacted", "safe_upload_copy")):
        return False
    if any(token in name for token in ("patchops", "l26_", "l25_", "report")):
        return True
    return False


def _candidate_reports() -> list[Path]:
    candidates: list[Path] = []
    for root in _desktop_roots():
        try:
            for path in root.glob("*.txt"):
                if path.is_file() and _looks_like_patchops_report(path):
                    candidates.append(path)
        except Exception:
            pass
    candidates.sort(key=lambda p: (p.stat().st_mtime if p.exists() else 0.0), reverse=True)
    return candidates


def _select_source_report() -> Path:
    skipped: list[str] = []
    for path in _candidate_reports():
        try:
            if path.stat().st_size <= 0:
                continue
            # Small header read verifies this is really a PatchOps-style report without logging contents.
            with path.open("rb") as handle:
                head = handle.read(4096)
            if b"PATCHOPS" in head.upper() or b"Patch" in head:
                return path
        except Exception as exc:
            skipped.append(f"{path.name}:{type(exc).__name__}")
            continue
    raise RuntimeError("No readable PatchOps text report candidate found for upload-safe copy.")


def _is_onedrive_path(path: Path) -> bool:
    text = str(path).lower()
    return "onedrive" in text or "one drive" in text


def _make_upload_safe_copy(source: Path, output_dir: Path) -> Path:
    copy_dir = output_dir / "upload_safe_copy"
    copy_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    target = copy_dir / f"patchops_report_safe_upload_copy_{stamp}_{_hash_text(source.name)}.txt"
    last_error = ""
    for _ in range(5):
        try:
            with source.open("rb") as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)
                dst.flush()
                os.fsync(dst.fileno())
            # Reopen read-only after close to prove the uploader will not see our handle as open.
            with target.open("rb") as check:
                check.read(1)
            return target
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            time.sleep(0.4)
    raise RuntimeError(f"Could not create upload-safe report copy: {last_error}")


def _reject_status_blob(blob: str) -> bool:
    return any(word in blob for word in _STATUS_REJECT_WORDS)


def _score_strict_upload_menu_candidate(control_type: str, class_name: str, raw_name: str, automation_id: str) -> tuple[int, bool]:
    blob = " ".join([control_type, class_name, raw_name, automation_id]).lower()
    if _reject_status_blob(blob):
        return 0, True
    score = 0
    if control_type in {"Button", "MenuItem", "ListItem"}:
        score += 35
    elif control_type in {"Custom", "Hyperlink", "Text"}:
        score += 10
    for phrase in _UPLOAD_LABEL_HINTS:
        if phrase in blob:
            score += 110
    if "upload" in blob and ("file" in blob or "photo" in blob or "computer" in blob):
        score += 95
    if "attach" in blob and "file" in blob:
        score += 80
    if "browse" in blob and ("file" in blob or "computer" in blob):
        score += 70
    if "composer-plus-btn" in blob or "add files and more" in blob:
        return 0, False
    return score, False


def _find_strict_upload_menu_item(inventory_path: Path, timeout_seconds: float = 12.0, max_controls: int = 3400) -> tuple[UploadControlCandidate, object, int, bool]:
    import pywinauto  # type: ignore
    desktop = pywinauto.Desktop(backend="uia")
    deadline = time.time() + timeout_seconds
    rejected_status = False
    last_inventory_count = 0
    while time.time() < deadline:
        try:
            last_inventory_count = _snapshot_menu_inventory(inventory_path)
        except Exception:
            last_inventory_count = 0
        best: tuple[UploadControlCandidate, object] | None = None
        try:
            roots = list(desktop.windows())
        except Exception:
            roots = []
        for root in roots:
            queue: list[tuple[object, int, bool]] = [(root, 0, True)]
            scanned = 0
            while queue and scanned < max_controls:
                control, depth, page_scope = queue.pop(0)
                scanned += 1
                try:
                    info = control.element_info
                    control_type = _info_text(info, "control_type")
                    class_name = _info_text(info, "class_name")
                    raw_name = _info_text(info, "name")
                    automation_id = _info_text(info, "automation_id")
                except Exception:
                    control_type = class_name = raw_name = automation_id = ""
                score, rejected = _score_strict_upload_menu_candidate(control_type, class_name, raw_name, automation_id)
                rejected_status = rejected_status or rejected
                if score >= 100:
                    candidate = _candidate_from_control(control, depth, True, "strict_upload_files_menu_item", score)
                    if best is None or candidate.score > best[0].score:
                        best = (candidate, control)
                if depth < 9:
                    try:
                        for child in list(control.children())[:110]:
                            queue.append((child, depth + 1, page_scope))
                    except Exception:
                        pass
        if best is not None:
            return best[0], best[1], last_inventory_count, rejected_status
        time.sleep(0.25)
    raise RuntimeError(f"Strict Upload files menu item was not found; inventory_count={last_inventory_count}; inventory_path={inventory_path}; rejected_status={rejected_status}")


def _write_report(path: Path, result: UploadSafeCopyResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.12E upload-safe report copy strict menu repair",
        "upload_safe_copy_created:true" if result.upload_safe_copy_created else "upload_safe_copy_created:false",
        "upload_safe_copy_closed:true" if result.upload_safe_copy_closed else "upload_safe_copy_closed:false",
        "safe_copy_outside_onedrive:true" if result.safe_copy_outside_onedrive else "safe_copy_outside_onedrive:false",
        "onedrive_status_candidate_rejected:true" if result.onedrive_status_candidate_rejected else "onedrive_status_candidate_rejected:false",
        "report_upload_attempted:true" if result.report_upload_attempted else "report_upload_attempted:false",
        "file_attach_attempted:true" if result.file_attach_attempted else "file_attach_attempted:false",
        "chatgpt_enter_key_sent:false",
        "send_submit_performed:false",
        "chatgpt_prompt_submitted:false",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "prompt_text_logged:false",
        "file_content_logged:false",
        "No full URL, file path, prompt, conversation text, or file contents are logged.",
        "",
        f"source_report_path_redacted: {result.source_report_path_redacted}",
        f"source_report_name: {result.source_report_name}",
        f"source_report_hash: {result.source_report_hash}",
        f"source_report_size_bytes: {result.source_report_size_bytes}",
        f"upload_safe_copy_path_redacted: {result.upload_safe_copy_path_redacted}",
        f"upload_safe_copy_name: {result.upload_safe_copy_name}",
        f"upload_safe_copy_hash: {result.upload_safe_copy_hash}",
        f"upload_safe_copy_size_bytes: {result.upload_safe_copy_size_bytes}",
        f"current_url_matches_target: {result.current_url_matches_target}",
        f"navigation_skipped_existing_target: {result.navigation_skipped_existing_target}",
        f"composer_focus_verified: {result.composer_focus_verified}",
        f"upload_menu_candidate_name_redacted: {result.upload_menu_candidate_name_redacted}",
        f"upload_menu_candidate_control_type: {result.upload_menu_candidate_control_type}",
        f"file_picker_opened: {result.file_picker_opened}",
        f"upload_staging_observed: {result.upload_staging_observed}",
        f"staging_observation_method: {result.staging_observation_method}",
        f"failure_layer: {result.failure_layer}",
        f"error: {result.error}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: UploadSafeCopyResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_12e_upload_safe_copy_gate(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 10.0, allow_report_upload: bool = False) -> UploadSafeCopyResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_12e_upload_safe_copy_result.json"
    report_path = out_dir / "normal_edge_l26_12e_upload_safe_copy_report.txt"
    menu_inventory_path = out_dir / "normal_edge_l26_12e_upload_menu_inventory_redacted.txt"
    target_ok = _canonical_url(target_url) == _canonical_url(REQUESTED_CHAT_URL)
    state: dict[str, object] = {
        "target_url_is_requested_chat": target_ok,
        "allow_report_upload_requested": allow_report_upload,
        "live_report_path": str(report_path),
        "json_path": str(json_path),
        "menu_inventory_path": str(menu_inventory_path),
    }
    try:
        if not allow_report_upload:
            raise RuntimeError("L26.12E requires explicit --allow-report-upload to attach the report file.")
        current_observed, page_ready, skipped_nav, attempted_nav, current_url = _ensure_target_loaded(out_dir, target_url, start_if_missing, settle_seconds)
        state.update({
            "current_url_matches_target": _canonical_url(current_url) == _canonical_url(target_url),
            "navigation_skipped_existing_target": skipped_nav,
            "navigation_attempted": attempted_nav,
            "target_page_ready": page_ready,
        })
        if not (target_ok and page_ready):
            raise RuntimeError("Target chat is not ready for report upload staging.")
        composer_found, focus_verified = _verify_direct_composer_focus()
        state.update({"composer_candidate_found": composer_found, "composer_focus_verified": focus_verified})
        if not (composer_found and focus_verified):
            raise RuntimeError("Composer focus was not verified.")
        source = _select_source_report()
        safe_copy = _make_upload_safe_copy(source, out_dir)
        source_hash = _hash_file(source)
        copy_hash = _hash_file(safe_copy)
        source_size = source.stat().st_size
        copy_size = safe_copy.stat().st_size
        state.update({
            "source_report_found": True,
            "source_report_path_redacted": _redact_path(source),
            "source_report_name": source.name,
            "source_report_hash": source_hash,
            "source_report_size_bytes": int(source_size),
            "source_report_is_text": source.suffix.lower() == ".txt",
            "upload_safe_copy_created": True,
            "upload_safe_copy_path_redacted": _redact_path(safe_copy),
            "upload_safe_copy_name": safe_copy.name,
            "upload_safe_copy_hash": copy_hash,
            "upload_safe_copy_size_bytes": int(copy_size),
            "upload_safe_copy_closed": True,
            "safe_copy_outside_onedrive": not _is_onedrive_path(safe_copy),
        })
        if source_hash != copy_hash or source_size != copy_size:
            raise RuntimeError("Upload-safe report copy hash/size mismatch.")
        plus, plus_control = _find_plus_control()
        state.update({"plus_button_found": True})
        _click_control(plus_control)
        state.update({"plus_button_clicked": True})
        time.sleep(0.8)
        upload_item, upload_control, inventory_count, rejected_status = _find_strict_upload_menu_item(menu_inventory_path)
        state.update({
            "upload_menu_item_found": True,
            "upload_menu_candidate_name_redacted": upload_item.name_redacted,
            "upload_menu_candidate_control_type": upload_item.control_type,
            "onedrive_status_candidate_rejected": rejected_status,
            "upload_menu_inventory_written": True,
            "upload_menu_inventory_count": inventory_count,
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
            "failure_layer": "" if staged else "upload_safe_copy_staging_observation",
            "error": "" if staged else "Upload-safe copy was selected but staged attachment was not observed.",
        })
    except Exception as exc:
        inv_count = 0
        try:
            inv_count = _snapshot_menu_inventory(menu_inventory_path)
        except Exception:
            pass
        state.update({
            "upload_menu_inventory_written": menu_inventory_path.exists(),
            "upload_menu_inventory_count": inv_count,
            "result": "FAIL",
            "failure_layer": "upload_safe_report_copy_strict_menu_repair",
            "error": f"{type(exc).__name__}: {exc}",
        })
    result = UploadSafeCopyResult(**state)
    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_12e_acceptance(result: UploadSafeCopyResult) -> None:
    payload = result.to_payload()
    required_true = [
        "target_url_is_requested_chat",
        "current_url_matches_target",
        "navigation_skipped_existing_target",
        "target_page_ready",
        "composer_candidate_found",
        "composer_focus_verified",
        "source_report_found",
        "source_report_is_text",
        "upload_safe_copy_created",
        "upload_safe_copy_closed",
        "safe_copy_outside_onedrive",
        "allow_report_upload_requested",
        "plus_button_found",
        "plus_button_clicked",
        "upload_menu_item_found",
        "upload_menu_item_clicked",
        "onedrive_status_candidate_rejected",
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
        raise AssertionError(f"L26.12E acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
