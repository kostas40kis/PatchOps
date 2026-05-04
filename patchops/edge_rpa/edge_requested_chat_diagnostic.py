from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.edge_rpa.edge_navigation_proof import run_l26_04_navigation_proof
from patchops.edge_rpa.edge_uia_tree_report import safe_text
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids, ensure_edge_running

PATCH_NAME = "l26_10b_requested_chat_targeting_diagnostic_repair"
REQUESTED_CHAT_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"

_PROMPT_WORDS = ("prompt-textarea", "prosemirror", "chat with chatgpt", "message chatgpt", "ask anything", "send a message")
_SEND_WORDS = ("send", "submit")
_ATTACH_WORDS = ("attach", "upload", "add photos", "add files")
_LOGIN_WORDS = ("log in", "login", "sign in", "sign up", "continue with google", "continue with microsoft")
_CHALLENGE_WORDS = ("cloudflare", "captcha", "verify you are human", "checking if the site connection is secure", "security check", "human verification")
_CHROME_WORDS = ("omnibox", "address and search bar", "search or enter web address", "favorites bar", "extensions", "tab strip", "toolbar")


@dataclass(frozen=True)
class DiagnosticCandidate:
    index: int
    depth: int
    control_type: str
    class_name_redacted: str
    name_redacted: str
    name_hash: str
    name_length: int
    automation_id_redacted: str
    rectangle: str
    candidate_kind: str
    candidate_score: int
    is_browser_chrome: bool
    is_in_page_scope: bool


@dataclass(frozen=True)
class RequestedChatDiagnosticResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    target_url_is_requested_chat: bool = False
    target_url_hash: str = ""
    diagnostic_completed: bool = False
    controlled_navigation_attempted: bool = False
    navigation_json_written: bool = False
    edge_window_attached: bool = False
    edge_window_focused: bool = False
    title_observed: bool = False
    title_hash: str = ""
    title_length: int = 0
    title_mentions_chatgpt: bool = False
    bounded_tree_scanned: bool = False
    controls_scanned: int = 0
    max_depth_observed: int = 0
    root_web_area_found: bool = False
    composer_candidate_found: bool = False
    composer_candidate_count: int = 0
    safe_composer_focus_candidate_found: bool = False
    send_button_candidate_found: bool = False
    attach_button_candidate_found: bool = False
    login_indicator_found: bool = False
    challenge_indicator_found: bool = False
    requested_chat_loaded_likely: bool = False
    diagnostic_classification: str = "unknown"
    recommended_next_patch: str = ""
    candidates: tuple[DiagnosticCandidate, ...] = ()
    diagnostic_report_path: str = ""
    diagnostic_json_path: str = ""
    navigation_json_path: str = ""
    report_upload_attempted: bool = False
    file_attach_attempted: bool = False
    clipboard_prompt_set: bool = False
    prompt_pasted: bool = False
    enter_key_sent: bool = False
    send_submit_performed: bool = False
    chatgpt_prompt_submitted: bool = False
    page_click_performed: bool = False
    download_click_performed: bool = False
    run_package_invoked: bool = False
    pasteback_or_send_performed: bool = False
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    prompt_text_logged: bool = False
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_dom_automation_used: bool = False
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["candidates"] = [asdict(item) for item in self.candidates]
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


def _window_title_raw(window: object) -> str:
    for attr in ("window_text", "texts"):
        try:
            value = getattr(window, attr)()
            if isinstance(value, list):
                return str(value[0]) if value else ""
            return str(value)
        except Exception:
            continue
    try:
        return str(window.element_info.name)
    except Exception:
        return ""


