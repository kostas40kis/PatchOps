from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import pywinauto  # type: ignore

from patchops.edge_rpa.edge_l26_12u_short_safe_inner_patchops_report_upload import ShortSafeInnerReportUploadResult, run_short_safe_inner_report_upload
from patchops.edge_rpa.edge_upload_safe_report_copy_gate import _hash_text, _info_text
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_12w_actionable_artifact_candidate_inventory"


@dataclass(frozen=True)
class ActionableArtifactInventoryResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    upload_submit_idle_result: str = "FAIL"
    uploaded_report_count: int = 0
    uploaded_safe_copy_hash_matches_inner_report: bool = False
    chatgpt_submit_performed: bool = False
    ready_for_next_probe: bool = False
    inventory_started: bool = False
    inventory_completed: bool = False
    edge_window_found_for_inventory: bool = False
    scanned_control_count: int = 0
    artifact_candidate_count: int = 0
    actionable_candidate_count: int = 0
    clickable_candidate_count: int = 0
    visible_candidate_count: int = 0
    enabled_candidate_count: int = 0
    download_like_candidate_count: int = 0
    zip_like_candidate_count: int = 0
    file_like_candidate_count: int = 0
    link_like_candidate_count: int = 0
    candidate_fingerprints_recorded: bool = False
    candidate_fingerprints: list[str] = field(default_factory=list)
    candidate_rect_hashes_recorded: bool = False
    candidate_rect_hashes: list[str] = field(default_factory=list)
    candidate_control_types_recorded: bool = False
    candidate_control_types: list[str] = field(default_factory=list)
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


