from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.edge_rpa.edge_composer_detector import run_l26_06_composer_detector
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids
from patchops.edge_rpa.edge_uia_tree_report import safe_text

PATCH_NAME = "l26_07_chatgpt_composer_focus_only_probe"
_CHROME_WORDS = ("omnibox", "address and search bar", "search or enter web address", "favorites bar", "extensions", "tab strip", "toolbar")
_CHROME_CLASSES = ("Omnibox", "OmniboxView", "BrowserRootView", "TabStrip", "ToolbarView")


@dataclass(frozen=True)
class FocusCandidate:
    depth: int
    control_type: str
    class_name_redacted: str
    name_redacted: str
    name_hash: str
    name_length: int
    automation_id_redacted: str
    rectangle: str
    candidate_score: int
    candidate_kind: str
    is_browser_chrome: bool
    is_in_page_scope: bool


@dataclass(frozen=True)
class ComposerFocusProbeResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    targeted_sequence_completed: bool = False
    classification: str = "unknown"
    chatgpt_accessible: bool = False
    composer_detector_completed: bool = False
    composer_candidate_found: bool = False
    candidate_not_browser_chrome: bool = False
    candidate_in_page_scope: bool = False
    candidate_control_type: str = ""
    candidate_class_name_redacted: str = ""
    candidate_automation_id_redacted: str = ""
    composer_focus_attempted: bool = False
    focus_call_succeeded: bool = False
    focus_state_observed: bool = False
    composer_focus_verified: bool = False
    focus_probe_report_written: bool = False
    candidate: FocusCandidate | None = None
    candidate_report_path: str = ""
    detector_json_path: str = ""
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_dom_automation_used: bool = False
    chatgpt_prompt_submitted: bool = False
    prompt_text_entered: bool = False
    keyboard_text_sent: bool = False
    clipboard_prompt_set: bool = False
    page_click_performed: bool = False
    download_click_performed: bool = False
    run_package_invoked: bool = False
    pasteback_or_send_performed: bool = False
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["candidate"] = asdict(self.candidate) if self.candidate is not None else None
        return payload


def _hash_text(value: object) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def _info_text(info: object, name: str) -> str:
    try:
        value = getattr(info, name)
        return "" if value is None else str(value)
    except Exception:
        return ""


def _rect_text(control: object) -> str:
    try:
        rect = control.rectangle()
        return f"L{rect.left} T{rect.top} R{rect.right} B{rect.bottom}"
    except Exception:
        return ""


def _is_browser_chrome(control_type: str, class_name: str, name: str, automation_id: str) -> bool:
    text = " ".join([control_type, class_name, name, automation_id]).lower()
    if any(word.lower() in text for word in _CHROME_WORDS):
        return True
    if any(cls.lower() in class_name.lower() for cls in _CHROME_CLASSES):
        return True
    if automation_id.startswith("view_") and ("address" in text or "omnibox" in text):
        return True
    return False


def _is_root_web_area(control_type: str, class_name: str, name: str, automation_id: str) -> bool:
    text = " ".join([control_type, class_name, name, automation_id]).lower()
    return automation_id == "RootWebArea" or "rootwebarea" in text or control_type == "Document"


def _score_focus_candidate(control_type: str, class_name: str, name: str, automation_id: str, depth: int, page_scope: bool, chrome: bool) -> tuple[str, int]:
    if chrome or not page_scope:
        return "none", 0
    text = " ".join([control_type, class_name, name, automation_id]).lower()
    if control_type == "Button":
        return "none", 0
    score = 0
    kind = "none"
    if control_type == "Edit":
        score += 35
    if automation_id == "prompt-textarea":
        kind = "composer_prompt_textarea_focus_candidate"
        score += 130
    if "prosemirror" in class_name.lower():
        kind = "composer_prosemirror_focus_candidate"
        score += 105
    if "chat with chatgpt" in text or "message chatgpt" in text:
        kind = "composer_named_focus_candidate"
        score += 85
    if "composer" in class_name.lower() and control_type in {"Edit", "Document", "Custom"}:
        kind = "composer_class_focus_candidate"
        score += 45
    if kind == "none" or score < 80:
        return "none", 0
    return kind, score


