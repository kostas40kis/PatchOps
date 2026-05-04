from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.edge_rpa.edge_l26_13b_canonical_rollover_publish import CanonicalRolloverPublishResult, run_canonical_rollover_publish

PATCH_NAME = "l26_13c_stable_latest_canonical_upload_source"


@dataclass(frozen=True)
class StableLatestCanonicalUploadSourceResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    stable_latest_source_used: bool = False
    latest_canonical_source_exists: bool = False
    latest_canonical_source_path: str = ""
    latest_canonical_source_is_canonical_report: bool = False
    previous_canonical_uploaded: bool = False
    uploaded_report_role: str = ""
    uploaded_report_count: int = 0
    current_canonical_report_created: bool = False
    current_canonical_report_path: str = ""
    current_canonical_contains_apply_evidence: bool = False
    current_canonical_contains_browser_evidence: bool = False
    current_canonical_uploaded_this_run: bool = False
    latest_canonical_pointer_created: bool = False
    latest_canonical_matches_current: bool = False
    chatgpt_submit_performed: bool = False
    ready_for_next_probe: bool = False
    wildcard_source_selection_used: bool = False
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


def write_json(path: Path, result: StableLatestCanonicalUploadSourceResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: StableLatestCanonicalUploadSourceResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def _is_canonical(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return "PATCHOPS CANONICAL BROWSER EVIDENCE REPORT" in text and "BROWSER LIVE PROOF SUMMARY" in text and "PATCHOPS APPLY EVIDENCE" in text


def run_stable_latest_canonical_upload_source(
    short_live_root: Path,
    latest_canonical_path: Path,
    operator_report_path: Path,
    inner_patchops_report_path: Path,
    short_upload_dir: Path,
    current_canonical_report_path: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    observe_seconds: int,
) -> StableLatestCanonicalUploadSourceResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_13c_stable_latest_canonical_upload_source_result.json"
    live_report_path = short_live_root / "l26_13c_stable_latest_canonical_upload_source_live_report.txt"
    state: dict[str, object] = {}
    try:
        latest = latest_canonical_path.resolve()
        state.update({
            "stable_latest_source_used": True,
            "latest_canonical_source_exists": latest.exists() and latest.is_file(),
            "latest_canonical_source_path": str(latest),
            "latest_canonical_source_is_canonical_report": _is_canonical(latest),
            "wildcard_source_selection_used": False,
        })
        if not state["latest_canonical_source_exists"]:
            raise RuntimeError(f"Stable latest canonical source does not exist: {latest}")
        if not state["latest_canonical_source_is_canonical_report"]:
            raise RuntimeError(f"Stable latest canonical source is not a canonical browser evidence report: {latest}")
        upstream: CanonicalRolloverPublishResult = run_canonical_rollover_publish(
            short_live_root / "r",
            latest,
            operator_report_path,
            inner_patchops_report_path,
            short_upload_dir,
            current_canonical_report_path,
            latest,
            allow_report_upload,
            allow_chatgpt_submit,
            observe_seconds,
        )
        p = upstream.to_payload()
        state.update({
            "previous_canonical_uploaded": bool(p.get("previous_canonical_uploaded")),
            "uploaded_report_role": str(p.get("uploaded_report_role") or ""),
            "uploaded_report_count": int(p.get("uploaded_report_count") or 0),
            "current_canonical_report_created": bool(p.get("current_canonical_report_created")),
            "current_canonical_report_path": str(p.get("current_canonical_report_path") or ""),
            "current_canonical_contains_apply_evidence": bool(p.get("current_canonical_contains_apply_evidence")),
            "current_canonical_contains_browser_evidence": bool(p.get("current_canonical_contains_browser_evidence")),
            "current_canonical_uploaded_this_run": bool(p.get("current_canonical_uploaded_this_run")),
            "latest_canonical_pointer_created": bool(p.get("latest_canonical_pointer_created")),
            "latest_canonical_matches_current": bool(p.get("latest_canonical_matches_current")),
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
        ok = p.get("result") == "PASS" and bool(state["previous_canonical_uploaded"]) and bool(state["latest_canonical_matches_current"])
        state.update({"result": "PASS" if ok else "FAIL", "failure_layer": "" if ok else "stable_latest_canonical_upload_source", "error": "" if ok else f"Stable latest canonical rollover failed; upstream_result={p.get('result')}; upstream_error={p.get('error')}"})
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "stable_latest_canonical_upload_source", "error": f"{type(exc).__name__}: {exc}"})
    result = StableLatestCanonicalUploadSourceResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: StableLatestCanonicalUploadSourceResult) -> None:
    p = result.to_payload()
    true_keys = [
        "stable_latest_source_used", "latest_canonical_source_exists", "latest_canonical_source_is_canonical_report",
        "previous_canonical_uploaded", "current_canonical_report_created", "current_canonical_contains_apply_evidence",
        "current_canonical_contains_browser_evidence", "latest_canonical_pointer_created", "latest_canonical_matches_current",
        "chatgpt_submit_performed", "ready_for_next_probe",
    ]
    false_keys = [
        "wildcard_source_selection_used", "current_canonical_uploaded_this_run", "operator_report_uploaded",
        "raw_apply_report_uploaded_as_browser_target", "conversation_text_logged", "full_conversation_text_logged",
        "prompt_text_logged", "file_content_logged", "download_click_performed", "generated_file_click_performed",
        "candidate_click_performed", "run_package_invoked", "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if p.get("uploaded_report_role") != "canonical_browser_evidence_report":
        missing.append("uploaded_report_role_canonical")
    if int(p.get("uploaded_report_count") or 0) != 1:
        missing.append("uploaded_report_count_1")
    for key in ("latest_canonical_source_path", "current_canonical_report_path"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.13C acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