def write_json(path: Path, result: ActionableArtifactInventoryResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: ActionableArtifactInventoryResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = result.to_payload()
    safe_lines: list[str] = []
    for key, value in payload.items():
        if isinstance(value, list):
            safe_lines.append(f"{key}: {','.join(str(item) for item in value)}")
        else:
            safe_lines.append(f"{key}: {value}")
    path.write_text("\n".join(safe_lines) + "\n", encoding="utf-8")


def _kind(control_type: str, name: str, automation_id: str, class_name: str) -> tuple[bool, bool, bool, bool, bool]:
    text = " ".join([control_type or "", name or "", automation_id or "", class_name or ""]).lower()
    download_like = "download" in text or "save" in text
    zip_like = ".zip" in text or " zip" in text or "archive" in text
    file_like = "file" in text or "attachment" in text or ".txt" in text or ".md" in text or ".json" in text or ".zip" in text
    link_like = control_type in {"Hyperlink", "Button"} and (download_like or zip_like or file_like or "sandbox" in text)
    artifact = download_like or zip_like or file_like or link_like
    return artifact, download_like, zip_like, file_like, link_like


def _safe_rect(control: object) -> tuple[int, int, int, int, int, int, bool]:
    try:
        r = control.rectangle()
        left = int(r.left)
        top = int(r.top)
        width = int(r.width())
        height = int(r.height())
        center_x = left + max(0, width // 2)
        center_y = top + max(0, height // 2)
        on_screen = width > 0 and height > 0 and center_x >= 0 and center_y >= 0
        return left, top, width, height, center_x, center_y, on_screen
    except Exception:
        return 0, 0, 0, 0, 0, 0, False


def _control_flags(control: object) -> tuple[bool, bool, bool]:
    visible = enabled = clickable = False
    try:
        visible = bool(control.is_visible())
    except Exception:
        visible = False
    try:
        enabled = bool(control.is_enabled())
    except Exception:
        enabled = False
    try:
        clickable = bool(visible and enabled and control.friendly_class_name())
    except Exception:
        clickable = bool(visible and enabled)
    return visible, enabled, clickable


def inventory_artifact_candidates(probe_seconds: int) -> dict[str, object]:
    deadline = time.time() + max(5, min(int(probe_seconds), 120))
    fingerprints: list[str] = []
    rect_hashes: list[str] = []
    control_types: list[str] = []
    seen: set[str] = set()
    total_scanned = 0
    artifact_count = actionable_count = clickable_count = visible_count = enabled_count = 0
    download_count = zip_count = file_count = link_count = 0
    edge_found = False
    while time.time() < deadline:
        desktop = pywinauto.Desktop(backend="uia")
        _windows, wrappers = discover_edge_windows(desktop, edge_process_ids())
        wrappers = list(wrappers or [])
        edge_found = edge_found or bool(wrappers)
        for window in wrappers[:3]:
            queue: list[tuple[object, int]] = [(window, 0)]
            local_scanned = 0
            while queue and local_scanned < 3500:
                control, depth = queue.pop(0)
                local_scanned += 1
                total_scanned += 1
                try:
                    info = control.element_info
                    control_type = _info_text(info, "control_type")
                    name = _info_text(info, "name")
                    automation_id = _info_text(info, "automation_id")
                    class_name = _info_text(info, "class_name")
                except Exception:
                    control_type = name = automation_id = class_name = ""
                artifact, download_like, zip_like, file_like, link_like = _kind(control_type, name, automation_id, class_name)
                if artifact:
                    left, top, width, height, center_x, center_y, on_screen = _safe_rect(control)
                    visible, enabled, clickable = _control_flags(control)
                    fp = _hash_text("|".join([control_type or "", name or "", automation_id or "", class_name or ""]))
                    rect_hash = _hash_text(f"{left},{top},{width},{height},{center_x},{center_y},{on_screen}")
                    if fp not in seen:
                        seen.add(fp)
                        artifact_count += 1
                        if on_screen and width > 2 and height > 2:
                            actionable_count += 1
                        if clickable:
                            clickable_count += 1
                        if visible:
                            visible_count += 1
                        if enabled:
                            enabled_count += 1
                        if download_like: download_count += 1
                        if zip_like: zip_count += 1
                        if file_like: file_count += 1
                        if link_like: link_count += 1
                        if len(fingerprints) < 12:
                            fingerprints.append(fp)
                            rect_hashes.append(rect_hash)
                            control_types.append(control_type or "unknown")
                if depth < 9:
                    try:
                        for child in list(control.children())[:100]:
                            queue.append((child, depth + 1))
                    except Exception:
                        pass
        time.sleep(2.0)
    return {
        "edge_window_found_for_inventory": edge_found,
        "scanned_control_count": total_scanned,
        "artifact_candidate_count": artifact_count,
        "actionable_candidate_count": actionable_count,
        "clickable_candidate_count": clickable_count,
        "visible_candidate_count": visible_count,
        "enabled_candidate_count": enabled_count,
        "download_like_candidate_count": download_count,
        "zip_like_candidate_count": zip_count,
        "file_like_candidate_count": file_count,
        "link_like_candidate_count": link_count,
        "candidate_fingerprints_recorded": True,
        "candidate_fingerprints": fingerprints,
        "candidate_rect_hashes_recorded": True,
        "candidate_rect_hashes": rect_hashes,
        "candidate_control_types_recorded": True,
        "candidate_control_types": control_types,
    }


def run_actionable_artifact_inventory(
    output_dir: Path,
    inner_patchops_report_path: Path,
    operator_report_path: Path,
    short_upload_dir: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    observe_seconds: int,
    probe_seconds: int,
) -> ActionableArtifactInventoryResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "l26_12w_actionable_artifact_candidate_inventory_result.json"
    live_report_path = output_dir / "l26_12w_actionable_artifact_candidate_inventory_live_report.txt"
    state: dict[str, object] = {}
    try:
        upstream: ShortSafeInnerReportUploadResult = run_short_safe_inner_report_upload(
            output_dir / "single_upload_submit_idle",
            inner_patchops_report_path,
            operator_report_path,
            short_upload_dir,
            allow_report_upload,
            allow_chatgpt_submit,
            observe_seconds,
        )
        up = upstream.to_payload()
        upstream_ok = up.get("result") == "PASS" and bool(up.get("ready_for_next_probe"))
        state.update({
            "upload_submit_idle_result": str(up.get("result") or "FAIL"),
            "uploaded_report_count": int(up.get("uploaded_report_count") or 0),
            "uploaded_safe_copy_hash_matches_inner_report": bool(up.get("uploaded_safe_copy_hash_matches_inner_report")),
            "chatgpt_submit_performed": bool(up.get("chatgpt_submit_performed")),
            "ready_for_next_probe": bool(up.get("ready_for_next_probe")),
            "conversation_text_logged": bool(up.get("conversation_text_logged")),
            "full_conversation_text_logged": bool(up.get("full_conversation_text_logged")),
            "prompt_text_logged": bool(up.get("prompt_text_logged")),
            "file_content_logged": bool(up.get("file_content_logged")),
            "download_click_performed": bool(up.get("download_click_performed")),
            "generated_file_click_performed": bool(up.get("generated_file_click_performed")),
            "run_package_invoked": bool(up.get("run_package_invoked")),
            "webdriver_used": bool(up.get("webdriver_used")),
            "selenium_imported": bool(up.get("selenium_imported")),
            "cloudflare_bypass_attempted": bool(up.get("cloudflare_bypass_attempted")),
            "browser_dom_automation_used": bool(up.get("browser_dom_automation_used")),
        })
        if not upstream_ok:
            raise RuntimeError(f"Upload/submit/idle precondition failed; upstream_result={up.get('result')}; upstream_error={up.get('error')}")
        state.update({"inventory_started": True})
        inventory = inventory_artifact_candidates(probe_seconds)
        state.update(inventory)
        actionable_ok = bool(inventory.get("edge_window_found_for_inventory")) and int(inventory.get("scanned_control_count") or 0) > 0 and int(inventory.get("actionable_candidate_count") or 0) > 0
        state.update({
            "inventory_completed": True,
            "result": "PASS" if actionable_ok else "FAIL",
            "failure_layer": "" if actionable_ok else "actionable_artifact_inventory",
            "error": "" if actionable_ok else "No actionable artifact candidate was found after the accepted upload/submit/idle flow.",
        })
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "actionable_artifact_inventory", "error": f"{type(exc).__name__}: {exc}"})
    result = ActionableArtifactInventoryResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: ActionableArtifactInventoryResult) -> None:
    p = result.to_payload()
    true_keys = [
        "uploaded_safe_copy_hash_matches_inner_report", "chatgpt_submit_performed", "ready_for_next_probe",
        "inventory_started", "inventory_completed", "edge_window_found_for_inventory",
        "candidate_fingerprints_recorded", "candidate_rect_hashes_recorded", "candidate_control_types_recorded",
    ]
    false_keys = [
        "conversation_text_logged", "full_conversation_text_logged", "prompt_text_logged", "file_content_logged",
        "download_click_performed", "generated_file_click_performed", "candidate_click_performed", "run_package_invoked",
        "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if int(p.get("uploaded_report_count") or 0) != 1:
        missing.append("uploaded_report_count_1")
    if int(p.get("scanned_control_count") or 0) <= 0:
        missing.append("scanned_control_count_positive")
    if int(p.get("actionable_candidate_count") or 0) <= 0:
        missing.append("actionable_candidate_count_positive")
    if int(p.get("artifact_candidate_count") or 0) <= 0:
        missing.append("artifact_candidate_count_positive")
    if not p.get("candidate_fingerprints"):
        missing.append("candidate_fingerprints_nonempty")
    if not p.get("candidate_rect_hashes"):
        missing.append("candidate_rect_hashes_nonempty")
    if not p.get("candidate_control_types"):
        missing.append("candidate_control_types_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.12W acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