def _scan_focus_candidates(window: object, *, max_depth: int = 16, max_controls: int = 1000) -> list[tuple[FocusCandidate, object]]:
    found: list[tuple[FocusCandidate, object]] = []
    queue: list[tuple[object, int, bool]] = [(window, 0, False)]
    scanned = 0
    while queue and scanned < max_controls:
        control, depth, inherited_page_scope = queue.pop(0)
        scanned += 1
        try:
            info = control.element_info
            control_type = _info_text(info, "control_type")
            class_name = _info_text(info, "class_name")
            raw_name = _info_text(info, "name")
            automation_id = _info_text(info, "automation_id")
        except Exception:
            control_type = ""
            class_name = ""
            raw_name = ""
            automation_id = ""
        page_scope = bool(inherited_page_scope or _is_root_web_area(control_type, class_name, raw_name, automation_id))
        chrome = _is_browser_chrome(control_type, class_name, raw_name, automation_id)
        kind, score = _score_focus_candidate(control_type, class_name, raw_name, automation_id, depth, page_scope, chrome)
        if kind != "none":
            name_redacted, name_hash, name_length = safe_text(raw_name, control_type=control_type, max_chars=48)
            class_redacted, _, _ = safe_text(class_name, control_type="Button", max_chars=80)
            auto_redacted, _, _ = safe_text(automation_id, control_type="Button", max_chars=48)
            found.append((FocusCandidate(
                depth=depth,
                control_type=control_type,
                class_name_redacted=class_redacted,
                name_redacted=name_redacted,
                name_hash=name_hash,
                name_length=name_length,
                automation_id_redacted=auto_redacted,
                rectangle=_rect_text(control),
                candidate_score=score,
                candidate_kind=kind,
                is_browser_chrome=chrome,
                is_in_page_scope=page_scope,
            ), control))
        if depth >= max_depth:
            continue
        try:
            children = list(control.children())
        except Exception:
            children = []
        for child in children[: max(0, max_controls - scanned)]:
            queue.append((child, depth + 1, page_scope))
    found.sort(key=lambda item: -item[0].candidate_score)
    return found


def _observe_keyboard_focus(control: object) -> tuple[bool, bool, str]:
    try:
        value = bool(control.has_keyboard_focus())
        return True, value, ""
    except Exception as first_exc:
        try:
            value = bool(control.element_info.has_keyboard_focus)
            return True, value, ""
        except Exception as second_exc:
            return False, False, f"has_keyboard_focus failed: {type(first_exc).__name__}: {first_exc}; element_info failed: {type(second_exc).__name__}: {second_exc}"


