from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import pywinauto  # type: ignore

from patchops.edge_rpa.edge_l26_12r_gated_submit_fallback_gate import GatedSubmitFallbackResult, run_gated_submit_fallback
from patchops.edge_rpa.edge_upload_safe_report_copy_gate import _info_text
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_12s_post_submit_idle_observer"


@dataclass(frozen=True)
class PostSubmitIdleObserverResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    submit_result: str = "FAIL"
    picker_confirmed_upload_accepted: bool = False
    chatgpt_submit_performed: bool = False
    submit_method: str = ""
    post_submit_observation_started: bool = False
    observe_seconds_requested: int = 0
    observe_wait_completed: bool = False
    edge_window_found: bool = False
    stop_generating_seen: bool = False
    stop_generating_absent_at_end: bool = False
    send_like_control_seen_after_submit: bool = False
    stable_control_count_observed: bool = False
    first_control_count: int = 0
    final_control_count: int = 0
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


def write_json(path: Path, result: PostSubmitIdleObserverResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: PostSubmitIdleObserverResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def _scan_edge_controls(max_controls: int = 3500) -> tuple[bool, int, bool, bool]:
    desktop = pywinauto.Desktop(backend="uia")
    _windows, wrappers = discover_edge_windows(desktop, edge_process_ids())
    wrappers = list(wrappers or [])
    if not wrappers:
        return False, 0, False, False
    stop_seen = False
    send_like_seen = False
    count = 0
    for window in wrappers[:3]:
        queue: list[tuple[object, int]] = [(window, 0)]
        while queue and count < max_controls:
            control, depth = queue.pop(0)
            count += 1
            try:
                info = control.element_info
                control_type = _info_text(info, "control_type")
                name = _info_text(info, "name")
                automation_id = _info_text(info, "automation_id")
                class_name = _info_text(info, "class_name")
            except Exception:
                control_type = name = automation_id = class_name = ""
            text = " ".join([control_type or "", name or "", automation_id or "", class_name or ""]).lower()
            if "stop" in text and ("generat" in text or "respond" in text or control_type == "Button"):
                stop_seen = True
            if ("send" in text or "submit" in text) and "stop" not in text:
                send_like_seen = True
            if depth < 9:
                try:
                    for child in list(control.children())[:100]:
                        queue.append((child, depth + 1))
                except Exception:
                    pass
    return True, count, stop_seen, send_like_seen


def observe_idle(observe_seconds: int) -> dict[str, object]:
    observe_seconds = max(8, min(int(observe_seconds), 180))
    found1, count1, stop1, send1 = _scan_edge_controls()
    stop_seen_any = stop1
    send_seen_any = send1
    deadline = time.time() + observe_seconds
    last_found, last_count, last_stop, last_send = found1, count1, stop1, send1
    while time.time() < deadline:
        time.sleep(3.0)
        last_found, last_count, last_stop, last_send = _scan_edge_controls()
        stop_seen_any = stop_seen_any or last_stop
        send_seen_any = send_seen_any or last_send
    stable = abs(int(last_count) - int(count1)) <= max(25, int(count1 * 0.15)) if count1 and last_count else False
    return {
        "edge_window_found": bool(found1 or last_found),
        "first_control_count": int(count1),
        "final_control_count": int(last_count),
        "stop_generating_seen": bool(stop_seen_any),
        "stop_generating_absent_at_end": not bool(last_stop),
        "send_like_control_seen_after_submit": bool(send_seen_any or last_send),
        "stable_control_count_observed": bool(stable),
    }


def run_post_submit_idle_observer(output_dir: Path, report_path: Path, allow_report_upload: bool, allow_chatgpt_submit: bool, observe_seconds: int) -> PostSubmitIdleObserverResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "l26_12s_post_submit_idle_observer_result.json"
    live_report_path = output_dir / "l26_12s_post_submit_idle_observer_live_report.txt"
    state: dict[str, object] = {"observe_seconds_requested": int(observe_seconds)}
    try:
        submit: GatedSubmitFallbackResult = run_gated_submit_fallback(output_dir / "submit_proof", report_path, allow_report_upload, allow_chatgpt_submit)
        sp = submit.to_payload()
        submit_ok = sp.get("result") == "PASS" and bool(sp.get("chatgpt_submit_performed"))
        state.update({
            "submit_result": str(sp.get("result") or "FAIL"),
            "picker_confirmed_upload_accepted": bool(sp.get("picker_confirmed_upload_accepted")),
            "chatgpt_submit_performed": bool(sp.get("chatgpt_submit_performed")),
            "submit_method": str(sp.get("submit_method") or ""),
        })
        if not submit_ok:
            raise RuntimeError(f"Submit precondition failed; submit_result={sp.get('result')}; error={sp.get('error')}")
        state.update({"post_submit_observation_started": True})
        obs = observe_idle(observe_seconds)
        state.update(obs)
        state.update({"observe_wait_completed": True})
        ready = bool(obs.get("edge_window_found")) and bool(obs.get("stop_generating_absent_at_end"))
        state.update({
            "idle_observation_completed": True,
            "ready_for_next_probe": ready,
            "result": "PASS" if ready else "FAIL",
            "failure_layer": "" if ready else "post_submit_idle_observation",
            "error": "" if ready else "Edge observed, but stop-generating/idle readiness could not be confirmed at the end of the observation window.",
        })
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "post_submit_idle_observer", "error": f"{type(exc).__name__}: {exc}"})
    result = PostSubmitIdleObserverResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: PostSubmitIdleObserverResult) -> None:
    p = result.to_payload()
    true_keys = [
        "picker_confirmed_upload_accepted",
        "chatgpt_submit_performed",
        "post_submit_observation_started",
        "observe_wait_completed",
        "edge_window_found",
        "stop_generating_absent_at_end",
        "idle_observation_completed",
        "ready_for_next_probe",
    ]
    false_keys = [
        "conversation_text_logged", "full_conversation_text_logged", "prompt_text_logged", "file_content_logged",
        "download_click_performed", "generated_file_click_performed", "run_package_invoked", "webdriver_used",
        "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used",
    ]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if not p.get("submit_method"):
        missing.append("submit_method_nonempty")
    if int(p.get("final_control_count") or 0) <= 0:
        missing.append("final_control_count_positive")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.12S acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
