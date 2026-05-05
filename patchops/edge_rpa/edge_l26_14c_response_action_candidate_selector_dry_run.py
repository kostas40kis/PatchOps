from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import pywinauto  # type: ignore

from patchops.edge_rpa.edge_l26_14b_response_readiness_stability_classifier import ResponseReadinessStabilityClassifierResult, run_response_readiness_stability_classifier
from patchops.edge_rpa.edge_upload_safe_report_copy_gate import _hash_text, _info_text
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_14c_response_action_candidate_selector_dry_run"


@dataclass(frozen=True)
class ResponseActionCandidateSelectorDryRunResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    upstream_stability_result: str = "FAIL"
    response_ready_stable: bool = False
    canonical_cycle_result: str = "FAIL"
    stable_latest_source_used: bool = False
    previous_canonical_uploaded: bool = False
    uploaded_report_role: str = ""
    uploaded_report_count: int = 0
    current_canonical_report_created: bool = False
    latest_canonical_matches_current: bool = False
    chatgpt_submit_performed: bool = False
    ready_for_next_probe: bool = False
    selector_started: bool = False
    selector_completed: bool = False
    edge_window_found_for_selector: bool = False
    selector_scanned_control_count: int = 0
    candidate_inventory_count: int = 0
    candidate_selected: bool = False
    selected_candidate_kind: str = ""
    selected_candidate_rank: int = 0
    selected_candidate_fingerprint: str = ""
    selected_candidate_rect_hash: str = ""
    selected_candidate_control_type: str = ""
    selected_candidate_click_allowed: bool = False
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


