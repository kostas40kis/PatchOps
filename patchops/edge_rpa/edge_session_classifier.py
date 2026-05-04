from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids, ensure_edge_running
from patchops.edge_rpa.edge_uia_tree_report import safe_text

PATCH_NAME = "l26_05_chatgpt_accessibility_session_classifier"
_CLASSIFICATIONS = {"accessible", "login_required", "human_challenge_required", "unknown"}
_CHALLENGE_WORDS = (
    "cloudflare",
    "captcha",
    "verify you are human",
    "checking if the site connection is secure",
    "turnstile",
    "human verification",
    "security check",
)
_LOGIN_WORDS = ("log in", "login", "sign in", "sign up", "continue with google", "continue with microsoft")
_ACCESSIBLE_WORDS = ("chatgpt", "message chatgpt", "ask anything", "new chat", "temporary chat")


@dataclass(frozen=True)
class SessionIndicator:
    index: int
    control_type: str
    class_name: str
    name_redacted: str
    name_hash: str
    name_length: int
    indicator_kind: str
    indicator_score: int


@dataclass(frozen=True)
class ChatGptSessionClassificationResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    pywinauto_imported: bool = False
    uia_backend_available: bool = False
    normal_edge_attached: bool = False
    edge_focused: bool = False
    edge_window_title_read: bool = False
    title_redacted: str = ""
    title_hash: str = ""
    title_length: int = 0
    title_mentions_chatgpt: bool = False
    indicator_scan_completed: bool = False
    indicator_count: int = 0
    challenge_indicator_found: bool = False
    login_indicator_found: bool = False
    accessible_indicator_found: bool = False
    chatgpt_session_classified: bool = False
    classification: str = "unknown"
    human_challenge_required: bool = False
    login_required: bool = False
    loop_stopped: bool = False
    indicators: tuple[SessionIndicator, ...] = ()
    classifier_report_path: str = ""
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_navigation_performed: bool = False
    chatgpt_prompt_submitted: bool = False
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
        payload["indicators"] = [asdict(item) for item in self.indicators]
        return payload


def _with(result: ChatGptSessionClassificationResult, **changes: Any) -> ChatGptSessionClassificationResult:
    payload = result.to_payload()
    payload.update(changes)
    indicators = tuple(SessionIndicator(**item) for item in payload.pop("indicators", []))
    return ChatGptSessionClassificationResult(indicators=indicators, **payload)


def _hash_text(value: object) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def _import_pywinauto() -> tuple[bool, str, Any]:
    try:
        import pywinauto  # type: ignore
        return True, "", pywinauto
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}", None


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


def _info_text(info: object, name: str) -> str:
    try:
        value = getattr(info, name)
        return "" if value is None else str(value)
    except Exception:
        return ""


def classify_text(text: str) -> tuple[str, int]:
    low = text.lower()
    if any(word in low for word in _CHALLENGE_WORDS):
        return "challenge", 100
    if any(word in low for word in _LOGIN_WORDS):
        return "login", 80
    if any(word in low for word in _ACCESSIBLE_WORDS):
        return "accessible", 60
    return "none", 0


def _scan_indicators(window: object, *, max_depth: int, max_controls: int) -> tuple[list[SessionIndicator], bool, bool, bool]:
    indicators: list[SessionIndicator] = []
    queue: list[tuple[object, int]] = [(window, 0)]
    scanned = 0
    challenge = False
    login = False
    accessible = False
    while queue and scanned < max_controls:
        control, depth = queue.pop(0)
        scanned += 1
        try:
            info = control.element_info
            control_type = _info_text(info, "control_type")
            class_name = _info_text(info, "class_name")
            raw_name = _info_text(info, "name")
        except Exception:
            control_type = ""
            class_name = ""
            raw_name = ""
        indicator_kind, score = classify_text(" ".join([control_type, class_name, raw_name]))
        if indicator_kind != "none":
            redacted, digest, length = safe_text(raw_name, control_type=control_type, max_chars=48)
            indicators.append(SessionIndicator(
                index=len(indicators),
                control_type=control_type,
                class_name=class_name,
                name_redacted=redacted,
                name_hash=digest,
                name_length=length,
                indicator_kind=indicator_kind,
                indicator_score=score,
            ))
            challenge = challenge or indicator_kind == "challenge"
            login = login or indicator_kind == "login"
            accessible = accessible or indicator_kind == "accessible"
        if depth >= max_depth:
            continue
        try:
            children = list(control.children())
        except Exception:
            children = []
        for child in children[: max(0, max_controls - scanned)]:
            queue.append((child, depth + 1))
    return indicators, challenge, login, accessible


