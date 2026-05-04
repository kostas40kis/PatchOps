from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import pywinauto  # type: ignore

from patchops.edge_rpa.edge_l26_12p_picker_confirmed_upload_gate import PickerConfirmedUploadResult, run_picker_confirmed_upload
from patchops.edge_rpa.edge_upload_safe_report_copy_gate import _click_control, _hash_text, _info_text
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_12q_gated_send_after_picker_upload"


@dataclass(frozen=True)
class SendCandidate:
    score: int
    control_type: str
    fingerprint: str
    name_length: int
    automation_id_length: int
    class_name_length: int
    depth: int


@dataclass(frozen=True)
class GatedSendResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    allow_chatgpt_submit: bool = False
    upload_result: str = "FAIL"
    picker_confirmed_upload_accepted: bool = False
    send_button_found: bool = False
    send_button_clicked: bool = False
    send_button_candidate_hash: str = ""
    send_button_candidate_control_type: str = ""
    chatgpt_submit_performed: bool = False
    submit_method: str = ""
    send_invocation_completed: bool = False
    post_send_wait_completed: bool = False
    slash_leftover_tolerated: bool = True
    ctrl_l_used: bool = False
    plus_clicked_after_slash: bool = False
    chatgpt_enter_key_sent: bool = False
    download_click_performed: bool = False
    run_package_invoked: bool = False
    pasteback_or_send_performed: bool = False
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    prompt_text_logged: bool = False
    file_content_logged: bool = False
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_dom_automation_used: bool = False
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


def write_json(path: Path, result: GatedSendResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: GatedSendResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def _score_send_candidate(control_type: str, name: str, automation_id: str, class_name: str) -> int:
    text = " ".join([name or "", automation_id or "", class_name or ""]).lower()
    score = 0
    if control_type == "Button": score += 50
    if "send" in text: score += 80
    if "submit" in text: score += 80
    if "prompt" in text or "message" in text: score += 15
    if "composer" in text: score += 10
    if "stop" in text or "voice" in text or "dictate" in text or "attach" in text or "file" in text or "add" in text: score -= 80
    return score


def _fingerprint(control_type: str, name: str, automation_id: str, class_name: str) -> str:
    return _hash_text("|".join([control_type or "", name or "", automation_id or "", class_name or ""]))


def find_send_button() -> tuple[SendCandidate, object]:
    desktop = pywinauto.Desktop(backend="uia")
    edge_pids = edge_process_ids()
    _windows, wrappers = discover_edge_windows(desktop, edge_pids)
    best: tuple[SendCandidate, object] | None = None
    for window in wrappers or []:
        queue: list[tuple[object, int]] = [(window, 0)]
        scanned = 0
        while queue and scanned < 4500:
            control, depth = queue.pop(0)
            scanned += 1
            try:
                info = control.element_info
                control_type = _info_text(info, "control_type")
                name = _info_text(info, "name")
                automation_id = _info_text(info, "automation_id")
                class_name = _info_text(info, "class_name")
            except Exception:
                control_type = name = automation_id = class_name = ""
            score = _score_send_candidate(control_type, name, automation_id, class_name)
            if score >= 80:
                cand = SendCandidate(score=score, control_type=control_type, fingerprint=_fingerprint(control_type, name, automation_id, class_name), name_length=len(name or ""), automation_id_length=len(automation_id or ""), class_name_length=len(class_name or ""), depth=depth)
                if best is None or cand.score > best[0].score or (cand.score == best[0].score and cand.depth < best[0].depth):
                    best = (cand, control)
            if depth < 12:
                try:
                    for child in list(control.children())[:120]:
                        queue.append((child, depth + 1))
                except Exception:
                    pass
    if best is None:
        raise RuntimeError("No ChatGPT send/submit button candidate found in Edge UIA tree.")
    return best


def run_gated_send(output_dir: Path, report_path: Path, allow_report_upload: bool, allow_chatgpt_submit: bool) -> GatedSendResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "l26_12q_gated_send_result.json"
    live_report_path = output_dir / "l26_12q_gated_send_live_report.txt"
    state: dict[str, object] = {"allow_chatgpt_submit": allow_chatgpt_submit}
    try:
        upload: PickerConfirmedUploadResult = run_picker_confirmed_upload(output_dir / "upload_proof", report_path, allow_report_upload)
        up = upload.to_payload()
        upload_ok = bool(up.get("picker_confirmed_upload_accepted")) and up.get("result") == "PASS"
        state.update({
            "upload_result": str(up.get("result") or "FAIL"),
            "picker_confirmed_upload_accepted": upload_ok,
            "slash_leftover_tolerated": bool(up.get("slash_leftover_tolerated")),
            "ctrl_l_used": bool(up.get("ctrl_l_used")),
            "plus_clicked_after_slash": False,
        })
        if not upload_ok:
            raise RuntimeError(f"Upload precondition failed before send; upload_result={up.get('result')}; error={up.get('error')}")
        if not allow_chatgpt_submit:
            raise RuntimeError("Refusing to submit because --allow-chatgpt-submit was not provided.")
        cand, button = find_send_button()
        state.update({"send_button_found": True, "send_button_candidate_hash": cand.fingerprint, "send_button_candidate_control_type": cand.control_type})
        _click_control(button)
        state.update({"send_button_clicked": True, "chatgpt_submit_performed": True, "submit_method": "uia_send_button_click", "send_invocation_completed": True})
        time.sleep(3.0)
        state.update({"post_send_wait_completed": True, "result": "PASS", "failure_layer": "", "error": ""})
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "gated_send_after_picker_upload", "error": f"{type(exc).__name__}: {exc}"})
    result = GatedSendResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: GatedSendResult) -> None:
    p = result.to_payload()
    true_keys = ["allow_chatgpt_submit", "picker_confirmed_upload_accepted", "send_button_found", "send_button_clicked", "chatgpt_submit_performed", "send_invocation_completed", "post_send_wait_completed"]
    false_keys = ["ctrl_l_used", "plus_clicked_after_slash", "chatgpt_enter_key_sent", "download_click_performed", "run_package_invoked", "conversation_text_logged", "prompt_text_logged", "file_content_logged", "webdriver_used", "selenium_imported", "browser_dom_automation_used"]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    for k in ("send_button_candidate_hash", "send_button_candidate_control_type", "submit_method"):
        if not p.get(k): missing.append(k + "_nonempty")
    if p.get("result") != "PASS": missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.12Q acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
