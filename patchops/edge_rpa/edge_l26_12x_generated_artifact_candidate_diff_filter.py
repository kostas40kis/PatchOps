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

PATCH_NAME = "l26_12x_generated_artifact_candidate_diff_filter"


@dataclass(frozen=True)
class GeneratedArtifactCandidateDiffResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    baseline_scan_completed: bool = False
    baseline_candidate_count: int = 0
    baseline_fingerprints_recorded: bool = False
    upload_submit_idle_result: str = "FAIL"
    uploaded_report_count: int = 0
    uploaded_safe_copy_hash_matches_inner_report: bool = False
    chatgpt_submit_performed: bool = False
    ready_for_next_probe: bool = False
    post_scan_completed: bool = False
    post_candidate_count: int = 0
    known_candidate_count: int = 0
    novel_candidate_count: int = 0
    novel_actionable_candidate_count: int = 0
    novel_clickable_candidate_count: int = 0
    novel_link_like_candidate_count: int = 0
    novel_file_like_candidate_count: int = 0
    novel_download_like_candidate_count: int = 0
    novel_zip_like_candidate_count: int = 0
    novel_candidate_fingerprints_recorded: bool = False
    novel_candidate_fingerprints: list[str] = field(default_factory=list)
    novel_candidate_rect_hashes_recorded: bool = False
    novel_candidate_rect_hashes: list[str] = field(default_factory=list)
    novel_candidate_control_types_recorded: bool = False
    novel_candidate_control_types: list[str] = field(default_factory=list)
    generated_candidate_click_allowed: bool = False
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


