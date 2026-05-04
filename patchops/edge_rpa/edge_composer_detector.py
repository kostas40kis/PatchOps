from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.edge_rpa.edge_targeted_session_classifier import run_l26_05a_targeted_classifier
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids
from patchops.edge_rpa.edge_uia_tree_report import safe_text

PATCH_NAME = "l26_06b_in_page_composer_detector_repair"
_PROMPT_WORDS = ("message chatgpt", "ask anything", "send a message", "prompt", "composer", "textbox", "text box", "prosemirror", "rich text")
_SEND_WORDS = ("send", "send message", "submit")
_ATTACH_WORDS = ("attach", "upload", "add photos", "add files")
_CHROME_WORDS = ("omnibox", "address and search bar", "search or enter web address", "favorites bar", "extensions", "tab strip", "toolbar")
_CHROME_CLASSES = ("Omnibox", "OmniboxView", "BrowserRootView", "TabStrip", "ToolbarView")


@dataclass(frozen=True)
class ComposerCandidate:
    index: int
    depth: int
    control_type: str
    class_name: str
    name_redacted: str
    name_hash: str
    name_length: int
    automation_id_redacted: str
    rectangle: str
    candidate_kind: str
    candidate_score: int
    is_browser_chrome: bool
    is_in_page_scope: bool
    exclusion_reason: str = ""


@dataclass(frozen=True)
class ComposerDetectorResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    targeted_sequence_completed: bool = False
    classification: str = "unknown"
    chatgpt_accessible: bool = False
    composer_scan_completed: bool = False
    candidate_report_written: bool = False
    controls_scanned: int = 0
    max_depth_observed: int = 0
    browser_chrome_candidates_filtered: bool = False
    browser_chrome_candidate_count: int = 0
    root_web_area_found: bool = False
    in_page_scope_confirmed: bool = False
    in_page_candidate_count: int = 0
    candidate_count: int = 0
    prompt_input_candidate_found: bool = False
    send_button_candidate_found: bool = False
    attach_button_candidate_found: bool = False
    top_candidate_kind: str = ""
    top_candidate_score: int = 0
    top_candidate_is_browser_chrome: bool = False
    candidates: tuple[ComposerCandidate, ...] | list[ComposerCandidate] | list[dict[str, Any]] = ()
    filtered_candidates: tuple[ComposerCandidate, ...] | list[ComposerCandidate] | list[dict[str, Any]] = ()
    detector_report_path: str = ""
    targeted_json_path: str = ""
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_dom_automation_used: bool = False
    chatgpt_prompt_submitted: bool = False
    prompt_text_entered: bool = False
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
        payload["candidates"] = [_candidate_to_payload(item) for item in self.candidates]
        payload["filtered_candidates"] = [_candidate_to_payload(item) for item in self.filtered_candidates]
        return payload


def _candidate_to_payload(item: ComposerCandidate | dict[str, Any]) -> dict[str, Any]:
    if is_dataclass(item):
        return asdict(item)
    if isinstance(item, dict):
        return dict(item)
    raise TypeError(f"Unsupported composer candidate payload item: {type(item).__name__}")


def _candidate_from_payload(item: ComposerCandidate | dict[str, Any]) -> ComposerCandidate:
    if isinstance(item, ComposerCandidate):
        return item
    if isinstance(item, dict):
        allowed = {field_name for field_name in ComposerCandidate.__dataclass_fields__}
        return ComposerCandidate(**{key: item[key] for key in allowed if key in item})
    raise TypeError(f"Unsupported composer candidate item: {type(item).__name__}")


def normalize_candidates(items: tuple[ComposerCandidate, ...] | list[ComposerCandidate] | list[dict[str, Any]]) -> tuple[ComposerCandidate, ...]:
    return tuple(_candidate_from_payload(item) for item in items)


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


def _classify_candidate(control_type: str, class_name: str, name: str, automation_id: str, depth: int, is_page_scope: bool, is_chrome: bool) -> tuple[str, int, str]:
    text = " ".join([control_type, class_name, name, automation_id]).lower()
    if is_chrome:
        return "browser_chrome_filtered", 0, "browser_chrome_or_omnibox"
    score = 0
    kind = "none"
    if control_type in {"Edit", "Document", "Text", "Custom", "Pane"}:
        score += 10
    if is_page_scope:
        score += 20
    if any(word in text for word in _PROMPT_WORDS):
        kind = "prompt_input_candidate"
        score += 90
    elif any(word in text for word in _SEND_WORDS) and control_type in {"Button", "MenuItem", "Text"}:
        kind = "send_button_candidate"
        score += 75
    elif any(word in text for word in _ATTACH_WORDS):
        kind = "attach_button_candidate"
        score += 50
    elif is_page_scope and control_type in {"Edit", "Document", "Text", "Custom", "Pane"}:
        kind = "in_page_text_surface_candidate"
        score += 40
    elif control_type in {"Edit", "Document"}:
        kind = "generic_text_input_candidate"
        score += 20
    if kind == "none" or score <= 0:
        return "none", 0, ""
    return kind, score, ""