def _contains_any(text: str, words: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(word in low for word in words)


def _is_browser_chrome(control_type: str, class_name: str, name: str, automation_id: str) -> bool:
    text = " ".join([control_type, class_name, name, automation_id]).lower()
    return _contains_any(text, _CHROME_WORDS) or (automation_id.startswith("view_") and ("address" in text or "omnibox" in text))


def _is_root_web_area(control_type: str, class_name: str, name: str, automation_id: str) -> bool:
    text = " ".join([control_type, class_name, name, automation_id]).lower()
    return automation_id == "RootWebArea" or "rootwebarea" in text or control_type == "Document"


def classify_node(control_type: str, class_name: str, name: str, automation_id: str, *, depth: int, in_page_scope: bool) -> tuple[str, int, bool]:
    text = " ".join([control_type, class_name, name, automation_id]).lower()
    chrome = _is_browser_chrome(control_type, class_name, name, automation_id)
    if chrome:
        return "browser_chrome", 0, True
    if _contains_any(text, _CHALLENGE_WORDS):
        return "challenge_indicator", 100, False
    if _contains_any(text, _LOGIN_WORDS):
        return "login_indicator", 90, False
    score = 0
    if in_page_scope:
        score += 25
    if automation_id == "prompt-textarea":
        return "composer_prompt_textarea", score + 140, False
    if "prosemirror" in class_name.lower():
        return "composer_prosemirror", score + 120, False
    if _contains_any(text, _PROMPT_WORDS):
        return "composer_text_candidate", score + 100, False
    if _contains_any(text, _SEND_WORDS) and control_type in {"Button", "Text", "MenuItem"}:
        return "send_button_candidate", score + 70, False
    if _contains_any(text, _ATTACH_WORDS):
        return "attach_button_candidate", score + 55, False
    if in_page_scope and control_type in {"Edit", "Document", "Custom", "Pane", "Text"}:
        return "generic_in_page_surface", score + 25, False
    return "none", 0, False


def _scan_tree(window: object, *, max_depth: int, max_controls: int) -> tuple[list[DiagnosticCandidate], dict[str, Any]]:
    candidates: list[DiagnosticCandidate] = []
    queue: list[tuple[object, int, bool]] = [(window, 0, False)]
    scanned = 0
    max_seen = 0
    root_web_area_found = False
    login = False
    challenge = False
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
        in_page = bool(inherited_page_scope or is_root)
        root_web_area_found = root_web_area_found or is_root
        kind, score, chrome = classify_node(control_type, class_name, raw_name, automation_id, depth=depth, in_page_scope=in_page)
        login = login or kind == "login_indicator"
        challenge = challenge or kind == "challenge_indicator"
        if kind != "none":
            name_redacted, name_hash, name_len = safe_text(raw_name, control_type=control_type, max_chars=48)
            class_redacted, _, _ = safe_text(class_name, control_type="Button", max_chars=80)
            auto_redacted, _, _ = safe_text(automation_id, control_type="Button", max_chars=48)
            candidates.append(DiagnosticCandidate(
                index=len(candidates),
                depth=depth,
                control_type=control_type,
                class_name_redacted=class_redacted,
                name_redacted=name_redacted,
                name_hash=name_hash,
                name_length=name_len,
                automation_id_redacted=auto_redacted,
                rectangle=_rect_text(control),
                candidate_kind=kind,
                candidate_score=score,
                is_browser_chrome=chrome,
                is_in_page_scope=in_page,
            ))
        if depth >= max_depth:
            continue
        try:
            children = list(control.children())
        except Exception:
            children = []
        for child in children[: max(0, max_controls - scanned)]:
            queue.append((child, depth + 1, in_page))
    candidates.sort(key=lambda item: (-item.candidate_score, item.index))
    stats = {
        "controls_scanned": scanned,
        "max_depth_observed": max_seen,
        "root_web_area_found": root_web_area_found,
        "login_indicator_found": login,
        "challenge_indicator_found": challenge,
    }
    return candidates, stats


def _classification(*, title_mentions_chatgpt: bool, root_found: bool, composer_found: bool, safe_focus_candidate: bool, login: bool, challenge: bool) -> tuple[str, str]:
    if challenge:
        return "human_challenge_required", "stop_for_manual_challenge_no_bypass"
    if login:
        return "login_required", "operator_login_then_rerun_requested_chat_diagnostic"
    if safe_focus_candidate:
        return "composer_reachable", "resume_l26_10_send_disabled_gate_or_l26_11_report_upload_dry_run"
    if composer_found:
        return "composer_present_but_not_safe_focus_candidate", "repair_focus_candidate_selector_for_requested_chat"
    if root_found or title_mentions_chatgpt:
        return "chatgpt_loaded_no_composer_found", "increase_settle_or_add_requested_chat_specific_selector_scan"
    return "requested_chat_not_loaded_or_wrong_surface", "repair_navigation_observation_before_upload"


def _write_report(path: Path, result: RequestedChatDiagnosticResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.10B requested-chat targeting diagnostic repair",
        "report_upload_attempted:false",
        "file_attach_attempted:false",
        "clipboard_prompt_set:false",
        "prompt_pasted:false",
        "enter_key_sent:false",
        "chatgpt_prompt_submitted:false",
        "page_click_performed:false",
        "download_click_performed:false",
        "run_package_invoked:false",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "prompt_text_logged:false",
        "Only redacted candidate metadata and hashes/lengths are recorded.",
        "",
        f"target_url_is_requested_chat: {result.target_url_is_requested_chat}",
        f"target_url_hash: {result.target_url_hash}",
        f"diagnostic_completed: {result.diagnostic_completed}",
        f"controlled_navigation_attempted: {result.controlled_navigation_attempted}",
        f"navigation_json_written: {result.navigation_json_written}",
        f"edge_window_attached: {result.edge_window_attached}",
        f"title_observed: {result.title_observed}",
        f"title_hash: {result.title_hash}",
        f"title_length: {result.title_length}",
        f"title_mentions_chatgpt: {result.title_mentions_chatgpt}",
        f"bounded_tree_scanned: {result.bounded_tree_scanned}",
        f"controls_scanned: {result.controls_scanned}",
        f"max_depth_observed: {result.max_depth_observed}",
        f"root_web_area_found: {result.root_web_area_found}",
        f"composer_candidate_found: {result.composer_candidate_found}",
        f"composer_candidate_count: {result.composer_candidate_count}",
        f"safe_composer_focus_candidate_found: {result.safe_composer_focus_candidate_found}",
        f"send_button_candidate_found: {result.send_button_candidate_found}",
        f"attach_button_candidate_found: {result.attach_button_candidate_found}",
        f"login_indicator_found: {result.login_indicator_found}",
        f"challenge_indicator_found: {result.challenge_indicator_found}",
        f"diagnostic_classification: {result.diagnostic_classification}",
        f"recommended_next_patch: {result.recommended_next_patch}",
        "",
        "TOP REDACTED CANDIDATES",
        "-----------------------",
    ]
    for item in result.candidates[:40]:
        lines.append(
            f"[{item.index}] kind={item.candidate_kind} score={item.candidate_score} depth={item.depth} "
            f"page={item.is_in_page_scope} chrome={item.is_browser_chrome} type={item.control_type!r} "
            f"class={item.class_name_redacted!r} name={item.name_redacted!r} hash={item.name_hash} len={item.name_length} "
            f"automation_id={item.automation_id_redacted!r} rect={item.rectangle!r}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: RequestedChatDiagnosticResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_10b_requested_chat_diagnostic(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 12.0, max_depth: int = 16, max_controls: int = 1400) -> RequestedChatDiagnosticResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_10b_requested_chat_diagnostic_result.json"
    report_path = out_dir / "normal_edge_l26_10b_requested_chat_diagnostic_report.txt"
    navigation_dir = out_dir / "requested_chat_navigation"
    navigation_json = navigation_dir / "normal_edge_l26_04_navigation_result.json"
    target_is_requested = target_url.rstrip("/") == REQUESTED_CHAT_URL.rstrip("/")

    try:
        if not target_is_requested:
            raise RuntimeError("L26.10B must target the requested project chat URL.")
        nav_result = run_l26_04_navigation_proof(output_dir=navigation_dir, target_url=target_url, start_if_missing=start_if_missing, settle_seconds=settle_seconds)
        navigation_json_written = navigation_json.exists()
        time.sleep(1.0)
        import pywinauto  # type: ignore
        ensure_edge_running(start_if_missing=start_if_missing)
        edge_pids = edge_process_ids()
        desktop = pywinauto.Desktop(backend="uia")
        _windows, wrappers = discover_edge_windows(desktop, edge_pids)
        if not wrappers:
            raise RuntimeError("No normal Edge window wrappers discovered after requested-chat navigation.")
        window = wrappers[0]
        focused = False
        try:
            window.set_focus()
            focused = True
        except Exception:
            focused = False
        raw_title = _window_title_raw(window)
        title_hash = _hash_text(raw_title)
        title_length = len(raw_title)
        title_mentions_chatgpt = "chatgpt" in raw_title.lower()
        candidates, stats = _scan_tree(window, max_depth=max_depth, max_controls=max_controls)
        composer_records = [item for item in candidates if item.candidate_kind.startswith("composer") or item.candidate_kind == "generic_in_page_surface"]
        safe_records = [item for item in composer_records if item.is_in_page_scope and not item.is_browser_chrome and item.candidate_score >= 90]
        send_records = [item for item in candidates if item.candidate_kind == "send_button_candidate" and item.is_in_page_scope and not item.is_browser_chrome]
        attach_records = [item for item in candidates if item.candidate_kind == "attach_button_candidate" and item.is_in_page_scope and not item.is_browser_chrome]
        diagnostic_class, next_patch = _classification(
            title_mentions_chatgpt=title_mentions_chatgpt,
            root_found=bool(stats["root_web_area_found"]),
            composer_found=bool(composer_records),
            safe_focus_candidate=bool(safe_records),
            login=bool(stats["login_indicator_found"]),
            challenge=bool(stats["challenge_indicator_found"]),
        )
        requested_loaded_likely = bool(title_mentions_chatgpt or stats["root_web_area_found"] or composer_records)
        result = RequestedChatDiagnosticResult(
            target_url_is_requested_chat=True,
            target_url_hash=_hash_text(target_url),
            diagnostic_completed=True,
            controlled_navigation_attempted=True,
            navigation_json_written=navigation_json_written,
            edge_window_attached=True,
            edge_window_focused=focused,
            title_observed=title_length > 0,
            title_hash=title_hash,
            title_length=title_length,
            title_mentions_chatgpt=title_mentions_chatgpt,
            bounded_tree_scanned=True,
            controls_scanned=int(stats["controls_scanned"]),
            max_depth_observed=int(stats["max_depth_observed"]),
            root_web_area_found=bool(stats["root_web_area_found"]),
            composer_candidate_found=bool(composer_records),
            composer_candidate_count=len(composer_records),
            safe_composer_focus_candidate_found=bool(safe_records),
            send_button_candidate_found=bool(send_records),
            attach_button_candidate_found=bool(attach_records),
            login_indicator_found=bool(stats["login_indicator_found"]),
            challenge_indicator_found=bool(stats["challenge_indicator_found"]),
            requested_chat_loaded_likely=requested_loaded_likely,
            diagnostic_classification=diagnostic_class,
            recommended_next_patch=next_patch,
            candidates=tuple(candidates[:80]),
            diagnostic_report_path=str(report_path),
            diagnostic_json_path=str(json_path),
            navigation_json_path=str(navigation_json),
            result="PASS",
        )
    except Exception as exc:
        result = RequestedChatDiagnosticResult(
            target_url_is_requested_chat=target_is_requested,
            target_url_hash=_hash_text(target_url),
            controlled_navigation_attempted=True,
            diagnostic_report_path=str(report_path),
            diagnostic_json_path=str(json_path),
            navigation_json_path=str(navigation_json),
            result="FAIL",
            failure_layer="requested_chat_targeting_diagnostic",
            error=f"{type(exc).__name__}: {exc}",
        )
    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_10b_acceptance(result: RequestedChatDiagnosticResult) -> None:
    payload = result.to_payload()
    required_true = [
        "target_url_is_requested_chat",
        "diagnostic_completed",
        "controlled_navigation_attempted",
        "navigation_json_written",
        "edge_window_attached",
        "bounded_tree_scanned",
    ]
    required_false = [
        "report_upload_attempted",
        "file_attach_attempted",
        "clipboard_prompt_set",
        "prompt_pasted",
        "enter_key_sent",
        "send_submit_performed",
        "chatgpt_prompt_submitted",
        "page_click_performed",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
        "full_conversation_text_logged",
        "prompt_text_logged",
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if payload.get("controls_scanned", 0) < 1:
        missing_true.append("controls_scanned>=1")
    if not payload.get("diagnostic_classification") or payload.get("diagnostic_classification") == "unknown":
        missing_true.append("diagnostic_classification_nonunknown")
    if not payload.get("recommended_next_patch"):
        missing_true.append("recommended_next_patch_nonempty")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.10B acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