def _write_report(path: Path, result: ComposerFocusProbeResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.7 ChatGPT composer focus-only probe",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "chatgpt_prompt_submitted:false",
        "prompt_text_entered:false",
        "keyboard_text_sent:false",
        "clipboard_prompt_set:false",
        "page_click_performed:false",
        "",
        f"classification: {result.classification}",
        f"chatgpt_accessible: {result.chatgpt_accessible}",
        f"composer_candidate_found: {result.composer_candidate_found}",
        f"candidate_not_browser_chrome: {result.candidate_not_browser_chrome}",
        f"candidate_in_page_scope: {result.candidate_in_page_scope}",
        f"composer_focus_attempted: {result.composer_focus_attempted}",
        f"focus_call_succeeded: {result.focus_call_succeeded}",
        f"focus_state_observed: {result.focus_state_observed}",
        f"composer_focus_verified: {result.composer_focus_verified}",
        "",
    ]
    if result.candidate is not None:
        item = result.candidate
        lines.extend([
            "CANDIDATE",
            "---------",
            f"kind: {item.candidate_kind}",
            f"score: {item.candidate_score}",
            f"depth: {item.depth}",
            f"control_type: {item.control_type}",
            f"class_name: {item.class_name_redacted}",
            f"name: {item.name_redacted}",
            f"name_hash: {item.name_hash}",
            f"automation_id: {item.automation_id_redacted}",
            f"rectangle: {item.rectangle}",
        ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: ComposerFocusProbeResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_07_focus_probe(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 8.0) -> ComposerFocusProbeResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_07_composer_focus_result.json"
    report_path = out_dir / "normal_edge_l26_07_composer_focus_report.txt"
    detector_dir = out_dir / "composer_detector"
    detector_json = detector_dir / "normal_edge_l26_06_composer_detector_result.json"

    detector = run_l26_06_composer_detector(output_dir=detector_dir, target_url=target_url, start_if_missing=start_if_missing, settle_seconds=settle_seconds, max_depth=14, max_controls=900)
    detector_payload = detector.to_payload()
    classification = str(detector_payload.get("classification", "unknown"))
    sequence_completed = bool(detector_payload.get("targeted_sequence_completed"))
    accessible = bool(detector_payload.get("chatgpt_accessible"))
    detector_completed = bool(detector_payload.get("composer_scan_completed") and detector_payload.get("result") == "PASS")

    if not (sequence_completed and accessible and detector_completed):
        result = ComposerFocusProbeResult(
            targeted_sequence_completed=sequence_completed,
            classification=classification,
            chatgpt_accessible=accessible,
            composer_detector_completed=detector_completed,
            detector_json_path=str(detector_json),
            candidate_report_path=str(report_path),
            result="FAIL",
            failure_layer="composer_detector_gate",
            error=f"L26.7 requires L26.6B accessible detector PASS first; classification={classification!r} detector_completed={detector_completed}.",
        )
        _write_report(report_path, result)
        _write_json(json_path, result)
        return result

    try:
        import pywinauto  # type: ignore
        edge_pids = edge_process_ids()
        desktop = pywinauto.Desktop(backend="uia")
        _windows, wrappers = discover_edge_windows(desktop, edge_pids)
        if not wrappers:
            raise RuntimeError("No normal Edge window wrappers discovered for focus probe.")
        window = wrappers[0]
        window.set_focus()
        candidates = _scan_focus_candidates(window)
        if not candidates:
            raise RuntimeError("No in-page focusable ChatGPT composer candidate was found.")
        candidate, control = candidates[0]
        attempted = True
        try:
            control.set_focus()
            focus_ok = True
            focus_error = ""
        except Exception as exc:
            focus_ok = False
            focus_error = f"{type(exc).__name__}: {exc}"
        time.sleep(0.4)
        observed, verified, observe_error = _observe_keyboard_focus(control)
        error = focus_error or observe_error
    except Exception as exc:
        candidate = None
        attempted = False
        focus_ok = False
        observed = False
        verified = False
        error = f"{type(exc).__name__}: {exc}"

    result_pass = bool(candidate is not None and attempted and focus_ok and observed and verified and not candidate.is_browser_chrome and candidate.is_in_page_scope)
    result = ComposerFocusProbeResult(
        targeted_sequence_completed=sequence_completed,
        classification=classification,
        chatgpt_accessible=accessible,
        composer_detector_completed=detector_completed,
        composer_candidate_found=candidate is not None,
        candidate_not_browser_chrome=bool(candidate is not None and not candidate.is_browser_chrome),
        candidate_in_page_scope=bool(candidate is not None and candidate.is_in_page_scope),
        candidate_control_type=candidate.control_type if candidate is not None else "",
        candidate_class_name_redacted=candidate.class_name_redacted if candidate is not None else "",
        candidate_automation_id_redacted=candidate.automation_id_redacted if candidate is not None else "",
        composer_focus_attempted=attempted,
        focus_call_succeeded=focus_ok,
        focus_state_observed=observed,
        composer_focus_verified=verified,
        focus_probe_report_written=True,
        candidate=candidate,
        candidate_report_path=str(report_path),
        detector_json_path=str(detector_json),
        result="PASS" if result_pass else "FAIL",
        failure_layer="" if result_pass else "composer_focus_probe",
        error="" if result_pass else error,
    )
    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_07_acceptance(result: ComposerFocusProbeResult) -> None:
    payload = result.to_payload()
    required_true = [
        "targeted_sequence_completed",
        "chatgpt_accessible",
        "composer_detector_completed",
        "composer_candidate_found",
        "candidate_not_browser_chrome",
        "candidate_in_page_scope",
        "composer_focus_attempted",
        "focus_call_succeeded",
        "focus_state_observed",
        "composer_focus_verified",
        "focus_probe_report_written",
    ]
    required_false = [
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
        "chatgpt_prompt_submitted",
        "prompt_text_entered",
        "keyboard_text_sent",
        "clipboard_prompt_set",
        "page_click_performed",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
        "full_conversation_text_logged",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if payload.get("classification") != "accessible":
        missing_true.append("classification_accessible")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.7 acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
