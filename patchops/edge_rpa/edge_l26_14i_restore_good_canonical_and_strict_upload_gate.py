from __future__ import annotations

import hashlib
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.edge_rpa.edge_l26_14f_visible_gate_canonical_publish_restore import VisibleGateCanonicalPublishRestoreResult, run_visible_gate_canonical_publish_restore

PATCH_NAME = "l26_14i_restore_good_canonical_and_strict_upload_gate"


@dataclass(frozen=True)
class RestoreGoodCanonicalAndStrictUploadGateResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    latest_was_good_before_restore: bool = False
    latest_restored_from_good_canonical: bool = False
    restored_source_path: str = ""
    restored_source_hash: str = ""
    strict_visible_gate_required: bool = True
    upstream_strict_result: str = "FAIL"
    visible_attachment_gate_passed: bool = False
    attachment_visible_before_submit: bool = False
    attachment_signal_count_before_submit: int = 0
    picker_confirmed_upload_accepted: bool = False
    chatgpt_submit_performed: bool = False
    submit_method: str = ""
    idle_observation_completed: bool = False
    ready_for_next_probe: bool = False
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


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def write_json(path: Path, result: RestoreGoodCanonicalAndStrictUploadGateResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: RestoreGoodCanonicalAndStrictUploadGateResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def canonical_is_good(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return (
        "PATCHOPS CANONICAL BROWSER EVIDENCE REPORT" in text
        and "PATCHOPS APPLY EVIDENCE" in text
        and "BROWSER LIVE PROOF SUMMARY" in text
        and "visible_attachment_gate_passed: True" in text
        and "browser_live_passed: True" in text
        and "ExitCode : 0" in text
        and "Result   : PASS" in text
    )


def find_last_good_canonical(desktop: Path) -> Path | None:
    patterns = [
        "l26_14f_visible_gate_canonical_publish_restore_*_canonical.txt",
        "l26_13*_canonical.txt",
        "l26_12z_*_canonical.txt",
        "*_canonical.txt",
    ]
    candidates: list[Path] = []
    for pattern in patterns:
        candidates.extend(desktop.glob(pattern))
    unique = []
    seen = set()
    for p in candidates:
        key = str(p.resolve()).lower()
        if key not in seen:
            seen.add(key)
            unique.append(p)
    good = [p for p in unique if canonical_is_good(p)]
    if not good:
        return None
    good.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return good[0]


def restore_latest_if_needed(latest_path: Path, desktop: Path) -> tuple[bool, bool, str, str]:
    was_good = canonical_is_good(latest_path)
    if was_good:
        return True, False, str(latest_path), hash_file(latest_path)
    good = find_last_good_canonical(desktop)
    if good is None:
        raise RuntimeError("No known-good PASS canonical report found to restore latest pointer.")
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(good, latest_path)
    return False, True, str(good), hash_file(good)


def run_restore_good_canonical_and_strict_upload_gate(
    short_live_root: Path,
    latest_canonical_path: Path,
    desktop_path: Path,
    operator_report_path: Path,
    inner_patchops_report_path: Path,
    upload_bridge_dir: Path,
    current_canonical_report_path: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    observe_seconds: int,
    probe_seconds: int,
    attachment_verify_seconds: int,
) -> RestoreGoodCanonicalAndStrictUploadGateResult:
    short_live_root.mkdir(parents=True, exist_ok=True)
    json_path = short_live_root / "l26_14i_restore_good_canonical_and_strict_upload_gate_result.json"
    live_report_path = short_live_root / "l26_14i_restore_good_canonical_and_strict_upload_gate_live_report.txt"
    state: dict[str, object] = {}
    try:
        was_good, restored, restored_source, restored_hash = restore_latest_if_needed(latest_canonical_path, desktop_path)
        state.update({
            "latest_was_good_before_restore": was_good,
            "latest_restored_from_good_canonical": restored,
            "restored_source_path": restored_source,
            "restored_source_hash": restored_hash,
            "strict_visible_gate_required": True,
        })
        upstream: VisibleGateCanonicalPublishRestoreResult = run_visible_gate_canonical_publish_restore(
            short_live_root / "f",
            latest_canonical_path,
            operator_report_path,
            inner_patchops_report_path,
            upload_bridge_dir,
            current_canonical_report_path,
            allow_report_upload,
            allow_chatgpt_submit,
            observe_seconds,
            probe_seconds,
            4,
            attachment_verify_seconds,
        )
        p = upstream.to_payload()
        state.update({
            "upstream_strict_result": str(p.get("result") or "FAIL"),
            "visible_attachment_gate_passed": bool(p.get("visible_attachment_gate_passed")),
            "attachment_visible_before_submit": bool(p.get("attachment_visible_before_submit")),
            "attachment_signal_count_before_submit": int(p.get("attachment_signal_count_before_submit") or 0),
            "picker_confirmed_upload_accepted": bool(p.get("picker_confirmed_upload_accepted")),
            "chatgpt_submit_performed": bool(p.get("chatgpt_submit_performed")),
            "submit_method": str(p.get("submit_method") or ""),
            "idle_observation_completed": bool(p.get("idle_observation_completed")),
            "ready_for_next_probe": bool(p.get("ready_for_next_probe")),
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
        ok = p.get("result") == "PASS" and bool(state["visible_attachment_gate_passed"]) and bool(state["latest_canonical_matches_current"])
        state.update({"result": "PASS" if ok else "FAIL", "failure_layer": "" if ok else "restore_good_canonical_and_strict_upload_gate", "error": "" if ok else f"Strict upload gate failed after restore; upstream={p.get('result')}; upstream_error={p.get('error')}"})
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "restore_good_canonical_and_strict_upload_gate", "error": f"{type(exc).__name__}: {exc}"})
    result = RestoreGoodCanonicalAndStrictUploadGateResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: RestoreGoodCanonicalAndStrictUploadGateResult) -> None:
    p = result.to_payload()
    true_keys = [
        "strict_visible_gate_required", "visible_attachment_gate_passed", "attachment_visible_before_submit",
        "picker_confirmed_upload_accepted", "chatgpt_submit_performed", "idle_observation_completed",
        "ready_for_next_probe", "current_canonical_report_created", "current_canonical_contains_apply_evidence",
        "current_canonical_contains_browser_evidence", "latest_canonical_pointer_created", "latest_canonical_matches_current",
        "selector_completed", "candidate_selected",
    ]
    false_keys = [
        "selected_candidate_click_performed", "candidate_click_performed", "download_click_performed", "generated_file_click_performed",
        "conversation_text_logged", "full_conversation_text_logged", "prompt_text_logged", "file_content_logged",
        "run_package_invoked", "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if not (p.get("latest_was_good_before_restore") or p.get("latest_restored_from_good_canonical")):
        missing.append("latest_good_or_restored")
    if p.get("upstream_strict_result") != "PASS":
        missing.append("upstream_strict_result_PASS")
    if int(p.get("attachment_signal_count_before_submit") or 0) <= 0:
        missing.append("attachment_signal_count_before_submit_positive")
    for key in ("restored_source_path", "restored_source_hash", "selected_candidate_kind", "selected_candidate_fingerprint", "selected_candidate_rect_hash"):
        if not p.get(key):
            missing.append(key + "_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.14I acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