def write_json(path: Path, result: ResponseActionCandidateSelectorDryRunResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: ResponseActionCandidateSelectorDryRunResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def _rect_hash(control: object) -> tuple[str, bool]:
    try:
        r = control.rectangle()
        w = int(r.width())
        h = int(r.height())
        cx = int(r.left) + max(0, w // 2)
        cy = int(r.top) + max(0, h // 2)
        visible_rect = w > 2 and h > 2 and cx >= 0 and cy >= 0
        return _hash_text(f"{int(r.left)},{int(r.top)},{w},{h},{cx},{cy}"), visible_rect
    except Exception:
        return _hash_text("rect-error"), False


def _rank_candidate(control_type: str, name: str, automation_id: str, class_name: str, visible_rect: bool) -> tuple[int, str]:
    # Internal text is only used for classification. It is never persisted to reports.
    t = " ".join([control_type or "", name or "", automation_id or "", class_name or ""]).lower()
    base = 0
    kind = "none"
    if "copy" in t or "clipboard" in t:
        base, kind = 90, "copy_like_response_action"
    elif "regenerate" in t or "try again" in t:
        base, kind = 70, "regenerate_like_response_action"
    elif "read aloud" in t or "thumb" in t or "rating" in t:
        base, kind = 55, "response_feedback_action"
    elif "message" in t or "prompt" in t or "textbox" in t or "composer" in t or control_type in {"Edit", "Document"}:
        base, kind = 25, "composer_or_response_surface"
    elif control_type in {"Button", "Hyperlink", "MenuItem", "SplitButton"}:
        base, kind = 15, "generic_action_control"
    if base and control_type in {"Button", "Hyperlink", "MenuItem", "SplitButton"}:
        base += 5
    if base and visible_rect:
        base += 3
    return base, kind


def select_response_action_candidate(probe_seconds: int) -> dict[str, object]:
    deadline = time.time() + max(5, min(int(probe_seconds), 90))
    best: dict[str, object] = {}
    seen: set[str] = set()
    scanned = 0
    inventory = 0
    edge_found = False
    while time.time() < deadline:
        desktop = pywinauto.Desktop(backend="uia")
        _windows, wrappers = discover_edge_windows(desktop, edge_process_ids())
        wrappers = list(wrappers or [])
        edge_found = edge_found or bool(wrappers)
        for window in wrappers[:3]:
            queue: list[tuple[object, int]] = [(window, 0)]
            local = 0
            while queue and local < 4500:
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
                rect_hash, visible_rect = _rect_hash(control)
                rank, kind = _rank_candidate(control_type, name, automation_id, class_name, visible_rect)
                if rank > 0:
                    fp = _hash_text("|".join([control_type or "", name or "", automation_id or "", class_name or ""]))
                    if fp not in seen:
                        seen.add(fp)
                        inventory += 1
                        if not best or rank > int(best.get("rank", 0)):
                            best = {"rank": rank, "kind": kind, "fingerprint": fp, "rect_hash": rect_hash, "control_type": control_type or "unknown"}
                if depth < 9:
                    try:
                        for child in list(control.children())[:100]:
                            queue.append((child, depth + 1))
                    except Exception:
                        pass
        time.sleep(1.0)
    return {"edge_found": edge_found, "scanned": scanned, "inventory": inventory, "best": best}


def run_response_action_candidate_selector_dry_run(
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
    stability_delay_seconds: int,
) -> ResponseActionCandidateSelectorDryRunResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14c_response_action_candidate_selector_dry_run_result.json"
    live_report_path = short_live_root / "l26_14c_response_action_candidate_selector_dry_run_live_report.txt"
    state: dict[str, object] = {}
    try:
        upstream: ResponseReadinessStabilityClassifierResult = run_response_readiness_stability_classifier(
            short_live_root / "b",
            latest_canonical_path,
            operator_report_path,
            inner_patchops_report_path,
            short_upload_dir,
            current_canonical_report_path,
            allow_report_upload,
            allow_chatgpt_submit,
            observe_seconds,
            probe_seconds,
            stability_delay_seconds,
        )
        p = upstream.to_payload()
        state.update({
            "upstream_stability_result": str(p.get("result") or "FAIL"),
            "response_ready_stable": bool(p.get("response_ready_stable")),
            "canonical_cycle_result": str(p.get("canonical_cycle_result") or "FAIL"),
            "stable_latest_source_used": bool(p.get("stable_latest_source_used")),
            "previous_canonical_uploaded": bool(p.get("previous_canonical_uploaded")),
            "uploaded_report_role": str(p.get("uploaded_report_role") or ""),
            "uploaded_report_count": int(p.get("uploaded_report_count") or 0),
            "current_canonical_report_created": bool(p.get("current_canonical_report_created")),
            "latest_canonical_matches_current": bool(p.get("latest_canonical_matches_current")),
            "chatgpt_submit_performed": bool(p.get("chatgpt_submit_performed")),
            "ready_for_next_probe": bool(p.get("ready_for_next_probe")),
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
        if p.get("result") != "PASS" or not bool(p.get("response_ready_stable")):
            raise RuntimeError(f"Upstream stability classifier was not ready; result={p.get('result')}; reason={p.get('response_ready_reason')}; error={p.get('error')}")
        state.update({"selector_started": True})
        selected = select_response_action_candidate(probe_seconds)
        best = dict(selected.get("best") or {})
        state.update({
            "selector_completed": True,
            "edge_window_found_for_selector": bool(selected.get("edge_found")),
            "selector_scanned_control_count": int(selected.get("scanned") or 0),
            "candidate_inventory_count": int(selected.get("inventory") or 0),
            "candidate_selected": bool(best),
            "selected_candidate_kind": str(best.get("kind") or ""),
            "selected_candidate_rank": int(best.get("rank") or 0),
            "selected_candidate_fingerprint": str(best.get("fingerprint") or ""),
            "selected_candidate_rect_hash": str(best.get("rect_hash") or ""),
            "selected_candidate_control_type": str(best.get("control_type") or ""),
            "selected_candidate_click_allowed": False,
            "selected_candidate_click_performed": False,
        })
        ok = bool(best) and bool(selected.get("edge_found")) and int(selected.get("scanned") or 0) > 0
        state.update({"result": "PASS" if ok else "FAIL", "failure_layer": "" if ok else "response_action_candidate_selector_dry_run", "error": "" if ok else "No response action candidate was selected."})
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "response_action_candidate_selector_dry_run", "error": f"{type(exc).__name__}: {exc}"})
    result = ResponseActionCandidateSelectorDryRunResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: ResponseActionCandidateSelectorDryRunResult) -> None:
    p = result.to_payload()
    true_keys = [
        "response_ready_stable", "stable_latest_source_used", "previous_canonical_uploaded", "current_canonical_report_created",
        "latest_canonical_matches_current", "chatgpt_submit_performed", "ready_for_next_probe", "selector_started",
        "selector_completed", "edge_window_found_for_selector", "candidate_selected",
    ]
    false_keys = [
        "selected_candidate_click_allowed", "selected_candidate_click_performed", "candidate_click_performed", "download_click_performed",
        "generated_file_click_performed", "conversation_text_logged", "full_conversation_text_logged", "prompt_text_logged",
        "file_content_logged", "run_package_invoked", "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if p.get("upstream_stability_result") != "PASS":
        missing.append("upstream_stability_result_PASS")
    if p.get("canonical_cycle_result") != "PASS":
        missing.append("canonical_cycle_result_PASS")
    if p.get("uploaded_report_role") != "canonical_browser_evidence_report":
        missing.append("uploaded_report_role_canonical")
    if int(p.get("uploaded_report_count") or 0) != 1:
        missing.append("uploaded_report_count_1")
    if int(p.get("selector_scanned_control_count") or 0) <= 0:
        missing.append("selector_scanned_control_count_positive")
    for key in ("selected_candidate_kind", "selected_candidate_fingerprint", "selected_candidate_rect_hash", "selected_candidate_control_type"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14C acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
