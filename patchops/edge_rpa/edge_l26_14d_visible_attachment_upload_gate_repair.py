from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import pywinauto  # type: ignore

from patchops.edge_rpa.edge_l26_12s_post_submit_idle_observer import observe_idle
from patchops.edge_rpa.edge_l26_12u_short_safe_inner_patchops_report_upload import submit_after_upload, upload_short_safe_copy
from patchops.edge_rpa.edge_l26_14c_response_action_candidate_selector_dry_run import select_response_action_candidate
from patchops.edge_rpa.edge_l26_14b_response_readiness_stability_classifier import run_response_readiness_stability_classifier
from patchops.edge_rpa.edge_upload_safe_report_copy_gate import _hash_text, _info_text
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids
from patchops.edge_rpa.edge_l26_12m_upload_gate import drive_valid, has_bad_lc_prefix

PATCH_NAME = "l26_14d_visible_attachment_upload_gate_repair"


@dataclass(frozen=True)
class VisibleAttachmentUploadGateRepairResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    upload_source_is_canonical: bool = False
    attachment_source_basename: str = ""
    attachment_source_basename_hash: str = ""
    uploaded_safe_copy_path: str = ""
    uploaded_safe_copy_hash_matches_source: bool = False
    uploaded_safe_copy_drive_valid: bool = False
    uploaded_safe_copy_lc_prefix_detected: bool = False
    picker_confirmed_upload_accepted: bool = False
    attachment_visible_before_submit: bool = False
    attachment_signal_count_before_submit: int = 0
    attachment_visible_after_submit: bool = False
    attachment_signal_count_after_submit: int = 0
    visible_attachment_gate_passed: bool = False
    chatgpt_submit_performed: bool = False
    submit_method: str = ""
    idle_observation_completed: bool = False
    ready_for_next_probe: bool = False
    selector_started: bool = False
    selector_completed: bool = False
    candidate_selected: bool = False
    selected_candidate_kind: str = ""
    selected_candidate_fingerprint: str = ""
    selected_candidate_rect_hash: str = ""
    selected_candidate_click_allowed: bool = False
    selected_candidate_click_performed: bool = False
    candidate_click_performed: bool = False
    download_click_performed: bool = False
    generated_file_click_performed: bool = False
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    prompt_text_logged: bool = False
    file_content_logged: bool = False
    run_package_invoked: bool = False
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_dom_automation_used: bool = False
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def copy_to_unique_short_upload(source: Path, short_upload_dir: Path) -> Path:
    short_upload_dir.mkdir(parents=True, exist_ok=True)
    safe_path = short_upload_dir / f"canonical_visible_attachment_{int(time.time())}.txt"
    with source.open("rb") as src, safe_path.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
        dst.flush()
        os.fsync(dst.fileno())
    return safe_path


