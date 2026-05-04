from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.edge_rpa.edge_l26_14a_stable_canonical_response_readiness_probe import (
    StableCanonicalResponseReadinessProbeResult,
    probe_response_readiness,
    run_stable_canonical_response_readiness_probe,
)

PATCH_NAME = "l26_14b_response_readiness_stability_classifier"


@dataclass(frozen=True)
class ResponseReadinessStabilityClassifierResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    upstream_response_probe_result: str = "FAIL"
    canonical_cycle_result: str = "FAIL"
    stable_latest_source_used: bool = False
    previous_canonical_uploaded: bool = False
    uploaded_report_role: str = ""
    uploaded_report_count: int = 0
    current_canonical_report_created: bool = False
    latest_canonical_matches_current: bool = False
    chatgpt_submit_performed: bool = False
    ready_for_next_probe: bool = False
    first_probe_completed: bool = False
    second_probe_completed: bool = False
    edge_window_found_for_probe: bool = False
    first_scanned_control_count: int = 0
    second_scanned_control_count: int = 0
    first_response_like_candidate_count: int = 0
    second_response_like_candidate_count: int = 0
    first_action_button_candidate_count: int = 0
    second_action_button_candidate_count: int = 0
    first_stop_generating_seen: bool = False
    second_stop_generating_seen: bool = False
    response_ready_stable: bool = False
    response_ready_reason: str = ""
    fingerprint_overlap_count: int = 0
    fingerprint_union_count: int = 0
    fingerprint_overlap_ratio_scaled_1000: int = 0
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


