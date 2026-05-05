from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.edge_rpa.edge_l26_14d_visible_attachment_upload_gate_repair import (
    VisibleAttachmentUploadGateRepairResult,
    run_visible_attachment_upload_gate_repair,
)

PATCH_NAME = "l26_14e_picker_remembered_directory_bridge"


@dataclass(frozen=True)
class PickerRememberedDirectoryBridgeResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    upload_bridge_dir_used: bool = False
    upload_bridge_dir_path: str = ""
    uploaded_safe_copy_parent_matches_bridge: bool = False
    visible_attachment_gate_passed: bool = False
    attachment_visible_before_submit: bool = False
    attachment_signal_count_before_submit: int = 0
    picker_confirmed_upload_accepted: bool = False
    chatgpt_submit_performed: bool = False
    submit_method: str = ""
    idle_observation_completed: bool = False
    ready_for_next_probe: bool = False
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


def write_json(path: Path, result: PickerRememberedDirectoryBridgeResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: PickerRememberedDirectoryBridgeResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def run_picker_remembered_directory_bridge(
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
) -> PickerRememberedDirectoryBridgeResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14e_picker_remembered_directory_bridge_result.json"
    live_report_path = short_live_root / "l26_14e_picker_remembered_directory_bridge_live_report.txt"
    state: dict[str, object] = {"upload_bridge_dir_used": True, "upload_bridge_dir_path": str(upload_bridge_dir)}
    try:
        bridge = upload_bridge_dir.resolve()
        bridge.mkdir(parents=True, exist_ok=True)
        upstream: VisibleAttachmentUploadGateRepairResult = run_visible_attachment_upload_gate_repair(
            short_live_root / "d",
            latest_canonical_path,
            operator_report_path,
            inner_patchops_report_path,
            bridge,
            current_canonical_report_path,
            allow_report_upload,
            allow_chatgpt_submit,
            observe_seconds,
            probe_seconds,
            stability_delay_seconds,
            attachment_verify_seconds,
        )
        p = upstream.to_payload()
        uploaded_path = Path(str(p.get("uploaded_safe_copy_path") or ""))
        parent_matches = bool(str(uploaded_path.parent.resolve()).lower() == str(bridge).lower()) if uploaded_path else False
        state.update({
            "uploaded_safe_copy_parent_matches_bridge": parent_matches,
            "visible_attachment_gate_passed": bool(p.get("visible_attachment_gate_passed")),
            "attachment_visible_before_submit": bool(p.get("attachment_visible_before_submit")),
            "attachment_signal_count_before_submit": int(p.get("attachment_signal_count_before_submit") or 0),
            "picker_confirmed_upload_accepted": bool(p.get("picker_confirmed_upload_accepted")),
            "chatgpt_submit_performed": bool(p.get("chatgpt_submit_performed")),
            "submit_method": str(p.get("submit_method") or ""),
            "idle_observation_completed": bool(p.get("idle_observation_completed")),
            "ready_for_next_probe": bool(p.get("ready_for_next_probe")),
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
        ok = p.get("result") == "PASS" and parent_matches and bool(state["visible_attachment_gate_passed"])
        state.update({"result": "PASS" if ok else "FAIL", "failure_layer": "" if ok else "picker_remembered_directory_bridge", "error": "" if ok else f"Bridge failed; upstream_result={p.get('result')}; upstream_error={p.get('error')}; parent_matches={parent_matches}"})
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "picker_remembered_directory_bridge", "error": f"{type(exc).__name__}: {exc}"})
    result = PickerRememberedDirectoryBridgeResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: PickerRememberedDirectoryBridgeResult) -> None:
    p = result.to_payload()
    true_keys = [
        "upload_bridge_dir_used", "uploaded_safe_copy_parent_matches_bridge", "visible_attachment_gate_passed",
        "attachment_visible_before_submit", "picker_confirmed_upload_accepted", "chatgpt_submit_performed",
        "idle_observation_completed", "ready_for_next_probe", "selector_completed", "candidate_selected",
    ]
    false_keys = [
        "selected_candidate_click_performed", "candidate_click_performed", "download_click_performed", "generated_file_click_performed",
        "conversation_text_logged", "full_conversation_text_logged", "prompt_text_logged", "file_content_logged",
        "run_package_invoked", "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if int(p.get("attachment_signal_count_before_submit") or 0) <= 0:
        missing.append("attachment_signal_count_before_submit_positive")
    for key in ("upload_bridge_dir_path", "selected_candidate_kind", "selected_candidate_fingerprint", "selected_candidate_rect_hash"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14E acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
