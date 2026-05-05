from __future__ import annotations

import hashlib
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.edge_rpa.edge_l26_14e_picker_remembered_directory_bridge import PickerRememberedDirectoryBridgeResult, run_picker_remembered_directory_bridge

PATCH_NAME = "l26_14f_visible_gate_canonical_publish_restore"


@dataclass(frozen=True)
class VisibleGateCanonicalPublishRestoreResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    upstream_bridge_result: str = "FAIL"
    visible_attachment_gate_passed: bool = False
    attachment_visible_before_submit: bool = False
    picker_confirmed_upload_accepted: bool = False
    chatgpt_submit_performed: bool = False
    idle_observation_completed: bool = False
    ready_for_next_probe: bool = False
    uploaded_safe_copy_parent_matches_bridge: bool = False
    current_canonical_report_created: bool = False
    current_canonical_report_path: str = ""
    current_canonical_report_size_bytes: int = 0
    current_canonical_contains_apply_evidence: bool = False
    current_canonical_contains_browser_evidence: bool = False
    current_canonical_uploaded_this_run: bool = False
    latest_canonical_pointer_created: bool = False
    latest_canonical_path: str = ""
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


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_json(path: Path, result: VisibleGateCanonicalPublishRestoreResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: VisibleGateCanonicalPublishRestoreResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def build_current_canonical_report(canonical_path: Path, inner_patchops_report_path: Path, bridge_payload: dict[str, object]) -> tuple[bool, bool, int]:
    inner_text = read_text(inner_patchops_report_path)
    lines: list[str] = []
    lines.append("PATCHOPS CANONICAL BROWSER EVIDENCE REPORT")
    lines.append("==========================================")
    lines.append(f"Patch: {PATCH_NAME}")
    lines.append(f"InnerPatchOpsReportPath: {inner_patchops_report_path}")
    lines.append("")
    lines.append("CANONICAL NOTE")
    lines.append("==============")
    lines.append("This run uploaded the previous latest canonical report using the visible attachment gate and remembered-picker bridge.")
    lines.append("This current canonical report is published after the live proof and is the source for the next run.")
    lines.append("CurrentCanonicalUploadedThisRun: false")
    lines.append("")
    lines.append("PATCHOPS APPLY EVIDENCE")
    lines.append("=======================")
    lines.append(inner_text.rstrip())
    lines.append("")
    lines.append("BROWSER LIVE PROOF SUMMARY")
    lines.append("==========================")
    for key in [
        "result", "visible_attachment_gate_passed", "attachment_visible_before_submit", "picker_confirmed_upload_accepted",
        "chatgpt_submit_performed", "submit_method", "idle_observation_completed", "ready_for_next_probe",
        "uploaded_safe_copy_parent_matches_bridge", "selector_completed", "candidate_selected", "selected_candidate_kind",
        "selected_candidate_click_performed", "candidate_click_performed", "download_click_performed", "generated_file_click_performed",
        "conversation_text_logged", "prompt_text_logged", "file_content_logged", "run_package_invoked", "webdriver_used",
        "selenium_imported", "browser_dom_automation_used", "failure_layer", "error",
    ]:
        if key in bridge_payload:
            lines.append(f"{key}: {bridge_payload.get(key)}")
    apply_passed = "Result   : PASS" in inner_text or "Result : PASS" in inner_text
    browser_passed = bridge_payload.get("result") == "PASS" and bool(bridge_payload.get("visible_attachment_gate_passed"))
    lines.append("")
    lines.append("FINAL CANONICAL CHECKLIST")
    lines.append("=========================")
    lines.append(f"patchops_apply_passed: {apply_passed}")
    lines.append(f"browser_live_passed: {browser_passed}")
    lines.append(f"visible_attachment_gate_passed: {bool(bridge_payload.get('visible_attachment_gate_passed'))}")
    lines.append(f"current_canonical_uploaded_this_run: false")
    lines.append(f"no_candidate_or_download_clicks: {not bool(bridge_payload.get('candidate_click_performed')) and not bool(bridge_payload.get('download_click_performed')) and not bool(bridge_payload.get('generated_file_click_performed')) and not bool(bridge_payload.get('selected_candidate_click_performed'))}")
    lines.append(f"no_content_logging: {not bool(bridge_payload.get('conversation_text_logged')) and not bool(bridge_payload.get('prompt_text_logged')) and not bool(bridge_payload.get('file_content_logged'))}")
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
    has_browser = "BROWSER LIVE PROOF SUMMARY" in text and "visible_attachment_gate_passed: True" in text
    return has_apply, has_browser, canonical_path.stat().st_size


def run_visible_gate_canonical_publish_restore(
    short_live_root: Path,
    latest_canonical_path: Path,
    operator_report_path: Path,
    inner_patchops_report_path: Path,
    upload_bridge_dir: Path,
    current_canonical_report_path: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    observe_seconds: int,
    probe_seconds: int,
    stability_delay_seconds: int,
    attachment_verify_seconds: int,
) -> VisibleGateCanonicalPublishRestoreResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14f_visible_gate_canonical_publish_restore_result.json"
    live_report_path = short_live_root / "l26_14f_visible_gate_canonical_publish_restore_live_report.txt"
    state: dict[str, object] = {}
    try:
        upstream: PickerRememberedDirectoryBridgeResult = run_picker_remembered_directory_bridge(
            short_live_root / "e",
            latest_canonical_path,
            operator_report_path,
            inner_patchops_report_path,
            upload_bridge_dir,
            current_canonical_report_path,
            allow_report_upload,
            allow_chatgpt_submit,
            observe_seconds,
            probe_seconds,
            stability_delay_seconds,
            attachment_verify_seconds,
        )
        p = upstream.to_payload()
        state.update({
            "upstream_bridge_result": str(p.get("result") or "FAIL"),
            "visible_attachment_gate_passed": bool(p.get("visible_attachment_gate_passed")),
            "attachment_visible_before_submit": bool(p.get("attachment_visible_before_submit")),
            "picker_confirmed_upload_accepted": bool(p.get("picker_confirmed_upload_accepted")),
            "chatgpt_submit_performed": bool(p.get("chatgpt_submit_performed")),
            "idle_observation_completed": bool(p.get("idle_observation_completed")),
            "ready_for_next_probe": bool(p.get("ready_for_next_probe")),
            "uploaded_safe_copy_parent_matches_bridge": bool(p.get("uploaded_safe_copy_parent_matches_bridge")),
            "selector_completed": bool(p.get("selector_completed")),
            "candidate_selected": bool(p.get("candidate_selected")),
            "selected_candidate_kind": str(p.get("selected_candidate_kind") or ""),
            "selected_candidate_fingerprint": str(p.get("selected_candidate_fingerprint") or ""),
            "selected_candidate_rect_hash": str(p.get("selected_candidate_rect_hash") or ""),
            "selected_candidate_click_performed": bool(p.get("selected_candidate_click_performed")),
            "candidate_click_performed": bool(p.get("candidate_click_performed")),
            "download_click_performed": bool(p.get("download_click_performed")),
            "generated_file_click_performed": bool(p.get("generated_file_click_performed")),
            "conversation_text_logged": bool(p.get("conversation_text_logged")),
            "full_conversation_text_logged": bool(p.get("full_conversation_text_logged")),
            "prompt_text_logged": bool(p.get("prompt_text_logged")),
            "file_content_logged": bool(p.get("file_content_logged")),
            "run_package_invoked": bool(p.get("run_package_invoked")),
            "webdriver_used": bool(p.get("webdriver_used")),
            "selenium_imported": bool(p.get("selenium_imported")),
            "cloudflare_bypass_attempted": bool(p.get("cloudflare_bypass_attempted")),
            "browser_dom_automation_used": bool(p.get("browser_dom_automation_used")),
        })
        if p.get("result") != "PASS" or not bool(p.get("visible_attachment_gate_passed")):
            raise RuntimeError(f"Upstream visible bridge failed; result={p.get('result')}; error={p.get('error')}")
        has_apply, has_browser, size = build_current_canonical_report(current_canonical_report_path, inner_patchops_report_path, p)
        latest_canonical_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(current_canonical_report_path, latest_canonical_path)
        latest_matches = hash_file(current_canonical_report_path) == hash_file(latest_canonical_path)
        state.update({
            "current_canonical_report_created": current_canonical_report_path.exists(),
            "current_canonical_report_path": str(current_canonical_report_path),
            "current_canonical_report_size_bytes": int(size),
            "current_canonical_contains_apply_evidence": has_apply,
            "current_canonical_contains_browser_evidence": has_browser,
            "current_canonical_uploaded_this_run": False,
            "latest_canonical_pointer_created": latest_canonical_path.exists(),
            "latest_canonical_path": str(latest_canonical_path),
            "latest_canonical_matches_current": latest_matches,
        })
        ok = has_apply and has_browser and latest_matches
        state.update({"result": "PASS" if ok else "FAIL", "failure_layer": "" if ok else "visible_gate_canonical_publish_restore", "error": "" if ok else "Canonical publish restore failed after visible bridge."})
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "visible_gate_canonical_publish_restore", "error": f"{type(exc).__name__}: {exc}"})
    result = VisibleGateCanonicalPublishRestoreResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: VisibleGateCanonicalPublishRestoreResult) -> None:
    p = result.to_payload()
    true_keys = [
        "visible_attachment_gate_passed", "attachment_visible_before_submit", "picker_confirmed_upload_accepted",
        "chatgpt_submit_performed", "idle_observation_completed", "ready_for_next_probe", "uploaded_safe_copy_parent_matches_bridge",
        "current_canonical_report_created", "current_canonical_contains_apply_evidence", "current_canonical_contains_browser_evidence",
        "latest_canonical_pointer_created", "latest_canonical_matches_current", "selector_completed", "candidate_selected",
    ]
    false_keys = [
        "current_canonical_uploaded_this_run", "selected_candidate_click_performed", "candidate_click_performed", "download_click_performed",
        "generated_file_click_performed", "conversation_text_logged", "full_conversation_text_logged", "prompt_text_logged",
        "file_content_logged", "run_package_invoked", "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if p.get("upstream_bridge_result") != "PASS":
        missing.append("upstream_bridge_result_PASS")
    if int(p.get("current_canonical_report_size_bytes") or 0) <= 0:
        missing.append("current_canonical_report_size_positive")
    for key in ("current_canonical_report_path", "latest_canonical_path", "selected_candidate_kind", "selected_candidate_fingerprint", "selected_candidate_rect_hash"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14F acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
