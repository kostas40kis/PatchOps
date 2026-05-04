from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.edge_rpa.edge_l26_12u_short_safe_inner_patchops_report_upload import upload_short_safe_copy, submit_after_upload
from patchops.edge_rpa.edge_l26_12s_post_submit_idle_observer import observe_idle
from patchops.edge_rpa.edge_l26_12m_upload_gate import drive_valid, has_bad_lc_prefix

PATCH_NAME = "l26_13a_canonical_report_upload_target_smoke"


@dataclass(frozen=True)
class CanonicalReportUploadTargetSmokeResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    canonical_upload_source_exists: bool = False
    canonical_source_is_canonical_report: bool = False
    canonical_source_contains_apply_evidence: bool = False
    canonical_source_contains_browser_evidence: bool = False
    canonical_source_hash: str = ""
    canonical_source_size_bytes: int = 0
    uploaded_report_role: str = ""
    uploaded_report_count: int = 0
    uploaded_safe_copy_path: str = ""
    uploaded_safe_copy_path_length: int = 0
    uploaded_safe_copy_hash_matches_source: bool = False
    uploaded_safe_copy_drive_valid: bool = False
    uploaded_safe_copy_lc_prefix_detected: bool = False
    operator_report_uploaded: bool = False
    raw_apply_report_uploaded_as_browser_target: bool = False
    picker_confirmed_upload_accepted: bool = False
    allow_chatgpt_submit: bool = False
    chatgpt_submit_performed: bool = False
    submit_method: str = ""
    idle_observation_completed: bool = False
    ready_for_next_probe: bool = False
    observe_seconds_requested: int = 0
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    prompt_text_logged: bool = False
    file_content_logged: bool = False
    download_click_performed: bool = False
    generated_file_click_performed: bool = False
    candidate_click_performed: bool = False
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


def copy_to_short_upload(canonical_source: Path, short_upload_dir: Path) -> Path:
    short_upload_dir.mkdir(parents=True, exist_ok=True)
    safe_path = short_upload_dir / "canonical_browser_evidence_report.txt"
    with canonical_source.open("rb") as src, safe_path.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
        dst.flush()
        os.fsync(dst.fileno())
    with safe_path.open("rb") as check:
        check.read(1)
    return safe_path