def _write_classifier_report(path: Path, result: ChatGptSessionClassificationResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.5 ChatGPT accessibility/session classifier",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "No navigation, prompt paste/send, clicking, downloads, run-package, or CAPTCHA bypass are performed.",
        "",
        f"classification: {result.classification}",
        f"human_challenge_required: {result.human_challenge_required}",
        f"login_required: {result.login_required}",
        f"loop_stopped: {result.loop_stopped}",
        f"title_redacted: {result.title_redacted}",
        f"title_hash: {result.title_hash}",
        f"title_length: {result.title_length}",
        "",
        "INDICATORS",
        "----------",
    ]
    for item in result.indicators:
        lines.append(
            f"[{item.index}] kind={item.indicator_kind} score={item.indicator_score} "
            f"type={item.control_type!r} class={item.class_name!r} "
            f"name={item.name_redacted!r} name_hash={item.name_hash} name_length={item.name_length}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_l26_05_session_classifier(*, output_dir: str | Path, start_if_missing: bool = True, max_depth: int = 5, max_controls: int = 220) -> ChatGptSessionClassificationResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_05_session_classification_result.json"
    report_path = out_dir / "normal_edge_l26_05_session_classifier_report.txt"

    imported, import_error, pywinauto = _import_pywinauto()
    if not imported:
        result = ChatGptSessionClassificationResult(failure_layer="pywinauto_import", error=import_error, classifier_report_path=str(report_path))
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    try:
        ensure_edge_running(start_if_missing=start_if_missing)
        edge_pids = edge_process_ids()
        desktop = pywinauto.Desktop(backend="uia")
        candidates, wrappers = discover_edge_windows(desktop, edge_pids)
    except Exception as exc:
        result = ChatGptSessionClassificationResult(pywinauto_imported=True, failure_layer="edge_attach_bootstrap", error=f"{type(exc).__name__}: {exc}", classifier_report_path=str(report_path))
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    if not candidates or not wrappers:
        result = ChatGptSessionClassificationResult(pywinauto_imported=True, uia_backend_available=True, failure_layer="edge_window_discovery", error="No normal Edge window candidate found.", classifier_report_path=str(report_path))
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    window = wrappers[0]
    focused = False
    focus_error = ""
    try:
        window.set_focus()
        focused = True
    except Exception as exc:
        focus_error = f"{type(exc).__name__}: {exc}"

    raw_title = _window_title_raw(window)
    title_redacted, title_hash, title_length = safe_text(raw_title, control_type="Window", max_chars=96)
    title_kind, _title_score = classify_text(raw_title)
    title_mentions_chatgpt = "chatgpt" in raw_title.lower()

    try:
        indicators, challenge, login, accessible = _scan_indicators(window, max_depth=max_depth, max_controls=max_controls)
        scan_completed = True
    except Exception as exc:
        indicators = []
        challenge = False
        login = False
        accessible = False
        scan_completed = False
        focus_error = f"{focus_error}; indicator scan failed: {type(exc).__name__}: {exc}".strip("; ")

    challenge = challenge or title_kind == "challenge"
    login = login or title_kind == "login"
    accessible = accessible or title_kind == "accessible" or title_mentions_chatgpt

    if challenge:
        classification = "human_challenge_required"
    elif login:
        classification = "login_required"
    elif accessible:
        classification = "accessible"
    else:
        classification = "unknown"

    loop_stopped = classification in {"human_challenge_required", "login_required"}
    result_pass = bool(focused and title_length > 0 and scan_completed and classification in _CLASSIFICATIONS)

    result = ChatGptSessionClassificationResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_focused=focused,
        edge_window_title_read=title_length > 0,
        title_redacted=title_redacted,
        title_hash=title_hash,
        title_length=title_length,
        title_mentions_chatgpt=title_mentions_chatgpt,
        indicator_scan_completed=scan_completed,
        indicator_count=len(indicators),
        challenge_indicator_found=challenge,
        login_indicator_found=login,
        accessible_indicator_found=accessible,
        chatgpt_session_classified=True,
        classification=classification,
        human_challenge_required=classification == "human_challenge_required",
        login_required=classification == "login_required",
        loop_stopped=loop_stopped,
        indicators=tuple(indicators[:80]),
        classifier_report_path=str(report_path),
        result="PASS" if result_pass else "FAIL",
        failure_layer="" if result_pass else "session_classification",
        error="" if result_pass else focus_error,
    )
    _write_classifier_report(report_path, result)
    json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
    return result


def assert_l26_05_acceptance(result: ChatGptSessionClassificationResult) -> None:
    payload = result.to_payload()
    required_true = [
        "pywinauto_imported",
        "uia_backend_available",
        "normal_edge_attached",
        "edge_focused",
        "edge_window_title_read",
        "indicator_scan_completed",
        "chatgpt_session_classified",
    ]
    required_false = [
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_navigation_performed",
        "chatgpt_prompt_submitted",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
        "full_conversation_text_logged",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if payload.get("classification") not in _CLASSIFICATIONS:
        missing_true.append("classification_allowed_value")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.5 acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; classification={result.classification}; failure_layer={result.failure_layer}; error={result.error}")