def _scan_candidates(window: object, *, max_depth: int, max_controls: int) -> tuple[list[ComposerCandidate], list[ComposerCandidate], int, int, bool]:
    accepted: list[ComposerCandidate] = []
    filtered: list[ComposerCandidate] = []
    queue: list[tuple[object, int, bool]] = [(window, 0, False)]
    scanned = 0
    max_seen = 0
    root_web_area_found = False
    while queue and scanned < max_controls:
        control, depth, inherited_page_scope = queue.pop(0)
        scanned += 1
        max_seen = max(max_seen, depth)
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
        is_root = _is_root_web_area(control_type, class_name, raw_name, automation_id)
        is_page_scope = bool(inherited_page_scope or is_root)
        root_web_area_found = root_web_area_found or is_root
        is_chrome = _is_browser_chrome(control_type, class_name, raw_name, automation_id)
        kind, score, exclusion = _classify_candidate(control_type, class_name, raw_name, automation_id, depth, is_page_scope, is_chrome)
        if kind != "none":
            redacted, digest, length = safe_text(raw_name, control_type=control_type, max_chars=48)
            auto_redacted, _, _ = safe_text(automation_id, control_type="Button", max_chars=40)
            item = ComposerCandidate(
                index=len(accepted) + len(filtered),
                depth=depth,
                control_type=control_type,
                class_name=class_name,
                name_redacted=redacted,
                name_hash=digest,
                name_length=length,
                automation_id_redacted=auto_redacted,
                rectangle=_rect_text(control),
                candidate_kind=kind,
                candidate_score=score,
                is_browser_chrome=is_chrome,
                is_in_page_scope=is_page_scope,
                exclusion_reason=exclusion,
            )
            if is_chrome or kind == "browser_chrome_filtered":
                filtered.append(item)
            else:
                accepted.append(item)
        if depth >= max_depth:
            continue
        try:
            children = list(control.children())
        except Exception:
            children = []
        for child in children[: max(0, max_controls - scanned)]:
            queue.append((child, depth + 1, is_page_scope))
    accepted.sort(key=lambda item: (-item.candidate_score, item.index))
    filtered.sort(key=lambda item: (-item.candidate_score, item.index))
    return accepted, filtered, scanned, max_seen, root_web_area_found


