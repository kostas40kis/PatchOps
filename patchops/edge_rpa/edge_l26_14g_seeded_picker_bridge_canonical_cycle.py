from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from patchops.edge_rpa.edge_l26_14f_visible_gate_canonical_publish_restore import VisibleGateCanonicalPublishRestoreResult, run_visible_gate_canonical_publish_restore

PATCH_NAME = "l26_14g_seeded_picker_bridge_canonical_cycle"


@dataclass(frozen=True)
class SeededPickerBridgeCanonicalCycleResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    seeded_bridge_count: int = 0
    seeded_bridge_dirs_recorded: bool = False
    seeded_bridge_dir_hashes: list[str] = field(default_factory=list)
    primary_bridge_dir_path: str = ""
    seed_copy_count: int = 0
    seed_copy_hashes_match: bool = False
    upstream_publish_result: str = "FAIL"
    visible_attachment_gate_passed: bool = False
    attachment_visible_before_submit: bool = False
    picker_confirmed_upload_accepted: bool = False
    chatgpt_submit_performed: bool = False
    idle_observation_completed: bool = False
    ready_for_next_probe: bool = False
    uploaded_safe_copy_parent_matches_primary_bridge: bool = False
    current_canonical_report_created: bool = False
    current_canonical_contains_apply_evidence: bool = False
    current_canonical_contains_browser_evidence: bool = False
    latest_canonical_pointer_created: bool = False
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


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def write_json(path: Path, result: SeededPickerBridgeCanonicalCycleResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: SeededPickerBridgeCanonicalCycleResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def seed_upload_locations(source: Path, bridge_dirs: list[Path]) -> tuple[int, bool, list[str]]:
    source_hash = hash_file(source)
    count = 0
    all_match = True
    dir_hashes: list[str] = []
    for raw_dir in bridge_dirs:
        try:
            d = raw_dir.resolve()
            d.mkdir(parents=True, exist_ok=True)
            dir_hashes.append(hash_text(str(d)))
            target = d / f"seeded_visible_attachment_{int(time.time())}.txt"
            shutil.copyfile(source, target)
            count += 1
            all_match = all_match and hash_file(target) == source_hash
        except Exception:
            all_match = False
    return count, all_match, dir_hashes[:12]


def run_seeded_picker_bridge_canonical_cycle(
    short_live_root: Path,
    latest_canonical_path: Path,
    operator_report_path: Path,
    inner_patchops_report_path: Path,
    primary_bridge_dir: Path,
    bridge_dirs: list[Path],
    current_canonical_report_path: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    observe_seconds: int,
    probe_seconds: int,
    stability_delay_seconds: int,
    attachment_verify_seconds: int,
) -> SeededPickerBridgeCanonicalCycleResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14g_seeded_picker_bridge_canonical_cycle_result.json"
    live_report_path = short_live_root / "l26_14g_seeded_picker_bridge_canonical_cycle_live_report.txt"
    state: dict[str, object] = {}
    try:
        unique_dirs: list[Path] = []
        seen: set[str] = set()
        for d in [primary_bridge_dir, *bridge_dirs]:
            resolved = d.resolve()
            key = str(resolved).lower()
            if key not in seen:
                seen.add(key)
                unique_dirs.append(resolved)
        seed_count, seed_match, dir_hashes = seed_upload_locations(latest_canonical_path.resolve(), unique_dirs)
        upstream: VisibleGateCanonicalPublishRestoreResult = run_visible_gate_canonical_publish_restore(
            short_live_root / "f",
            latest_canonical_path,
            operator_report_path,
            inner_patchops_report_path,
            primary_bridge_dir,
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
            "seeded_bridge_count": len(unique_dirs),
            "seeded_bridge_dirs_recorded": True,
            "seeded_bridge_dir_hashes": dir_hashes,
            "primary_bridge_dir_path": str(primary_bridge_dir.resolve()),
            "seed_copy_count": seed_count,
            "seed_copy_hashes_match": seed_match,
            "upstream_publish_result": str(p.get("result") or "FAIL"),
            "visible_attachment_gate_passed": bool(p.get("visible_attachment_gate_passed")),
            "attachment_visible_before_submit": bool(p.get("attachment_visible_before_submit")),
            "picker_confirmed_upload_accepted": bool(p.get("picker_confirmed_upload_accepted")),
            "chatgpt_submit_performed": bool(p.get("chatgpt_submit_performed")),
            "idle_observation_completed": bool(p.get("idle_observation_completed")),
            "ready_for_next_probe": bool(p.get("ready_for_next_probe")),
            "uploaded_safe_copy_parent_matches_primary_bridge": bool(p.get("uploaded_safe_copy_parent_matches_bridge")),
            "current_canonical_report_created": bool(p.get("current_canonical_report_created")),
            "current_canonical_contains_apply_evidence": bool(p.get("current_canonical_contains_apply_evidence")),
            "current_canonical_contains_browser_evidence": bool(p.get("current_canonical_contains_browser_evidence")),
            "latest_canonical_pointer_created": bool(p.get("latest_canonical_pointer_created")),
            "latest_canonical_matches_current": bool(p.get("latest_canonical_matches_current")),
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
        ok = p.get("result") == "PASS" and seed_count >= 1 and seed_match and bool(state["visible_attachment_gate_passed"]) and bool(state["latest_canonical_matches_current"])
        state.update({"result": "PASS" if ok else "FAIL", "failure_layer": "" if ok else "seeded_picker_bridge_canonical_cycle", "error": "" if ok else f"Seeded picker bridge failed; upstream={p.get('result')}; seed_count={seed_count}; seed_match={seed_match}; upstream_error={p.get('error')}"})
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "seeded_picker_bridge_canonical_cycle", "error": f"{type(exc).__name__}: {exc}"})
    result = SeededPickerBridgeCanonicalCycleResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: SeededPickerBridgeCanonicalCycleResult) -> None:
    p = result.to_payload()
    true_keys = [
        "seeded_bridge_dirs_recorded", "seed_copy_hashes_match", "visible_attachment_gate_passed",
        "attachment_visible_before_submit", "picker_confirmed_upload_accepted", "chatgpt_submit_performed",
        "idle_observation_completed", "ready_for_next_probe", "uploaded_safe_copy_parent_matches_primary_bridge",
        "current_canonical_report_created", "current_canonical_contains_apply_evidence", "current_canonical_contains_browser_evidence",
        "latest_canonical_pointer_created", "latest_canonical_matches_current", "selector_completed", "candidate_selected",
    ]
    false_keys = [
        "selected_candidate_click_performed", "candidate_click_performed", "download_click_performed", "generated_file_click_performed",
        "conversation_text_logged", "full_conversation_text_logged", "prompt_text_logged", "file_content_logged",
        "run_package_invoked", "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if int(p.get("seeded_bridge_count") or 0) <= 0:
        missing.append("seeded_bridge_count_positive")
    if int(p.get("seed_copy_count") or 0) <= 0:
        missing.append("seed_copy_count_positive")
    if p.get("upstream_publish_result") != "PASS":
        missing.append("upstream_publish_result_PASS")
    for key in ("primary_bridge_dir_path", "selected_candidate_kind", "selected_candidate_fingerprint", "selected_candidate_rect_hash"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14G acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
