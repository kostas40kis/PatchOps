from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import pywinauto  # type: ignore

from patchops.edge_rpa.edge_l26_13c_stable_latest_canonical_upload_source import StableLatestCanonicalUploadSourceResult, run_stable_latest_canonical_upload_source
from patchops.edge_rpa.edge_upload_safe_report_copy_gate import _hash_text, _info_text
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_14a_stable_canonical_response_readiness_probe"


@dataclass(frozen=True)
class StableCanonicalResponseReadinessProbeResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    canonical_cycle_result: str = "FAIL"
    stable_latest_source_used: bool = False
    previous_canonical_uploaded: bool = False
    uploaded_report_role: str = ""
    uploaded_report_count: int = 0
    current_canonical_report_created: bool = False
    latest_canonical_matches_current: bool = False
    chatgpt_submit_performed: bool = False
    ready_for_next_probe: bool = False
    response_readiness_probe_started: bool = False
    response_readiness_probe_completed: bool = False
    edge_window_found_for_probe: bool = False
    scanned_control_count: int = 0
    response_like_candidate_count: int = 0
    action_button_candidate_count: int = 0
    copy_like_candidate_count: int = 0
    regenerate_like_candidate_count: int = 0
    composer_like_candidate_count: int = 0
    stop_generating_seen: bool = False
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