def _write_report(path: Path, result: ComposerDetectorResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    candidates = normalize_candidates(result.candidates)
    filtered = normalize_candidates(result.filtered_candidates)
    lines = [
        "L26.6B in-page ChatGPT composer detector repair",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "chatgpt_prompt_submitted:false",
        "prompt_text_entered:false",
        "page_click_performed:false",
        "browser_chrome_candidates_filtered:true",
        "Only redacted candidate metadata is recorded.",
        "",
        f"classification: {result.classification}",
        f"chatgpt_accessible: {result.chatgpt_accessible}",
        f"root_web_area_found: {result.root_web_area_found}",
        f"in_page_scope_confirmed: {result.in_page_scope_confirmed}",
        f"candidate_count: {result.candidate_count}",
        f"in_page_candidate_count: {result.in_page_candidate_count}",
        f"browser_chrome_candidate_count: {result.browser_chrome_candidate_count}",
        f"prompt_input_candidate_found: {result.prompt_input_candidate_found}",
        f"send_button_candidate_found: {result.send_button_candidate_found}",
        "",
        "ACCEPTED IN-PAGE CANDIDATES",
        "---------------------------",
    ]
    for item in candidates:
        lines.append(f"[{item.index}] kind={item.candidate_kind} score={item.candidate_score} depth={item.depth} page={item.is_in_page_scope} type={item.control_type!r} class={item.class_name!r} name={item.name_redacted!r} hash={item.name_hash} rect={item.rectangle!r}")
    lines.extend(["", "FILTERED BROWSER CHROME CANDIDATES", "----------------------------------"])
    for item in filtered:
        lines.append(f"[{item.index}] kind={item.candidate_kind} depth={item.depth} type={item.control_type!r} class={item.class_name!r} name={item.name_redacted!r} reason={item.exclusion_reason}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: ComposerDetectorResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_06_composer_detector(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 8.0, max_depth: int = 14, max_controls: int = 900) -> ComposerDetectorResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_06_composer_detector_result.json"
    report_path = out_dir / "normal_edge_l26_06_composer_detector_report.txt"
    targeted_dir = out_dir / "targeted_classifier"
    targeted_json = targeted_dir / "normal_edge_l26_05a_targeted_classification_result.json"

    targeted = run_l26_05a_targeted_classifier(output_dir=targeted_dir, target_url=target_url, start_if_missing=start_if_missing, settle_seconds=settle_seconds)
    targeted_payload = targeted.to_payload()
    classification = str(targeted_payload.get("classification", "unknown"))
    sequence_completed = bool(targeted_payload.get("targeted_sequence_completed"))
    accessible = classification == "accessible"

    if not sequence_completed or not accessible:
        result = ComposerDetectorResult(targeted_sequence_completed=sequence_completed, classification=classification, chatgpt_accessible=accessible, candidate_report_written=True, targeted_json_path=str(targeted_json), detector_report_path=str(report_path), result="FAIL", failure_layer="targeted_accessibility_gate", error=f"Targeted classification must be accessible before composer detection; got {classification!r}.")
        _write_report(report_path, result)
        _write_json(json_path, result)
        return result

    try:
        import pywinauto  # type: ignore
        edge_pids = edge_process_ids()
        desktop = pywinauto.Desktop(backend="uia")
        _candidates, wrappers = discover_edge_windows(desktop, edge_pids)
        if not wrappers:
            raise RuntimeError("No normal Edge window wrappers discovered after targeted classification.")
        window = wrappers[0]
        window.set_focus()
        candidate_records, filtered_records, scanned, max_seen, root_found = _scan_candidates(window, max_depth=max_depth, max_controls=max_controls)
        scan_completed = True
        scan_error = ""
    except Exception as exc:
        candidate_records = []
        filtered_records = []
        scanned = 0
        max_seen = 0
        root_found = False
        scan_completed = False
        scan_error = f"{type(exc).__name__}: {exc}"

    in_page_records = [item for item in candidate_records if item.is_in_page_scope and not item.is_browser_chrome]
    prompt_found = any(item.candidate_kind in {"prompt_input_candidate", "in_page_text_surface_candidate"} for item in in_page_records)
    send_found = any(item.candidate_kind == "send_button_candidate" for item in in_page_records)
    attach_found = any(item.candidate_kind == "attach_button_candidate" for item in in_page_records)
    top = in_page_records[0] if in_page_records else None
    top_kind = top.candidate_kind if top else ""
    top_score = top.candidate_score if top else 0
    top_is_chrome = bool(top.is_browser_chrome) if top else False
    result_pass = bool(scan_completed and sequence_completed and accessible and root_found and filtered_records is not None and not top_is_chrome)

    result = ComposerDetectorResult(
        targeted_sequence_completed=sequence_completed,
        classification=classification,
        chatgpt_accessible=accessible,
        composer_scan_completed=scan_completed,
        candidate_report_written=True,
        controls_scanned=scanned,
        max_depth_observed=max_seen,
        browser_chrome_candidates_filtered=True,
        browser_chrome_candidate_count=len(filtered_records),
        root_web_area_found=root_found,
        in_page_scope_confirmed=bool(root_found or in_page_records),
        in_page_candidate_count=len(in_page_records),
        candidate_count=len(candidate_records),
        prompt_input_candidate_found=prompt_found,
        send_button_candidate_found=send_found,
        attach_button_candidate_found=attach_found,
        top_candidate_kind=top_kind,
        top_candidate_score=top_score,
        top_candidate_is_browser_chrome=top_is_chrome,
        candidates=tuple(in_page_records[:80]),
        filtered_candidates=tuple(filtered_records[:40]),
        detector_report_path=str(report_path),
        targeted_json_path=str(targeted_json),
        result="PASS" if result_pass else "FAIL",
        failure_layer="" if result_pass else "in_page_composer_scan",
        error="" if result_pass else scan_error,
    )
    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_06_acceptance(result: ComposerDetectorResult) -> None:
    payload = result.to_payload()
    required_true = ["targeted_sequence_completed", "chatgpt_accessible", "composer_scan_completed", "candidate_report_written", "browser_chrome_candidates_filtered", "in_page_scope_confirmed"]
    required_false = ["webdriver_used", "selenium_imported", "cloudflare_bypass_attempted", "browser_dom_automation_used", "chatgpt_prompt_submitted", "prompt_text_entered", "page_click_performed", "download_click_performed", "run_package_invoked", "pasteback_or_send_performed", "conversation_text_logged", "full_conversation_text_logged", "top_candidate_is_browser_chrome"]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if payload.get("classification") != "accessible":
        missing_true.append("classification_accessible")
    if payload.get("controls_scanned", 0) < 1:
        missing_true.append("controls_scanned>=1")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.6B acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