def write_json(path: Path, result: GeneratedArtifactCandidateDiffResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: GeneratedArtifactCandidateDiffResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = result.to_payload()
    lines: list[str] = []
    for key, value in payload.items():
        if isinstance(value, list):
            lines.append(f"{key}: {','.join(str(item) for item in value)}")
        else:
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _kind(control_type: str, name: str, automation_id: str, class_name: str) -> tuple[bool, bool, bool, bool, bool]:
    text = " ".join([control_type or "", name or "", automation_id or "", class_name or ""]).lower()
    download_like = "download" in text or "save" in text
    zip_like = ".zip" in text or " zip" in text or "archive" in text
    file_like = "file" in text or "attachment" in text or ".txt" in text or ".md" in text or ".json" in text or ".zip" in text
    link_like = control_type in {"Hyperlink", "Button"} and (download_like or zip_like or file_like or "sandbox" in text)
    artifact = download_like or zip_like or file_like or link_like
    return artifact, download_like, zip_like, file_like, link_like


def _safe_rect_hash(control: object) -> tuple[str, bool]:
    try:
        r = control.rectangle()
        left = int(r.left)
        top = int(r.top)
        width = int(r.width())
        height = int(r.height())
        center_x = left + max(0, width // 2)
        center_y = top + max(0, height // 2)
        on_screen = width > 0 and height > 0 and center_x >= 0 and center_y >= 0
        return _hash_text(f"{left},{top},{width},{height},{center_x},{center_y},{on_screen}"), on_screen
    except Exception:
        return _hash_text("rect-error"), False


def _visible_enabled_clickable(control: object) -> tuple[bool, bool, bool]:
    try:
        visible = bool(control.is_visible())
    except Exception:
        visible = False
    try:
        enabled = bool(control.is_enabled())
    except Exception:
        enabled = False
    return visible, enabled, bool(visible and enabled)


def scan_candidates(probe_seconds: int) -> dict[str, object]:
    deadline = time.time() + max(3, min(int(probe_seconds), 120))
    fingerprints: list[str] = []
    rect_hashes: list[str] = []
    control_types: list[str] = []
    kinds: dict[str, dict[str, bool]] = {}
    seen: set[str] = set()
    scanned = 0
    artifact_count = actionable_count = clickable_count = 0
    download_count = zip_count = file_count = link_count = 0
    edge_found = False
    while time.time() < deadline:
        desktop = pywinauto.Desktop(backend="uia")
        _windows, wrappers = discover_edge_windows(desktop, edge_process_ids())
        wrappers = list(wrappers or [])
        edge_found = edge_found or bool(wrappers)
        for window in wrappers[:3]:
            queue: list[tuple[object, int]] = [(window, 0)]
            local = 0
            while queue and local < 3500:
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
                artifact, download_like, zip_like, file_like, link_like = _kind(control_type, name, automation_id, class_name)
                if artifact:
                    fp = _hash_text("|".join([control_type or "", name or "", automation_id or "", class_name or ""]))
                    rect_hash, on_screen = _safe_rect_hash(control)
                    visible, enabled, clickable = _visible_enabled_clickable(control)
                    if fp not in seen:
                        seen.add(fp)
                        artifact_count += 1
                        if on_screen and visible and enabled:
                            actionable_count += 1
                        if clickable:
                            clickable_count += 1
                        if download_like: download_count += 1
                        if zip_like: zip_count += 1
                        if file_like: file_count += 1
                        if link_like: link_count += 1
                        fingerprints.append(fp)
                        rect_hashes.append(rect_hash)
                        control_types.append(control_type or "unknown")
                        kinds[fp] = {"download": download_like, "zip": zip_like, "file": file_like, "link": link_like, "actionable": bool(on_screen and visible and enabled), "clickable": clickable}
                if depth < 9:
                    try:
                        for child in list(control.children())[:100]:
                            queue.append((child, depth + 1))
                    except Exception:
                        pass
        time.sleep(1.0)
    return {
        "edge_found": edge_found,
        "scanned": scanned,
        "fingerprints": fingerprints,
        "rect_hashes": rect_hashes,
        "control_types": control_types,
        "kinds": kinds,
        "artifact_count": artifact_count,
        "actionable_count": actionable_count,
        "clickable_count": clickable_count,
        "download_count": download_count,
        "zip_count": zip_count,
        "file_count": file_count,
        "link_count": link_count,
    }


def run_generated_candidate_diff_filter(
    output_dir: Path,
    inner_patchops_report_path: Path,
    operator_report_path: Path,
    short_upload_dir: Path,
    allow_report_upload: bool,
    allow_chatgpt_submit: bool,
    observe_seconds: int,
    probe_seconds: int,
) -> GeneratedArtifactCandidateDiffResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "l26_12x_generated_artifact_candidate_diff_filter_result.json"
    live_report_path = output_dir / "l26_12x_generated_artifact_candidate_diff_filter_live_report.txt"
    state: dict[str, object] = {}
    try:
        baseline = scan_candidates(max(3, min(int(probe_seconds), 15)))
        baseline_set = set(baseline.get("fingerprints") or [])
        state.update({
            "baseline_scan_completed": True,
            "baseline_candidate_count": int(baseline.get("artifact_count") or 0),
            "baseline_fingerprints_recorded": True,
        })
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
        post = scan_candidates(probe_seconds)
        post_fps = list(post.get("fingerprints") or [])
        post_rects = list(post.get("rect_hashes") or [])
        post_types = list(post.get("control_types") or [])
        kinds = dict(post.get("kinds") or {})
        novel_fps: list[str] = []
        novel_rects: list[str] = []
        novel_types: list[str] = []
        novel_actionable = novel_clickable = 0
        novel_link = novel_file = novel_download = novel_zip = 0
        for idx, fp in enumerate(post_fps):
            if fp in baseline_set:
                continue
            k = kinds.get(fp, {})
            novel_fps.append(fp)
            novel_rects.append(post_rects[idx] if idx < len(post_rects) else "")
            novel_types.append(post_types[idx] if idx < len(post_types) else "unknown")
            if k.get("actionable"): novel_actionable += 1
            if k.get("clickable"): novel_clickable += 1
            if k.get("link"): novel_link += 1
            if k.get("file"): novel_file += 1
            if k.get("download"): novel_download += 1
            if k.get("zip"): novel_zip += 1
        state.update({
            "post_scan_completed": True,
            "post_candidate_count": int(post.get("artifact_count") or 0),
            "known_candidate_count": len([fp for fp in post_fps if fp in baseline_set]),
            "novel_candidate_count": len(novel_fps),
            "novel_actionable_candidate_count": novel_actionable,
            "novel_clickable_candidate_count": novel_clickable,
            "novel_link_like_candidate_count": novel_link,
            "novel_file_like_candidate_count": novel_file,
            "novel_download_like_candidate_count": novel_download,
            "novel_zip_like_candidate_count": novel_zip,
            "novel_candidate_fingerprints_recorded": True,
            "novel_candidate_fingerprints": novel_fps[:12],
            "novel_candidate_rect_hashes_recorded": True,
            "novel_candidate_rect_hashes": novel_rects[:12],
            "novel_candidate_control_types_recorded": True,
            "novel_candidate_control_types": novel_types[:12],
            "generated_candidate_click_allowed": False,
            "candidate_click_performed": False,
            "result": "PASS",
            "failure_layer": "",
            "error": "",
        })
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "generated_candidate_diff_filter", "error": f"{type(exc).__name__}: {exc}"})
    result = GeneratedArtifactCandidateDiffResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: GeneratedArtifactCandidateDiffResult) -> None:
    p = result.to_payload()
    true_keys = [
        "baseline_scan_completed", "baseline_fingerprints_recorded", "uploaded_safe_copy_hash_matches_inner_report",
        "chatgpt_submit_performed", "ready_for_next_probe", "post_scan_completed",
        "novel_candidate_fingerprints_recorded", "novel_candidate_rect_hashes_recorded", "novel_candidate_control_types_recorded",
    ]
    false_keys = [
        "generated_candidate_click_allowed", "candidate_click_performed", "download_click_performed",
        "generated_file_click_performed", "conversation_text_logged", "full_conversation_text_logged", "prompt_text_logged",
        "file_content_logged", "run_package_invoked", "webdriver_used", "selenium_imported", "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if int(p.get("uploaded_report_count") or 0) != 1:
        missing.append("uploaded_report_count_1")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.12X acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