def write_json(path: Path, result: StableCanonicalResponseReadinessProbeResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: StableCanonicalResponseReadinessProbeResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = result.to_payload()
    lines: list[str] = []
    for key, value in payload.items():
        if isinstance(value, list):
            lines.append(f"{key}: {','.join(str(item) for item in value)}")
        else:
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _safe_rect_hash(control: object) -> str:
    try:
        r = control.rectangle()
        left = int(r.left)
        top = int(r.top)
        width = int(r.width())
        height = int(r.height())
        center_x = left + max(0, width // 2)
        center_y = top + max(0, height // 2)
        return _hash_text(f"{left},{top},{width},{height},{center_x},{center_y}")
    except Exception:
        return _hash_text("rect-error")


def _classify(control_type: str, name: str, automation_id: str, class_name: str) -> dict[str, bool]:
    # These labels are used only for classification and then discarded. They are never written to reports.
    text = " ".join([control_type or "", name or "", automation_id or "", class_name or ""]).lower()
    stop = "stop generating" in text or "stop streaming" in text
    copy_like = "copy" in text or "clipboard" in text
    regenerate_like = "regenerate" in text or "try again" in text
    composer_like = "message" in text or "prompt" in text or "textbox" in text or "edit" in text or "composer" in text
    response_like = copy_like or regenerate_like or "read aloud" in text or "thumb" in text or "rating" in text or "assistant" in text
    action_button = control_type in {"Button", "SplitButton", "MenuItem", "Hyperlink"} and (copy_like or regenerate_like or response_like or stop)
    return {"stop": stop, "copy": copy_like, "regenerate": regenerate_like, "composer": composer_like, "response": response_like, "action": action_button}


def probe_response_readiness(probe_seconds: int) -> dict[str, object]:
    deadline = time.time() + max(5, min(int(probe_seconds), 120))
    seen: set[str] = set()
    fingerprints: list[str] = []
    rect_hashes: list[str] = []
    control_types: list[str] = []
    scanned = 0
    edge_found = False
    response_count = action_count = copy_count = regenerate_count = composer_count = 0
    stop_seen = False
    while time.time() < deadline:
        desktop = pywinauto.Desktop(backend="uia")
        _windows, wrappers = discover_edge_windows(desktop, edge_process_ids())
        wrappers = list(wrappers or [])
        edge_found = edge_found or bool(wrappers)
        for window in wrappers[:3]:
            queue: list[tuple[object, int]] = [(window, 0)]
            local = 0
            while queue and local < 4000:
                control, depth = queue.pop(0)
                local += 1
                scanned += 1
                try:
                    info = control.element_info
                    control_type = _info_text(info, "control_type")
                    name = _info_text(info, "name")
                    automation_id = _info_text(info, "automation_id")
                    class_name = _info_text(info, "class_name")
                except Exception:
                    control_type = name = automation_id = class_name = ""
                c = _classify(control_type, name, automation_id, class_name)
                if c["stop"]:
                    stop_seen = True
                if c["response"] or c["action"] or c["composer"] or c["stop"]:
                    fp = _hash_text("|".join([control_type or "", name or "", automation_id or "", class_name or ""]))
                    if fp not in seen:
                        seen.add(fp)
                        if c["response"]: response_count += 1
                        if c["action"]: action_count += 1
                        if c["copy"]: copy_count += 1
                        if c["regenerate"]: regenerate_count += 1
                        if c["composer"]: composer_count += 1
                        if len(fingerprints) < 16:
                            fingerprints.append(fp)
                            rect_hashes.append(_safe_rect_hash(control))
                            control_types.append(control_type or "unknown")
                if depth < 9:
                    try:
                        for child in list(control.children())[:100]:
                            queue.append((child, depth + 1))
                    except Exception:
                        pass
        time.sleep(1.0)
    return {
        "edge_window_found_for_probe": edge_found,
        "scanned_control_count": scanned,
        "response_like_candidate_count": response_count,
        "action_button_candidate_count": action_count,
        "copy_like_candidate_count": copy_count,
        "regenerate_like_candidate_count": regenerate_count,
        "composer_like_candidate_count": composer_count,
        "stop_generating_seen": stop_seen,
        "candidate_fingerprints_recorded": True,
        "candidate_fingerprints": fingerprints,
        "candidate_rect_hashes_recorded": True,
        "candidate_rect_hashes": rect_hashes,
        "candidate_control_types_recorded": True,
        "candidate_control_types": control_types,
    }


def run_stable_canonical_response_readiness_probe(
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
) -> StableCanonicalResponseReadinessProbeResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14a_stable_canonical_response_readiness_probe_result.json"
    live_report_path = short_live_root / "l26_14a_stable_canonical_response_readiness_probe_live_report.txt"
    state: dict[str, object] = {}
    try:
        upstream: StableLatestCanonicalUploadSourceResult = run_stable_latest_canonical_upload_source(
            short_live_root / "c",
            latest_canonical_path,
            operator_report_path,
            inner_patchops_report_path,
            short_upload_dir,
            current_canonical_report_path,
            allow_report_upload,
            allow_chatgpt_submit,
            observe_seconds,
        )
        p = upstream.to_payload()
        state.update({
            "canonical_cycle_result": str(p.get("result") or "FAIL"),
            "stable_latest_source_used": bool(p.get("stable_latest_source_used")),
            "previous_canonical_uploaded": bool(p.get("previous_canonical_uploaded")),
            "uploaded_report_role": str(p.get("uploaded_report_role") or ""),
            "uploaded_report_count": int(p.get("uploaded_report_count") or 0),
            "current_canonical_report_created": bool(p.get("current_canonical_report_created")),
            "latest_canonical_matches_current": bool(p.get("latest_canonical_matches_current")),
            "chatgpt_submit_performed": bool(p.get("chatgpt_submit_performed")),
            "ready_for_next_probe": bool(p.get("ready_for_next_probe")),
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
        if p.get("result") != "PASS":
            raise RuntimeError(f"Stable canonical cycle failed; upstream_error={p.get('error')}")
        state.update({"response_readiness_probe_started": True})
        probe = probe_response_readiness(probe_seconds)
        state.update(probe)
        ok = bool(probe.get("edge_window_found_for_probe")) and int(probe.get("scanned_control_count") or 0) > 0 and bool(state.get("ready_for_next_probe"))
        state.update({
            "response_readiness_probe_completed": True,
            "result": "PASS" if ok else "FAIL",
            "failure_layer": "" if ok else "stable_canonical_response_readiness_probe",
            "error": "" if ok else "Response-readiness probe did not find an Edge window or scan controls.",
        })
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "stable_canonical_response_readiness_probe", "error": f"{type(exc).__name__}: {exc}"})
    result = StableCanonicalResponseReadinessProbeResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: StableCanonicalResponseReadinessProbeResult) -> None:
    p = result.to_payload()
    true_keys = [
        "stable_latest_source_used", "previous_canonical_uploaded", "current_canonical_report_created", "latest_canonical_matches_current",
        "chatgpt_submit_performed", "ready_for_next_probe", "response_readiness_probe_started", "response_readiness_probe_completed",
        "edge_window_found_for_probe", "candidate_fingerprints_recorded", "candidate_rect_hashes_recorded", "candidate_control_types_recorded",
    ]
    false_keys = [
        "conversation_text_logged", "full_conversation_text_logged", "prompt_text_logged", "file_content_logged",
        "download_click_performed", "generated_file_click_performed", "candidate_click_performed", "run_package_invoked",
        "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if p.get("canonical_cycle_result") != "PASS":
        missing.append("canonical_cycle_result_PASS")
    if p.get("uploaded_report_role") != "canonical_browser_evidence_report":
        missing.append("uploaded_report_role_canonical")
    if int(p.get("uploaded_report_count") or 0) != 1:
        missing.append("uploaded_report_count_1")
    if int(p.get("scanned_control_count") or 0) <= 0:
        missing.append("scanned_control_count_positive")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14A acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
