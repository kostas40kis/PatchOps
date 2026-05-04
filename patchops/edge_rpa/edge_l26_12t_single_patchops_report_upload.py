from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.edge_rpa.edge_l26_12s_post_submit_idle_observer import PostSubmitIdleObserverResult, run_post_submit_idle_observer

PATCH_NAME = "l26_12t_single_patchops_report_upload"


@dataclass(frozen=True)
class SinglePatchOpsReportUploadResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    uploaded_report_role: str = ""
    uploaded_report_count: int = 0
    uploaded_report_path_matches_inner_patchops_report: bool = False
    operator_report_uploaded: bool = False
    inner_patchops_report_exists: bool = False
    inner_patchops_report_hash: str = ""
    inner_patchops_report_size_bytes: int = 0
    submit_result: str = "FAIL"
    picker_confirmed_upload_accepted: bool = False
    chatgpt_submit_performed: bool = False
    submit_method: str = ""
    idle_observation_completed: bool = False
    ready_for_next_probe: bool = False
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    prompt_text_logged: bool = False
    file_content_logged: bool = False
    download_click_performed: bool = False
    generated_file_click_performed: bool = False
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


def write_json(path: Path, result: SinglePatchOpsReportUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: SinglePatchOpsReportUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def run_single_patchops_report_upload(
    output_dir: Path,
    inner_patchops_report_path: Path,
    operator_report_path: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    observe_seconds: int,
) -> SinglePatchOpsReportUploadResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "l26_12t_single_patchops_report_upload_result.json"
    live_report_path = output_dir / "l26_12t_single_patchops_report_upload_live_report.txt"
    state: dict[str, object] = {}
    try:
        inner = inner_patchops_report_path.resolve()
        operator = operator_report_path.resolve()
        if not inner.exists() or not inner.is_file():
            raise RuntimeError(f"Inner PatchOps report does not exist: {inner}")
        if inner == operator:
            raise RuntimeError("Inner PatchOps report and operator report must be different files for the single-upload proof.")
        state.update({
            "uploaded_report_role": "inner_patchops_apply_report",
            "uploaded_report_count": 1,
            "uploaded_report_path_matches_inner_patchops_report": True,
            "operator_report_uploaded": False,
            "inner_patchops_report_exists": True,
            "inner_patchops_report_hash": hash_file(inner),
            "inner_patchops_report_size_bytes": int(inner.stat().st_size),
        })
        # Important: pass the inner PatchOps report as the upload target. The local operator report is not uploaded.
        observed: PostSubmitIdleObserverResult = run_post_submit_idle_observer(
            output_dir / "upload_submit_idle_proof",
            inner,
            allow_report_upload,
            allow_chatgpt_submit,
            observe_seconds,
        )
        p = observed.to_payload()
        ok = p.get("result") == "PASS" and bool(p.get("ready_for_next_probe"))
        state.update({
            "submit_result": str(p.get("submit_result") or "FAIL"),
            "picker_confirmed_upload_accepted": bool(p.get("picker_confirmed_upload_accepted")),
            "chatgpt_submit_performed": bool(p.get("chatgpt_submit_performed")),
            "submit_method": str(p.get("submit_method") or ""),
            "idle_observation_completed": bool(p.get("idle_observation_completed")),
            "ready_for_next_probe": bool(p.get("ready_for_next_probe")),
            "conversation_text_logged": bool(p.get("conversation_text_logged")),
            "full_conversation_text_logged": bool(p.get("full_conversation_text_logged")),
            "prompt_text_logged": bool(p.get("prompt_text_logged")),
            "file_content_logged": bool(p.get("file_content_logged")),
            "download_click_performed": bool(p.get("download_click_performed")),
            "generated_file_click_performed": bool(p.get("generated_file_click_performed")),
            "run_package_invoked": bool(p.get("run_package_invoked")),
            "webdriver_used": bool(p.get("webdriver_used")),
            "selenium_imported": bool(p.get("selenium_imported")),
            "cloudflare_bypass_attempted": bool(p.get("cloudflare_bypass_attempted")),
            "browser_dom_automation_used": bool(p.get("browser_dom_automation_used")),
            "result": "PASS" if ok else "FAIL",
            "failure_layer": "" if ok else "single_patchops_report_upload_observation",
            "error": "" if ok else f"Upload/submit/idle proof did not pass; observed_result={p.get('result')}; observed_error={p.get('error')}",
        })
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "single_patchops_report_upload", "error": f"{type(exc).__name__}: {exc}"})
    result = SinglePatchOpsReportUploadResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: SinglePatchOpsReportUploadResult) -> None:
    p = result.to_payload()
    true_keys = [
        "uploaded_report_path_matches_inner_patchops_report",
        "inner_patchops_report_exists",
        "picker_confirmed_upload_accepted",
        "chatgpt_submit_performed",
        "idle_observation_completed",
        "ready_for_next_probe",
    ]
    false_keys = [
        "operator_report_uploaded", "conversation_text_logged", "full_conversation_text_logged", "prompt_text_logged",
        "file_content_logged", "download_click_performed", "generated_file_click_performed", "run_package_invoked",
        "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if p.get("uploaded_report_role") != "inner_patchops_apply_report":
        missing.append("uploaded_report_role_inner_patchops_apply_report")
    if int(p.get("uploaded_report_count") or 0) != 1:
        missing.append("uploaded_report_count_1")
    for k in ("inner_patchops_report_hash", "submit_method"):
        if not p.get(k):
            missing.append(k + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.12T acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
