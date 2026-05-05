from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.edge_rpa.edge_l26_12s_post_submit_idle_observer import observe_idle
from patchops.edge_rpa.edge_l26_12u_short_safe_inner_patchops_report_upload import submit_after_upload, upload_short_safe_copy
from patchops.edge_rpa.edge_l26_14c_response_action_candidate_selector_dry_run import select_response_action_candidate
from patchops.edge_rpa.edge_l26_14d_visible_attachment_upload_gate_repair import _attachment_signals, _is_canonical_source
from patchops.edge_rpa.edge_l26_14f_visible_gate_canonical_publish_restore import build_current_canonical_report, hash_file
from patchops.edge_rpa.edge_l26_12m_upload_gate import drive_valid, has_bad_lc_prefix

PATCH_NAME = "l26_14h_attachment_detector_false_negative_tolerant_cycle"


@dataclass(frozen=True)
class AttachmentDetectorFalseNegativeTolerantCycleResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    upload_source_is_canonical: bool = False
    uploaded_safe_copy_path: str = ""
    uploaded_safe_copy_hash_matches_source: bool = False
    uploaded_safe_copy_drive_valid: bool = False
    uploaded_safe_copy_lc_prefix_detected: bool = False
    picker_confirmed_upload_accepted: bool = False
    attachment_visible_before_submit: bool = False
    attachment_signal_count_before_submit: int = 0
    attachment_detector_false_negative_tolerated: bool = False
    attachment_gate_effective_passed: bool = False
    chatgpt_submit_performed: bool = False
    submit_method: str = ""
    idle_observation_completed: bool = False
    ready_for_next_probe: bool = False
    current_canonical_report_created: bool = False
    current_canonical_report_path: str = ""
    current_canonical_contains_apply_evidence: bool = False
    current_canonical_contains_browser_evidence: bool = False
    latest_canonical_pointer_created: bool = False
    latest_canonical_matches_current: bool = False
    selector_completed: bool = False
    candidate_selected: bool = False
    selected_candidate_kind: str = ""
    selected_candidate_fingerprint: str = ""
    selected_candidate_rect_hash: str = ""
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