def write_json(path: Path, result: CanonicalReportUploadTargetSmokeResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: CanonicalReportUploadTargetSmokeResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def run_canonical_report_upload_target_smoke(
    short_live_root: Path,
    canonical_upload_source_path: Path,
    operator_report_path: Path,
    inner_patchops_report_path: Path,
    short_upload_dir: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    observe_seconds: int,
) -> CanonicalReportUploadTargetSmokeResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_13a_canonical_report_upload_target_smoke_result.json"
    live_report_path = short_live_root / "l26_13a_canonical_report_upload_target_smoke_live_report.txt"
    state: dict[str, object] = {"observe_seconds_requested": int(observe_seconds), "allow_chatgpt_submit": allow_chatgpt_submit}
    try:
        if not allow_report_upload:
            raise RuntimeError("Missing explicit --allow-report-upload")
        source = canonical_upload_source_path.resolve()
        operator = operator_report_path.resolve()
        inner = inner_patchops_report_path.resolve()
        if not source.exists() or not source.is_file():
            raise RuntimeError(f"Canonical upload source does not exist: {source}")
        text = source.read_text(encoding="utf-8", errors="replace")
        source_hash = hash_file(source)
        source_size = source.stat().st_size
        is_canonical = "PATCHOPS CANONICAL BROWSER EVIDENCE REPORT" in text and source.name.endswith("_canonical.txt")
        has_apply = "PATCHOPS APPLY EVIDENCE" in text and "Result" in text
        has_browser = "BROWSER LIVE PROOF SUMMARY" in text and "browser_live_passed: True" in text
        safe_copy = copy_to_short_upload(source, short_upload_dir.resolve())
        safe_hash = hash_file(safe_copy)
        safe_size = safe_copy.stat().st_size
        state.update({
            "canonical_upload_source_exists": True,
            "canonical_source_is_canonical_report": is_canonical,
            "canonical_source_contains_apply_evidence": has_apply,
            "canonical_source_contains_browser_evidence": has_browser,
            "canonical_source_hash": source_hash,
            "canonical_source_size_bytes": int(source_size),
            "uploaded_report_role": "canonical_browser_evidence_report",
            "uploaded_report_count": 1,
            "uploaded_safe_copy_path": str(safe_copy),
            "uploaded_safe_copy_path_length": len(str(safe_copy)),
            "uploaded_safe_copy_hash_matches_source": source_hash == safe_hash and source_size == safe_size,
            "uploaded_safe_copy_drive_valid": drive_valid(safe_copy),
            "uploaded_safe_copy_lc_prefix_detected": has_bad_lc_prefix(safe_copy),
            "operator_report_uploaded": source == operator,
            "raw_apply_report_uploaded_as_browser_target": source == inner,
        })
        if not is_canonical:
            raise RuntimeError("Upload source is not a canonical browser evidence report.")
        if not has_apply or not has_browser:
            raise RuntimeError("Canonical source does not contain both apply and browser evidence.")
        if source == operator:
            raise RuntimeError("Refusing to upload outer operator report.")
        if source == inner:
            raise RuntimeError("Refusing to upload raw current PatchOps apply report as browser target.")
        if source_hash != safe_hash or source_size != safe_size:
            raise RuntimeError("Short safe canonical copy hash/size does not match source.")
        if not drive_valid(safe_copy) or has_bad_lc_prefix(safe_copy):
            raise RuntimeError(f"Short safe canonical copy path is invalid: {safe_copy}")
        upload_state = upload_short_safe_copy(safe_copy)
        state.update({"picker_confirmed_upload_accepted": bool(upload_state.get("picker_confirmed_upload_accepted"))})
        if not state["picker_confirmed_upload_accepted"]:
            raise RuntimeError("Picker-confirmed upload was not accepted.")
        submit_state = submit_after_upload(allow_chatgpt_submit)
        state.update({
            "chatgpt_submit_performed": bool(submit_state.get("chatgpt_submit_performed")),
            "submit_method": str(submit_state.get("submit_method") or ""),
        })
        obs = observe_idle(observe_seconds)
        state.update({
            "idle_observation_completed": True,
            "ready_for_next_probe": bool(obs.get("edge_window_found")) and bool(obs.get("stop_generating_absent_at_end")),
        })
        ok = bool(state.get("picker_confirmed_upload_accepted")) and bool(state.get("chatgpt_submit_performed")) and bool(state.get("ready_for_next_probe"))
        state.update({"result": "PASS" if ok else "FAIL", "failure_layer": "" if ok else "canonical_upload_target_observation", "error": "" if ok else "Canonical upload/submit/idle did not pass."})
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "canonical_report_upload_target_smoke", "error": f"{type(exc).__name__}: {exc}"})
    result = CanonicalReportUploadTargetSmokeResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: CanonicalReportUploadTargetSmokeResult) -> None:
    p = result.to_payload()
    true_keys = [
        "canonical_upload_source_exists", "canonical_source_is_canonical_report", "canonical_source_contains_apply_evidence",
        "canonical_source_contains_browser_evidence", "uploaded_safe_copy_hash_matches_source", "uploaded_safe_copy_drive_valid",
        "picker_confirmed_upload_accepted", "allow_chatgpt_submit", "chatgpt_submit_performed", "idle_observation_completed",
        "ready_for_next_probe",
    ]
    false_keys = [
        "operator_report_uploaded", "raw_apply_report_uploaded_as_browser_target", "uploaded_safe_copy_lc_prefix_detected",
        "conversation_text_logged", "full_conversation_text_logged", "prompt_text_logged", "file_content_logged",
        "download_click_performed", "generated_file_click_performed", "candidate_click_performed", "run_package_invoked",
        "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if p.get("uploaded_report_role") != "canonical_browser_evidence_report":
        missing.append("uploaded_report_role_canonical")
    if int(p.get("uploaded_report_count") or 0) != 1:
        missing.append("uploaded_report_count_1")
    for key in ("canonical_source_hash", "uploaded_safe_copy_path", "submit_method"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.13A acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
