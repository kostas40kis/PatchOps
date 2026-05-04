from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.edge_rpa.edge_l26_12x_generated_artifact_candidate_diff_filter import GeneratedArtifactCandidateDiffResult, run_generated_candidate_diff_filter

PATCH_NAME = "l26_12y_canonical_browser_evidence_report"


@dataclass(frozen=True)
class CanonicalBrowserEvidenceReportResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    canonical_report_created: bool = False
    canonical_report_path: str = ""
    canonical_report_size_bytes: int = 0
    canonical_contains_patchops_apply_evidence: bool = False
    canonical_contains_browser_live_evidence: bool = False
    canonical_contains_upload_submit_probe_evidence: bool = False
    canonical_uploaded_this_run: bool = False
    uploaded_report_role_this_run: str = "inner_patchops_apply_report_short_safe_copy"
    uploaded_report_count: int = 0
    uploaded_safe_copy_hash_matches_inner_report: bool = False
    upload_submit_idle_result: str = "FAIL"
    chatgpt_submit_performed: bool = False
    ready_for_next_probe: bool = False
    post_scan_completed: bool = False
    novel_candidate_count: int = 0
    baseline_candidate_count: int = 0
    post_candidate_count: int = 0
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


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _write_json(path: Path, result: CanonicalBrowserEvidenceReportResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def _write_live_report(path: Path, result: CanonicalBrowserEvidenceReportResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def _build_canonical_report(
    canonical_report_path: Path,
    inner_patchops_report_path: Path,
    live_payload: dict[str, object],
) -> tuple[bool, bool, bool, int]:
    inner_text = _read_text(inner_patchops_report_path)
    lines: list[str] = []
    lines.append("PATCHOPS CANONICAL BROWSER EVIDENCE REPORT")
    lines.append("==========================================")
    lines.append(f"Patch: {PATCH_NAME}")
    lines.append(f"InnerPatchOpsReportPath: {inner_patchops_report_path}")
    lines.append("")
    lines.append("CANONICAL UPLOAD NOTE")
    lines.append("=====================")
    lines.append("This canonical report is created after the browser live proof completes.")
    lines.append("It was not the file uploaded during this same run, because a report cannot contain proof of its own future upload.")
    lines.append("UploadedReportRoleThisRun: inner_patchops_apply_report_short_safe_copy")
    lines.append("CanonicalUploadedThisRun: false")
    lines.append("")
    lines.append("PATCHOPS APPLY EVIDENCE")
    lines.append("=======================")
    lines.append(inner_text.rstrip())
    lines.append("")
    lines.append("BROWSER LIVE PROOF SUMMARY")
    lines.append("==========================")
    safe_keys = [
        "result", "upload_submit_idle_result", "uploaded_report_count", "uploaded_safe_copy_hash_matches_inner_report",
        "chatgpt_submit_performed", "ready_for_next_probe", "baseline_scan_completed", "baseline_candidate_count",
        "post_scan_completed", "post_candidate_count", "known_candidate_count", "novel_candidate_count",
        "novel_actionable_candidate_count", "novel_clickable_candidate_count", "generated_candidate_click_allowed",
        "candidate_click_performed", "download_click_performed", "generated_file_click_performed", "conversation_text_logged",
        "prompt_text_logged", "file_content_logged", "run_package_invoked", "webdriver_used", "selenium_imported",
        "browser_dom_automation_used", "failure_layer", "error",
    ]
    for key in safe_keys:
        if key in live_payload:
            lines.append(f"{key}: {live_payload.get(key)}")
    lines.append("")
    lines.append("FINAL CANONICAL CHECKLIST")
    lines.append("=========================")
    lines.append(f"patchops_apply_passed: {'Result   : PASS' in inner_text or 'Result : PASS' in inner_text}")
    lines.append(f"browser_live_passed: {live_payload.get('result') == 'PASS'}")
    lines.append(f"single_report_uploaded_this_run: {live_payload.get('uploaded_report_count') == 1}")
    lines.append(f"submit_performed: {bool(live_payload.get('chatgpt_submit_performed'))}")
    lines.append(f"no_candidate_or_download_clicks: {not bool(live_payload.get('candidate_click_performed')) and not bool(live_payload.get('download_click_performed')) and not bool(live_payload.get('generated_file_click_performed'))}")
    lines.append(f"no_content_logging: {not bool(live_payload.get('conversation_text_logged')) and not bool(live_payload.get('prompt_text_logged')) and not bool(live_payload.get('file_content_logged'))}")
    lines.append("")
    lines.append("RESULT")
    lines.append("======")
    passed = ("Result   : PASS" in inner_text or "Result : PASS" in inner_text) and live_payload.get("result") == "PASS"
    lines.append("ExitCode : 0" if passed else "ExitCode : 1")
    lines.append("Result   : PASS" if passed else "Result   : FAIL")
    canonical_report_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    canonical_text = _read_text(canonical_report_path)
    has_apply = "PATCHOPS APPLY EVIDENCE" in canonical_text and ("PATCHOPS APPLY" in canonical_text) and ("Result" in canonical_text)
    has_browser = "BROWSER LIVE PROOF SUMMARY" in canonical_text and "chatgpt_submit_performed" in canonical_text
    has_probe = "post_scan_completed" in canonical_text and "upload_submit_idle_result" in canonical_text
    return has_apply, has_browser, has_probe, canonical_report_path.stat().st_size


def run_canonical_browser_evidence_report(
    output_dir: Path,
    inner_patchops_report_path: Path,
    operator_report_path: Path,
    canonical_report_path: Path,
    short_upload_dir: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    observe_seconds: int,
    probe_seconds: int,
) -> CanonicalBrowserEvidenceReportResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "l26_12y_canonical_browser_evidence_report_result.json"
    live_report_path = output_dir / "l26_12y_canonical_browser_evidence_report_live_report.txt"
    state: dict[str, object] = {}
    try:
        upstream: GeneratedArtifactCandidateDiffResult = run_generated_candidate_diff_filter(
            output_dir / "generated_candidate_diff",
            inner_patchops_report_path,
            operator_report_path,
            short_upload_dir,
            allow_report_upload,
            allow_chatgpt_submit,
            observe_seconds,
            probe_seconds,
        )
        up = upstream.to_payload()
        has_apply, has_browser, has_probe, size = _build_canonical_report(canonical_report_path, inner_patchops_report_path, up)
        state.update({
            "canonical_report_created": canonical_report_path.exists(),
            "canonical_report_path": str(canonical_report_path),
            "canonical_report_size_bytes": int(size),
            "canonical_contains_patchops_apply_evidence": has_apply,
            "canonical_contains_browser_live_evidence": has_browser,
            "canonical_contains_upload_submit_probe_evidence": has_probe,
            "canonical_uploaded_this_run": False,
            "uploaded_report_role_this_run": "inner_patchops_apply_report_short_safe_copy",
            "uploaded_report_count": int(up.get("uploaded_report_count") or 0),
            "uploaded_safe_copy_hash_matches_inner_report": bool(up.get("uploaded_safe_copy_hash_matches_inner_report")),
            "upload_submit_idle_result": str(up.get("upload_submit_idle_result") or "FAIL"),
            "chatgpt_submit_performed": bool(up.get("chatgpt_submit_performed")),
            "ready_for_next_probe": bool(up.get("ready_for_next_probe")),
            "post_scan_completed": bool(up.get("post_scan_completed")),
            "novel_candidate_count": int(up.get("novel_candidate_count") or 0),
            "baseline_candidate_count": int(up.get("baseline_candidate_count") or 0),
            "post_candidate_count": int(up.get("post_candidate_count") or 0),
            "candidate_click_performed": bool(up.get("candidate_click_performed")),
            "download_click_performed": bool(up.get("download_click_performed")),
            "generated_file_click_performed": bool(up.get("generated_file_click_performed")),
            "conversation_text_logged": bool(up.get("conversation_text_logged")),
            "full_conversation_text_logged": bool(up.get("full_conversation_text_logged")),
            "prompt_text_logged": bool(up.get("prompt_text_logged")),
            "file_content_logged": bool(up.get("file_content_logged")),
            "run_package_invoked": bool(up.get("run_package_invoked")),
            "webdriver_used": bool(up.get("webdriver_used")),
            "selenium_imported": bool(up.get("selenium_imported")),
            "cloudflare_bypass_attempted": bool(up.get("cloudflare_bypass_attempted")),
            "browser_dom_automation_used": bool(up.get("browser_dom_automation_used")),
        })
        ok = up.get("result") == "PASS" and has_apply and has_browser and has_probe and size > 0
        state.update({"result": "PASS" if ok else "FAIL", "failure_layer": "" if ok else "canonical_browser_evidence_report", "error": "" if ok else "Canonical report did not include required PatchOps apply and browser/live evidence."})
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "canonical_browser_evidence_report", "error": f"{type(exc).__name__}: {exc}"})
    result = CanonicalBrowserEvidenceReportResult(**state)
    _write_json(json_path, result)
    _write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: CanonicalBrowserEvidenceReportResult) -> None:
    p = result.to_payload()
    true_keys = [
        "canonical_report_created", "canonical_contains_patchops_apply_evidence", "canonical_contains_browser_live_evidence",
        "canonical_contains_upload_submit_probe_evidence", "uploaded_safe_copy_hash_matches_inner_report", "chatgpt_submit_performed",
        "ready_for_next_probe", "post_scan_completed",
    ]
    false_keys = [
        "canonical_uploaded_this_run", "candidate_click_performed", "download_click_performed", "generated_file_click_performed",
        "conversation_text_logged", "full_conversation_text_logged", "prompt_text_logged", "file_content_logged",
        "run_package_invoked", "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if p.get("uploaded_report_role_this_run") != "inner_patchops_apply_report_short_safe_copy":
        missing.append("uploaded_report_role_this_run_inner_short_safe_copy")
    if int(p.get("uploaded_report_count") or 0) != 1:
        missing.append("uploaded_report_count_1")
    if int(p.get("canonical_report_size_bytes") or 0) <= 0:
        missing.append("canonical_report_size_positive")
    if not p.get("canonical_report_path"):
        missing.append("canonical_report_path_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.12Y acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