def write_json(path: Path, result: ResponseReadinessStabilityClassifierResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: ResponseReadinessStabilityClassifierResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def classify_stability(first: dict[str, object], second: dict[str, object]) -> tuple[bool, str, int, int, int]:
    first_fps = set(first.get("candidate_fingerprints") or [])
    second_fps = set(second.get("candidate_fingerprints") or [])
    union = first_fps | second_fps
    overlap = first_fps & second_fps
    ratio = 1000 if not union else int((len(overlap) / len(union)) * 1000)
    first_scanned = int(first.get("scanned_control_count") or 0)
    second_scanned = int(second.get("scanned_control_count") or 0)
    second_edge = bool(second.get("edge_window_found_for_probe"))
    second_stop = bool(second.get("stop_generating_seen"))
    second_response = int(second.get("response_like_candidate_count") or 0)
    second_composer = int(second.get("composer_like_candidate_count") or 0)
    if not second_edge:
        return False, "edge_window_missing", len(overlap), len(union), ratio
    if second_scanned <= 0:
        return False, "no_controls_scanned", len(overlap), len(union), ratio
    if second_stop:
        return False, "stop_generating_seen", len(overlap), len(union), ratio
    if first_scanned > 0 and second_scanned > 0 and ratio < 150:
        return False, "fingerprint_overlap_too_low", len(overlap), len(union), ratio
    if second_response <= 0 and second_composer <= 0:
        return False, "no_response_or_composer_candidates", len(overlap), len(union), ratio
    return True, "stable_idle_response_state", len(overlap), len(union), ratio


def run_response_readiness_stability_classifier(
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
) -> ResponseReadinessStabilityClassifierResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14b_response_readiness_stability_classifier_result.json"
    live_report_path = short_live_root / "l26_14b_response_readiness_stability_classifier_live_report.txt"
    state: dict[str, object] = {}
    try:
        upstream: StableCanonicalResponseReadinessProbeResult = run_stable_canonical_response_readiness_probe(
            short_live_root / "p",
            latest_canonical_path,
            operator_report_path,
            inner_patchops_report_path,
            short_upload_dir,
            current_canonical_report_path,
            allow_report_upload,
            allow_chatgpt_submit,
            observe_seconds,
            probe_seconds,
        )
        p = upstream.to_payload()
        first_probe = {
            "edge_window_found_for_probe": bool(p.get("edge_window_found_for_probe")),
            "scanned_control_count": int(p.get("scanned_control_count") or 0),
            "response_like_candidate_count": int(p.get("response_like_candidate_count") or 0),
            "action_button_candidate_count": int(p.get("action_button_candidate_count") or 0),
            "composer_like_candidate_count": int(p.get("composer_like_candidate_count") or 0),
            "stop_generating_seen": bool(p.get("stop_generating_seen")),
            "candidate_fingerprints": list(p.get("candidate_fingerprints") or []),
        }
        state.update({
            "upstream_response_probe_result": str(p.get("result") or "FAIL"),
            "canonical_cycle_result": str(p.get("canonical_cycle_result") or "FAIL"),
            "stable_latest_source_used": bool(p.get("stable_latest_source_used")),
            "previous_canonical_uploaded": bool(p.get("previous_canonical_uploaded")),
            "uploaded_report_role": str(p.get("uploaded_report_role") or ""),
            "uploaded_report_count": int(p.get("uploaded_report_count") or 0),
            "current_canonical_report_created": bool(p.get("current_canonical_report_created")),
            "latest_canonical_matches_current": bool(p.get("latest_canonical_matches_current")),
            "chatgpt_submit_performed": bool(p.get("chatgpt_submit_performed")),
            "ready_for_next_probe": bool(p.get("ready_for_next_probe")),
            "first_probe_completed": bool(p.get("response_readiness_probe_completed")),
            "first_scanned_control_count": int(p.get("scanned_control_count") or 0),
            "first_response_like_candidate_count": int(p.get("response_like_candidate_count") or 0),
            "first_action_button_candidate_count": int(p.get("action_button_candidate_count") or 0),
            "first_stop_generating_seen": bool(p.get("stop_generating_seen")),
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
        if p.get("result") != "PASS":
            raise RuntimeError(f"Upstream response-readiness probe failed; upstream_error={p.get('error')}")
        time.sleep(max(1, min(int(stability_delay_seconds), 30)))
        second_probe = probe_response_readiness(max(5, min(int(probe_seconds), 60)))
        stable, reason, overlap, union, ratio = classify_stability(first_probe, second_probe)
        state.update({
            "second_probe_completed": True,
            "edge_window_found_for_probe": bool(second_probe.get("edge_window_found_for_probe")),
            "second_scanned_control_count": int(second_probe.get("scanned_control_count") or 0),
            "second_response_like_candidate_count": int(second_probe.get("response_like_candidate_count") or 0),
            "second_action_button_candidate_count": int(second_probe.get("action_button_candidate_count") or 0),
            "second_stop_generating_seen": bool(second_probe.get("stop_generating_seen")),
            "response_ready_stable": stable,
            "response_ready_reason": reason,
            "fingerprint_overlap_count": overlap,
            "fingerprint_union_count": union,
            "fingerprint_overlap_ratio_scaled_1000": ratio,
            "result": "PASS" if stable else "FAIL",
            "failure_layer": "" if stable else "response_readiness_stability_classifier",
            "error": "" if stable else reason,
        })
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "response_readiness_stability_classifier", "error": f"{type(exc).__name__}: {exc}"})
    result = ResponseReadinessStabilityClassifierResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: ResponseReadinessStabilityClassifierResult) -> None:
    p = result.to_payload()
    true_keys = [
        "stable_latest_source_used", "previous_canonical_uploaded", "current_canonical_report_created", "latest_canonical_matches_current",
        "chatgpt_submit_performed", "ready_for_next_probe", "first_probe_completed", "second_probe_completed",
        "edge_window_found_for_probe", "response_ready_stable",
    ]
    false_keys = [
        "candidate_click_performed", "download_click_performed", "generated_file_click_performed", "conversation_text_logged",
        "full_conversation_text_logged", "prompt_text_logged", "file_content_logged", "run_package_invoked",
        "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if p.get("upstream_response_probe_result") != "PASS":
        missing.append("upstream_response_probe_result_PASS")
    if p.get("canonical_cycle_result") != "PASS":
        missing.append("canonical_cycle_result_PASS")
    if p.get("uploaded_report_role") != "canonical_browser_evidence_report":
        missing.append("uploaded_report_role_canonical")
    if int(p.get("uploaded_report_count") or 0) != 1:
        missing.append("uploaded_report_count_1")
    if int(p.get("first_scanned_control_count") or 0) <= 0:
        missing.append("first_scanned_control_count_positive")
    if int(p.get("second_scanned_control_count") or 0) <= 0:
        missing.append("second_scanned_control_count_positive")
    if p.get("second_stop_generating_seen"):
        unexpected.append("second_stop_generating_seen")
    if not p.get("response_ready_reason"):
        missing.append("response_ready_reason_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14B acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
