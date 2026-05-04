from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import pywinauto  # type: ignore
from pywinauto import keyboard, mouse  # type: ignore

from patchops.edge_rpa.edge_l26_12p_picker_confirmed_upload_gate import PickerConfirmedUploadResult, run_picker_confirmed_upload
from patchops.edge_rpa.edge_upload_safe_report_copy_gate import _click_control, _hash_text, _info_text
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_12r_gated_submit_fallback_after_upload"


@dataclass(frozen=True)
class GatedSubmitFallbackResult:
    patch_name: str = PATCH_NAME
    python_executable: str = sys.executable
    allow_chatgpt_submit: bool = False
    upload_result: str = "FAIL"
    picker_confirmed_upload_accepted: bool = False
    uia_send_button_found: bool = False
    uia_send_button_clicked: bool = False
    uia_send_button_candidate_hash: str = ""
    uia_send_button_candidate_control_type: str = ""
    coordinate_fallback_used: bool = False
    coordinate_click_performed: bool = False
    coordinate_click_target_hash: str = ""
    escape_sent_before_submit: bool = False
    submit_invocation_completed: bool = False
    chatgpt_submit_performed: bool = False
    submit_method: str = ""
    post_submit_wait_completed: bool = False
    ctrl_l_used: bool = False
    plus_clicked_after_slash: bool = False
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