def write_json(path: Path, result: VisibleAttachmentUploadGateRepairResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: VisibleAttachmentUploadGateRepairResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def _attachment_signals(basename: str, timeout_seconds: int) -> dict[str, object]:
    deadline = time.time() + max(3, min(int(timeout_seconds), 60))
    basename_l = basename.lower()
    signals = 0
    found = False
    while time.time() < deadline:
        desktop = pywinauto.Desktop(backend="uia")
        _windows, wrappers = discover_edge_windows(desktop, edge_process_ids())
        for window in list(wrappers or [])[:3]:
            queue: list[tuple[object, int]] = [(window, 0)]
            local = 0
            while queue and local < 4500:
                control, depth = queue.pop(0)
                local += 1
                try:
                    info = control.element_info
                    control_type = _info_text(info, "control_type")
                    name = _info_text(info, "name")
                    automation_id = _info_text(info, "automation_id")
                    class_name = _info_text(info, "class_name")
                except Exception:
                    control_type = name = automation_id = class_name = ""
                text = " ".join([control_type or "", name or "", automation_id or "", class_name or ""]).lower()
                # Internal check only; never write labels/text to report.
                if basename_l in text or ("canonical_visible_attachment" in text and ".txt" in text) or ("remove" in text and "file" in text) or ("attachment" in text and ".txt" in text):
                    signals += 1
                    found = True
                if depth < 9:
                    try:
                        for child in list(control.children())[:100]:
                            queue.append((child, depth + 1))
                    except Exception:
                        pass
        if found:
            break
        time.sleep(1.0)
    return {"found": found, "signals": signals}


def _is_canonical_source(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    return "PATCHOPS CANONICAL BROWSER EVIDENCE REPORT" in text and "PATCHOPS APPLY EVIDENCE" in text and "BROWSER LIVE PROOF SUMMARY" in text


def run_visible_attachment_upload_gate_repair(
    short_live_root: Path,
    latest_canonical_path: Path,
    operator_report_path: Path,
    inner_patchops_report_path: Path,
    short_upload_dir: Path,
    current_canonical_report_path: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    observe_seconds: int,
    probe_seconds: int,
    stability_delay_seconds: int,
    attachment_verify_seconds: int,
) -> VisibleAttachmentUploadGateRepairResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14d_visible_attachment_upload_gate_repair_result.json"
    live_report_path = short_live_root / "l26_14d_visible_attachment_upload_gate_repair_live_report.txt"
    state: dict[str, object] = {}
    try:
        if not allow_report_upload:
            raise RuntimeError("Missing explicit --allow-report-upload")
        source = latest_canonical_path.resolve()
        if not source.exists() or not source.is_file():
            raise RuntimeError(f"Stable latest canonical source does not exist: {source}")
        source_is_canonical = _is_canonical_source(source)
        if not source_is_canonical:
            raise RuntimeError("Stable latest canonical source is not a canonical browser evidence report.")
        safe = copy_to_unique_short_upload(source, short_upload_dir.resolve())
        src_hash = hash_file(source)
        safe_hash = hash_file(safe)
        basename = safe.name
        state.update({
            "upload_source_is_canonical": source_is_canonical,
            "attachment_source_basename": basename,
            "attachment_source_basename_hash": _hash_text(basename),
            "uploaded_safe_copy_path": str(safe),
            "uploaded_safe_copy_hash_matches_source": src_hash == safe_hash and source.stat().st_size == safe.stat().st_size,
            "uploaded_safe_copy_drive_valid": drive_valid(safe),
            "uploaded_safe_copy_lc_prefix_detected": has_bad_lc_prefix(safe),
        })
        if src_hash != safe_hash:
            raise RuntimeError("Short upload copy hash mismatch.")
        if not drive_valid(safe) or has_bad_lc_prefix(safe):
            raise RuntimeError(f"Unsafe short upload path: {safe}")
        upload_state = upload_short_safe_copy(safe)
        state.update({"picker_confirmed_upload_accepted": bool(upload_state.get("picker_confirmed_upload_accepted"))})
        if not state["picker_confirmed_upload_accepted"]:
            raise RuntimeError("Picker-confirmed upload was not accepted.")
        before = _attachment_signals(basename, attachment_verify_seconds)
        state.update({"attachment_visible_before_submit": bool(before.get("found")), "attachment_signal_count_before_submit": int(before.get("signals") or 0)})
        if not state["attachment_visible_before_submit"]:
            raise RuntimeError("Visible attachment signal was not detected before submit; refusing false PASS.")
        submit_state = submit_after_upload(allow_chatgpt_submit)
        state.update({"chatgpt_submit_performed": bool(submit_state.get("chatgpt_submit_performed")), "submit_method": str(submit_state.get("submit_method") or "")})
        obs = observe_idle(observe_seconds)
        state.update({"idle_observation_completed": True, "ready_for_next_probe": bool(obs.get("edge_window_found")) and bool(obs.get("stop_generating_absent_at_end"))})
        after = _attachment_signals(basename, max(3, min(attachment_verify_seconds, 12)))
        state.update({"attachment_visible_after_submit": bool(after.get("found")), "attachment_signal_count_after_submit": int(after.get("signals") or 0)})
        # After submit the chip may disappear into the sent message, so before-submit visibility is the hard gate.
        state.update({"visible_attachment_gate_passed": bool(state["attachment_visible_before_submit"]) and bool(state["chatgpt_submit_performed"]) and bool(state["ready_for_next_probe"])})
        if not state["visible_attachment_gate_passed"]:
            raise RuntimeError("Visible attachment gate, submit, or idle readiness failed.")
        state.update({"selector_started": True})
        selected = select_response_action_candidate(probe_seconds)
        best = dict(selected.get("best") or {})
        state.update({
            "selector_completed": True,
            "candidate_selected": bool(best),
            "selected_candidate_kind": str(best.get("kind") or ""),
            "selected_candidate_fingerprint": str(best.get("fingerprint") or ""),
            "selected_candidate_rect_hash": str(best.get("rect_hash") or ""),
            "selected_candidate_click_allowed": False,
            "selected_candidate_click_performed": False,
            "result": "PASS" if bool(best) else "FAIL",
            "failure_layer": "" if bool(best) else "visible_attachment_selector_dry_run",
            "error": "" if bool(best) else "No response action candidate selected after visible attachment gate.",
        })
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "visible_attachment_upload_gate_repair", "error": f"{type(exc).__name__}: {exc}"})
    result = VisibleAttachmentUploadGateRepairResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: VisibleAttachmentUploadGateRepairResult) -> None:
    p = result.to_payload()
    true_keys = [
        "upload_source_is_canonical", "uploaded_safe_copy_hash_matches_source", "uploaded_safe_copy_drive_valid",
        "picker_confirmed_upload_accepted", "attachment_visible_before_submit", "visible_attachment_gate_passed",
        "chatgpt_submit_performed", "idle_observation_completed", "ready_for_next_probe", "selector_started",
        "selector_completed", "candidate_selected",
    ]
    false_keys = [
        "uploaded_safe_copy_lc_prefix_detected", "selected_candidate_click_allowed", "selected_candidate_click_performed",
        "candidate_click_performed", "download_click_performed", "generated_file_click_performed", "conversation_text_logged",
        "full_conversation_text_logged", "prompt_text_logged", "file_content_logged", "run_package_invoked", "webdriver_used",
        "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if int(p.get("attachment_signal_count_before_submit") or 0) <= 0:
        missing.append("attachment_signal_count_before_submit_positive")
    for key in ("attachment_source_basename", "attachment_source_basename_hash", "selected_candidate_kind", "selected_candidate_fingerprint", "selected_candidate_rect_hash"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14D acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