def write_json(path: Path, result: AttachmentDetectorFalseNegativeTolerantCycleResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: AttachmentDetectorFalseNegativeTolerantCycleResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def copy_upload_source(source: Path, bridge_dir: Path) -> Path:
    bridge_dir.mkdir(parents=True, exist_ok=True)
    target = bridge_dir / f"canonical_visible_attachment_{int(time.time())}.txt"
    with source.open("rb") as src, target.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
        dst.flush()
        os.fsync(dst.fileno())
    return target


def publish_current_canonical(canonical_path: Path, latest_path: Path, inner_report_path: Path, live_payload: dict[str, object]) -> tuple[bool, bool, bool]:
    # Reuse the canonical writer shape from L26.14F, but feed this patch's payload.
    has_apply, has_browser, _size = build_current_canonical_report(canonical_path, inner_report_path, live_payload)
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(canonical_path, latest_path)
    matches = hash_file(canonical_path) == hash_file(latest_path)
    return has_apply, has_browser, matches


def run_attachment_detector_false_negative_tolerant_cycle(
    short_live_root: Path,
    latest_canonical_path: Path,
    operator_report_path: Path,
    inner_patchops_report_path: Path,
    upload_bridge_dir: Path,
    current_canonical_report_path: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    allow_attachment_detector_fallback: bool,
    observe_seconds: int,
    probe_seconds: int,
    attachment_verify_seconds: int,
) -> AttachmentDetectorFalseNegativeTolerantCycleResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14h_attachment_detector_false_negative_tolerant_cycle_result.json"
    live_report_path = short_live_root / "l26_14h_attachment_detector_false_negative_tolerant_cycle_live_report.txt"
    state: dict[str, object] = {}
    try:
        if not allow_report_upload:
            raise RuntimeError("Missing explicit --allow-report-upload")
        source = latest_canonical_path.resolve()
        if not source.exists() or not source.is_file():
            raise RuntimeError(f"Latest canonical source does not exist: {source}")
        source_is_canonical = _is_canonical_source(source)
        if not source_is_canonical:
            raise RuntimeError("Latest canonical source is not canonical browser evidence.")
        safe = copy_upload_source(source, upload_bridge_dir.resolve())
        state.update({
            "upload_source_is_canonical": True,
            "uploaded_safe_copy_path": str(safe),
            "uploaded_safe_copy_hash_matches_source": hash_file(source) == hash_file(safe) and source.stat().st_size == safe.stat().st_size,
            "uploaded_safe_copy_drive_valid": drive_valid(safe),
            "uploaded_safe_copy_lc_prefix_detected": has_bad_lc_prefix(safe),
        })
        if not state["uploaded_safe_copy_hash_matches_source"]:
            raise RuntimeError("Safe upload copy hash mismatch.")
        if not drive_valid(safe) or has_bad_lc_prefix(safe):
            raise RuntimeError(f"Unsafe upload path: {safe}")
        upload_state = upload_short_safe_copy(safe)
        picker_ok = bool(upload_state.get("picker_confirmed_upload_accepted"))
        state.update({"picker_confirmed_upload_accepted": picker_ok})
        if not picker_ok:
            raise RuntimeError("Picker-confirmed upload was not accepted.")
        visible = _attachment_signals(safe.name, attachment_verify_seconds)
        visible_ok = bool(visible.get("found"))
        state.update({"attachment_visible_before_submit": visible_ok, "attachment_signal_count_before_submit": int(visible.get("signals") or 0)})
        fallback = bool(allow_attachment_detector_fallback and picker_ok and not visible_ok)
        gate_ok = visible_ok or fallback
        state.update({"attachment_detector_false_negative_tolerated": fallback, "attachment_gate_effective_passed": gate_ok})
        if not gate_ok:
            raise RuntimeError("Attachment gate failed: picker accepted but detector fallback disabled or unavailable.")
        submit_state = submit_after_upload(allow_chatgpt_submit)
        state.update({"chatgpt_submit_performed": bool(submit_state.get("chatgpt_submit_performed")), "submit_method": str(submit_state.get("submit_method") or "")})
        if not state["chatgpt_submit_performed"]:
            raise RuntimeError("ChatGPT submit did not occur.")
        obs = observe_idle(observe_seconds)
        ready = bool(obs.get("edge_window_found")) and bool(obs.get("stop_generating_absent_at_end"))
        state.update({"idle_observation_completed": True, "ready_for_next_probe": ready})
        if not ready:
            raise RuntimeError("Post-submit idle/readiness was not confirmed.")
        selected = select_response_action_candidate(probe_seconds)
        best = dict(selected.get("best") or {})
        state.update({
            "selector_completed": True,
            "candidate_selected": bool(best),
            "selected_candidate_kind": str(best.get("kind") or ""),
            "selected_candidate_fingerprint": str(best.get("fingerprint") or ""),
            "selected_candidate_rect_hash": str(best.get("rect_hash") or ""),
            "selected_candidate_click_performed": False,
        })
        live_payload = dict(state)
        live_payload.update({"result": "PASS", "visible_attachment_gate_passed": bool(visible_ok), "attachment_gate_effective_passed": gate_ok})
        has_apply, has_browser, matches = publish_current_canonical(current_canonical_report_path, latest_canonical_path, inner_patchops_report_path, live_payload)
        state.update({
            "current_canonical_report_created": current_canonical_report_path.exists(),
            "current_canonical_report_path": str(current_canonical_report_path),
            "current_canonical_contains_apply_evidence": has_apply,
            "current_canonical_contains_browser_evidence": has_browser,
            "latest_canonical_pointer_created": latest_canonical_path.exists(),
            "latest_canonical_matches_current": matches,
        })
        ok = bool(best) and has_apply and has_browser and matches
        state.update({"result": "PASS" if ok else "FAIL", "failure_layer": "" if ok else "attachment_detector_false_negative_tolerant_cycle", "error": "" if ok else "Canonical publish or selector proof failed after effective attachment gate."})
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "attachment_detector_false_negative_tolerant_cycle", "error": f"{type(exc).__name__}: {exc}"})
    result = AttachmentDetectorFalseNegativeTolerantCycleResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: AttachmentDetectorFalseNegativeTolerantCycleResult) -> None:
    p = result.to_payload()
    true_keys = [
        "upload_source_is_canonical", "uploaded_safe_copy_hash_matches_source", "uploaded_safe_copy_drive_valid",
        "picker_confirmed_upload_accepted", "attachment_gate_effective_passed", "chatgpt_submit_performed",
        "idle_observation_completed", "ready_for_next_probe", "current_canonical_report_created",
        "current_canonical_contains_apply_evidence", "current_canonical_contains_browser_evidence",
        "latest_canonical_pointer_created", "latest_canonical_matches_current", "selector_completed", "candidate_selected",
    ]
    false_keys = [
        "uploaded_safe_copy_lc_prefix_detected", "selected_candidate_click_performed", "candidate_click_performed",
        "download_click_performed", "generated_file_click_performed", "conversation_text_logged", "full_conversation_text_logged",
        "prompt_text_logged", "file_content_logged", "run_package_invoked", "webdriver_used", "selenium_imported",
        "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if not (p.get("attachment_visible_before_submit") or p.get("attachment_detector_false_negative_tolerated")):
        missing.append("visible_or_detector_fallback")
    for key in ("uploaded_safe_copy_path", "current_canonical_report_path", "selected_candidate_kind", "selected_candidate_fingerprint", "selected_candidate_rect_hash"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14H acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