def write_json(path: Path, result: GatedSubmitFallbackResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def write_live_report(path: Path, result: GatedSubmitFallbackResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{k}: {v}" for k, v in result.to_payload().items()) + "\n", encoding="utf-8")


def _edge_wrappers() -> list[object]:
    desktop = pywinauto.Desktop(backend="uia")
    _windows, wrappers = discover_edge_windows(desktop, edge_process_ids())
    return list(wrappers or [])


def _score_send_candidate(control_type: str, name: str, automation_id: str, class_name: str) -> int:
    text = " ".join([name or "", automation_id or "", class_name or ""]).lower()
    score = 0
    if control_type in {"Button", "SplitButton"}: score += 45
    if "send" in text: score += 90
    if "submit" in text: score += 90
    if "arrow" in text or "up" in text: score += 15
    if "stop" in text or "voice" in text or "dictate" in text or "attach" in text or "file" in text or "add" in text or "plus" in text: score -= 90
    return score


def _fingerprint(control_type: str, name: str, automation_id: str, class_name: str) -> str:
    return _hash_text("|".join([control_type or "", name or "", automation_id or "", class_name or ""]))


def try_uia_send_button() -> tuple[bool, str, str]:
    best: tuple[int, object, str, str] | None = None
    for window in _edge_wrappers():
        queue: list[tuple[object, int]] = [(window, 0)]
        scanned = 0
        while queue and scanned < 6500:
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
                fp = _fingerprint(control_type, name, automation_id, class_name)
                if best is None or score > best[0]:
                    best = (score, control, fp, control_type)
            if depth < 14:
                try:
                    for child in list(control.children())[:140]:
                        queue.append((child, depth + 1))
                except Exception:
                    pass
    if best is None:
        return False, "", ""
    _click_control(best[1])
    return True, best[2], best[3]


def click_coordinate_fallback() -> tuple[bool, str]:
    wrappers = _edge_wrappers()
    if not wrappers:
        return False, ""
    # Pick the largest Edge window and click the lower-right composer/send area.
    def area(w: object) -> int:
        try:
            r = w.rectangle()
            return max(0, r.width()) * max(0, r.height())
        except Exception:
            return 0
    window = sorted(wrappers, key=area, reverse=True)[0]
    try:
        window.set_focus()
    except Exception:
        pass
    time.sleep(0.25)
    r = window.rectangle()
    # ChatGPT composer send control is near the lower-right of the content region.
    x = int(r.right - 105)
    y = int(r.bottom - 92)
    target_hash = _hash_text(f"edge_window_relative:{r.width()}x{r.height()}:-105:-92")
    mouse.click(button="left", coords=(x, y))
    return True, target_hash


def run_gated_submit_fallback(output_dir: Path, report_path: Path, allow_report_upload: bool, allow_chatgpt_submit: bool) -> GatedSubmitFallbackResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "l26_12r_gated_submit_fallback_result.json"
    live_report_path = output_dir / "l26_12r_gated_submit_fallback_live_report.txt"
    state: dict[str, object] = {"allow_chatgpt_submit": allow_chatgpt_submit}
    try:
        upload: PickerConfirmedUploadResult = run_picker_confirmed_upload(output_dir / "upload_proof", report_path, allow_report_upload)
        up = upload.to_payload()
        upload_ok = bool(up.get("picker_confirmed_upload_accepted")) and up.get("result") == "PASS"
        state.update({
            "upload_result": str(up.get("result") or "FAIL"),
            "picker_confirmed_upload_accepted": upload_ok,
            "ctrl_l_used": bool(up.get("ctrl_l_used")),
            "plus_clicked_after_slash": False,
        })
        if not upload_ok:
            raise RuntimeError(f"Upload precondition failed; upload_result={up.get('result')}; error={up.get('error')}")
        if not allow_chatgpt_submit:
            raise RuntimeError("Refusing to submit because --allow-chatgpt-submit was not provided.")

        # Close the slash menu if it is still open. This is not a submit key.
        keyboard.send_keys("{ESC}")
        state.update({"escape_sent_before_submit": True})
        time.sleep(0.35)

        clicked, fp, ctype = try_uia_send_button()
        if clicked:
            state.update({
                "uia_send_button_found": True,
                "uia_send_button_clicked": True,
                "uia_send_button_candidate_hash": fp,
                "uia_send_button_candidate_control_type": ctype,
                "submit_method": "uia_send_button_click",
            })
        else:
            ok, target_hash = click_coordinate_fallback()
            state.update({
                "coordinate_fallback_used": True,
                "coordinate_click_performed": ok,
                "coordinate_click_target_hash": target_hash,
                "submit_method": "edge_window_lower_right_coordinate_click" if ok else "",
            })
            if not ok:
                raise RuntimeError("No UIA send button found and coordinate fallback could not click Edge window.")
        time.sleep(4.0)
        state.update({
            "submit_invocation_completed": True,
            "chatgpt_submit_performed": True,
            "post_submit_wait_completed": True,
            "result": "PASS",
            "failure_layer": "",
            "error": "",
        })
    except Exception as exc:
        state.update({"result": "FAIL", "failure_layer": "gated_submit_fallback_after_upload", "error": f"{type(exc).__name__}: {exc}"})
    result = GatedSubmitFallbackResult(**state)
    write_json(json_path, result)
    write_live_report(live_report_path, result)
    return result


def assert_acceptance(result: GatedSubmitFallbackResult) -> None:
    p = result.to_payload()
    true_keys = ["allow_chatgpt_submit", "picker_confirmed_upload_accepted", "escape_sent_before_submit", "submit_invocation_completed", "chatgpt_submit_performed", "post_submit_wait_completed"]
    false_keys = ["ctrl_l_used", "plus_clicked_after_slash", "download_click_performed", "run_package_invoked", "conversation_text_logged", "prompt_text_logged", "file_content_logged", "webdriver_used", "selenium_imported", "browser_dom_automation_used"]
    missing = [k for k in true_keys if not p.get(k)]
    unexpected = [k for k in false_keys if p.get(k)]
    if not (p.get("uia_send_button_clicked") or p.get("coordinate_click_performed")):
        missing.append("uia_or_coordinate_submit_click")
    if not p.get("submit_method"):
        missing.append("submit_method_nonempty")
    if p.get("coordinate_fallback_used") and not p.get("coordinate_click_target_hash"):
        missing.append("coordinate_click_target_hash_nonempty")
    if p.get("uia_send_button_clicked") and not p.get("uia_send_button_candidate_hash"):
        missing.append("uia_send_button_candidate_hash_nonempty")
    if p.get("result") != "PASS":
        missing.append("result_PASS")
    if missing or unexpected:
        raise AssertionError(f"L26.12R acceptance failed; missing={missing}; unexpected={unexpected}; layer={result.failure_layer}; error={result.error}")
