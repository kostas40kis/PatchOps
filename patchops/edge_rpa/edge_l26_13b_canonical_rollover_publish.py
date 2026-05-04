from __future__ import annotations

import hashlib
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.edge_rpa.edge_l26_13a_canonical_report_upload_target_smoke import CanonicalReportUploadTargetSmokeResult, run_canonical_report_upload_target_smoke

PATCH_NAME = "l26_13b_canonical_rollover_publish"


@dataclass(frozen=True)
class CanonicalRolloverPublishResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    previous_canonical_uploaded: bool = False
    previous_canonical_source_path: str = ""
    previous_canonical_source_hash: str = ""
    uploaded_report_role: str = ""
    uploaded_report_count: int = 0
    current_canonical_report_created: bool = False
    current_canonical_report_path: str = ""
    current_canonical_report_size_bytes: int = 0
    current_canonical_contains_apply_evidence: bool = False
    current_canonical_contains_browser_evidence: bool = False
    current_canonical_uploaded_this_run: bool = False
    latest_canonical_pointer_created: bool = False
    latest_canonical_path: str = ""
    latest_canonical_matches_current: bool = False
    chatgpt_submit_performed: bool = False
    ready_for_next_probe: bool = False
    operator_report_uploaded: bool = False
    raw_apply_report_uploaded_as_browser_target: bool = False
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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_json(path: Path, result: CanonicalRolloverPublishResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: CanonicalRolloverPublishResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def build_current_canonical_report(canonical_path: Path, inner_patchops_report_path: Path, live_payload: dict[str, object], previous_canonical: Path) -> tuple[bool, bool, int]:
    inner_text = read_text(inner_patchops_report_path)
    lines: list[str] = []
    lines.append("PATCHOPS CANONICAL BROWSER EVIDENCE REPORT")
    lines.append("==========================================")
    lines.append(f"Patch: {PATCH_NAME}")
    lines.append(f"InnerPatchOpsReportPath: {inner_patchops_report_path}")
    lines.append(f"PreviousCanonicalUploadedThisRun: {previous_canonical}")
    lines.append("")
    lines.append("CANONICAL ROLLOVER NOTE")
    lines.append("=======================")
    lines.append("This run uploaded the previous accepted canonical browser-evidence report as the single browser target.")
    lines.append("This current canonical report was created after the browser live proof completed and is published for the next run.")
    lines.append("CurrentCanonicalUploadedThisRun: false")
    lines.append("UploadedReportRoleThisRun: canonical_browser_evidence_report")
    lines.append("")
    lines.append("PATCHOPS APPLY EVIDENCE")
    lines.append("=======================")
    lines.append(inner_text.rstrip())
    lines.append("")
    lines.append("BROWSER LIVE PROOF SUMMARY")
    lines.append("==========================")
    for key in [
        "result", "uploaded_report_role", "uploaded_report_count", "canonical_source_is_canonical_report",
        "canonical_source_contains_apply_evidence", "canonical_source_contains_browser_evidence", "picker_confirmed_upload_accepted",
        "chatgpt_submit_performed", "submit_method", "idle_observation_completed", "ready_for_next_probe",
        "operator_report_uploaded", "raw_apply_report_uploaded_as_browser_target", "candidate_click_performed",
        "download_click_performed", "generated_file_click_performed", "conversation_text_logged", "prompt_text_logged",
        "file_content_logged", "run_package_invoked", "webdriver_used", "selenium_imported", "browser_dom_automation_used",
        "failure_layer", "error",
    ]:
        if key in live_payload:
            lines.append(f"{key}: {live_payload.get(key)}")
    apply_passed = "Result   : PASS" in inner_text or "Result : PASS" in inner_text
    browser_passed = live_payload.get("result") == "PASS"
    lines.append("")
    lines.append("FINAL CANONICAL CHECKLIST")
    lines.append("=========================")
    lines.append(f"patchops_apply_passed: {apply_passed}")
    lines.append(f"browser_live_passed: {browser_passed}")
    lines.append(f"previous_canonical_uploaded: {live_payload.get('uploaded_report_role') == 'canonical_browser_evidence_report'}")
    lines.append(f"current_canonical_uploaded_this_run: false")
    lines.append(f"no_candidate_or_download_clicks: {not bool(live_payload.get('candidate_click_performed')) and not bool(live_payload.get('download_click_performed')) and not bool(live_payload.get('generated_file_click_performed'))}")
    lines.append(f"no_content_logging: {not bool(live_payload.get('conversation_text_logged')) and not bool(live_payload.get('prompt_text_logged')) and not bool(live_payload.get('file_content_logged'))}")
    lines.append("")
    lines.append("RESULT")
    lines.append("======")
    passed = apply_passed and browser_passed
    lines.append("ExitCode : 0" if passed else "ExitCode : 1")
    lines.append("Result   : PASS" if passed else "Result   : FAIL")
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    text = read_text(canonical_path)
    has_apply = "PATCHOPS APPLY EVIDENCE" in text and "PATCHOPS APPLY" in text and "Result" in text
    has_browser = "BROWSER LIVE PROOF SUMMARY" in text and "chatgpt_submit_performed" in text and "previous_canonical_uploaded" in text
    return has_apply, has_browser, canonical_path.stat().st_size


def run_canonical_rollover_publish(
    short_live_root: Path,
    previous_canonical_upload_source_path: Path,
    operator_report_path: Path,
    inner_patchops_report_path: Path,
    short_upload_dir: Path,
    current_canonical_report_path: Path,
    latest_canonical_path: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    observe_seconds: int,
) -> CanonicalRolloverPublishResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_13b_canonical_rollover_publish_result.json"
    live_report_path = short_live_root / "l26_13b_canonical_rollover_publish_live_report.txt"
    state: dict[str, object] = {}
    try:
        previous = previous_canonical_upload_source_path.resolve()
        upload_root = short_live_root / "u"
        upload: CanonicalReportUploadTargetSmokeResult = run_canonical_report_upload_target_smoke(
            upload_root,
            previous,
            operator_report_path,
            inner_patchops_report_path,
            short_upload_dir,
            allow_report_upload,
            allow_chatgpt_submit,
            observe_seconds,
        )
        p = upload.to_payload()
        has_apply, has_browser, size = build_current_canonical_report(current_canonical_report_path, inner_patchops_report_path, p, previous)
        latest_canonical_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(current_canonical_report_path, latest_canonical_path)
        latest_matches = hash_file(current_canonical_report_path) == hash_file(latest_canonical_path)
        state.update({
            "previous_canonical_uploaded": p.get("result") == "PASS" and p.get("uploaded_report_role") == "canonical_browser_evidence_report",
            "previous_canonical_source_path": str(previous),
            "previous_canonical_source_hash": hash_file(previous),
            "uploaded_report_role": str(p.get("uploaded_report_role") or ""),
            "uploaded_report_count": int(p.get("uploaded_report_count") or 0),
            "current_canonical_report_created": current_canonical_report_path.exists(),
            "current_canonical_report_path": str(current_canonical_report_path),
            "current_canonical_report_size_bytes": int(size),
            "current_canonical_contains_apply_evidence": has_apply,
            "current_canonical_contains_browser_evidence": has_browser,
            "current_canonical_uploaded_this_run": False,
            "latest_canonical_pointer_created": latest_canonical_path.exists(),
            "latest_canonical_path": str(latest_canonical_path),
            "latest_canonical_matches_current": latest_matches,
            "chatgpt_submit_performed": bool(p.get("chatgpt_submit_performed")),
            "ready_for_next_probe": bool(p.get("ready_for_next_probe")),
            "operator_report_uploaded": bool(p.get("operator_report_uploaded")),
            "raw_apply_report_uploaded_as_browser_target": bool(p.get("raw_apply_report_uploaded_as_browser_target")),
            "conversation_text_logged": bool(p.get("conversation_text_logged")),
            "full_conversation_text_logged": bool(p.get("full_conversation_text_logged")),
            "prompt_text_logged": bool(p.get("prompt_text_logged")),
            "file_content_logged": bool(p.get("file_content_logged")),
            "download_click_performed": bool(p.get("download_click_performed")),
            "generated_file_click_performed": bool(p.get("generated_file_click_performed")),
            "candidate_click_performed": bool(p.get("candidate_click_performed")),
            "run_package_invoked": bool(p.get("run_package_invoked")),
            "webdriver_used": bool(p.get("webdriver_used")),
            "selenium_imported": bool(p.get("selenium_imported")),
            "cloudflare_bypass_attempted": bool(p.get("cloudflare_bypass_attempted")),
            "browser_dom_automation_used": bool(p.get("browser_dom_automation_used")),
        })
        ok = bool(state["previous_canonical_uploaded"]) and has_apply and has_browser and latest_matches
        state.update({"result": "PASS" if ok else "FAIL", "failure_layer": "" if ok else "canonical_rollover_publish", "error": "" if ok else f"Rollover failed; upload_result={p.get('result')}; upload_error={p.get('error')}"})
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "canonical_rollover_publish", "error": f"{type(exc).__name__}: {exc}"})
    result = CanonicalRolloverPublishResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: CanonicalRolloverPublishResult) -> None:
    p = result.to_payload()
    true_keys = [
        "previous_canonical_uploaded", "current_canonical_report_created", "current_canonical_contains_apply_evidence",
        "current_canonical_contains_browser_evidence", "latest_canonical_pointer_created", "latest_canonical_matches_current",
        "chatgpt_submit_performed", "ready_for_next_probe",
    ]
    false_keys = [
        "current_canonical_uploaded_this_run", "operator_report_uploaded", "raw_apply_report_uploaded_as_browser_target",
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
    for key in ("previous_canonical_source_path", "current_canonical_report_path", "latest_canonical_path", "previous_canonical_source_hash"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if int(p.get("current_canonical_report_size_bytes") or 0) <= 0:
        missing.append("current_canonical_report_size_positive")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.13B acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
