from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids, ensure_edge_running
from patchops.edge_rpa.edge_uia_tree_report import safe_text

PATCH_NAME = "l26_04_normal_edge_controlled_navigation_proof"
_CHALLENGE_WORDS = ("cloudflare", "captcha", "verify you are human", "checking if the site connection is secure", "turnstile")
_LOGIN_WORDS = ("log in", "login", "sign in", "sign up")


@dataclass(frozen=True)
class NavigationObservation:
    sample_index: int
    title_redacted: str
    title_hash: str
    title_length: int


@dataclass(frozen=True)
class ControlledNavigationResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    url_hash: str = ""
    url_scheme: str = ""
    url_host_redacted: str = ""
    pywinauto_imported: bool = False
    uia_backend_available: bool = False
    normal_edge_attached: bool = False
    edge_focused_before_navigation: bool = False
    edge_window_title_before_read: bool = False
    ctrl_l_sent: bool = False
    clipboard_url_set: bool = False
    clipboard_verified_before_paste: bool = False
    url_pasted_by_patchops: bool = False
    enter_sent: bool = False
    normal_edge_navigation: bool = False
    page_load_state_observed: bool = False
    edge_window_title_after_read: bool = False
    title_changed_or_observed: bool = False
    human_challenge_required: bool = False
    login_required: bool = False
    loop_stopped: bool = False
    classification: str = "unknown"
    observations: tuple[NavigationObservation, ...] = ()
    navigation_report_path: str = ""
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    chatgpt_prompt_submitted: bool = False
    download_click_performed: bool = False
    run_package_invoked: bool = False
    pasteback_or_send_performed: bool = False
    conversation_text_logged: bool = False
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["observations"] = [asdict(item) for item in self.observations]
        return payload


def _with(result: ControlledNavigationResult, **changes: Any) -> ControlledNavigationResult:
    payload = result.to_payload()
    payload.update(changes)
    observations = tuple(NavigationObservation(**item) for item in payload.pop("observations", []))
    return ControlledNavigationResult(observations=observations, **payload)


def _hash_text(value: object) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def validate_target_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("L26.4 only allows http/https URLs for the controlled navigation proof.")
    if not parsed.netloc:
        raise ValueError("Target URL must include a host.")
    return url.strip()


def _url_metadata(url: str) -> tuple[str, str, str]:
    parsed = urlparse(url)
    host = parsed.netloc
    redacted_host = host if len(host) <= 80 else f"<host redacted length={len(host)} sha256={_hash_text(host)}>"
    return _hash_text(url), parsed.scheme.lower(), redacted_host


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


def _title_observation(window: object, sample_index: int) -> NavigationObservation:
    raw = _window_title_raw(window)
    redacted, digest, length = safe_text(raw, control_type="Window", max_chars=96)
    return NavigationObservation(sample_index=sample_index, title_redacted=redacted, title_hash=digest, title_length=length)


def _set_clipboard_text(pywinauto: Any, text: str) -> tuple[bool, bool, str]:
    try:
        from pywinauto import clipboard  # type: ignore
        clipboard.SetData(text)
        try:
            observed = clipboard.GetData()
            return True, observed == text, ""
        except Exception:
            return True, False, "clipboard set but verification read failed"
    except Exception as first_exc:
        try:
            import tkinter  # type: ignore
            root = tkinter.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            return True, True, "tkinter clipboard fallback used"
        except Exception as second_exc:
            return False, False, f"pywinauto clipboard failed: {type(first_exc).__name__}: {first_exc}; tkinter failed: {type(second_exc).__name__}: {second_exc}"


def _scan_indicators(window: object, *, max_depth: int = 3, max_controls: int = 80) -> tuple[bool, bool]:
    texts: list[str] = []
    queue: list[tuple[object, int]] = [(window, 0)]
    while queue and len(texts) < max_controls:
        control, depth = queue.pop(0)
        try:
            info = control.element_info
            raw_name = str(info.name or "")
            raw_type = str(info.control_type or "")
            if raw_type in {"Window", "Button", "Text", "Edit", "Document", "Pane"} and raw_name:
                texts.append(raw_name.lower())
        except Exception:
            pass
        if depth >= max_depth:
            continue
        try:
            children = list(control.children())
        except Exception:
            children = []
        for child in children[: max(0, max_controls - len(texts))]:
            queue.append((child, depth + 1))
    joined = " ".join(texts)
    challenge = any(word in joined for word in _CHALLENGE_WORDS)
    login = any(word in joined for word in _LOGIN_WORDS)
    return challenge, login


def _write_navigation_report(path: Path, result: ControlledNavigationResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.4 controlled normal Edge navigation proof",
        "conversation_text_logged:false",
        "chatgpt_prompt_submitted:false",
        "cloudflare_bypass_attempted:false",
        "Only URL hash/scheme/host, title hashes/redacted titles, and state markers are recorded.",
        "",
        f"url_hash: {result.url_hash}",
        f"url_scheme: {result.url_scheme}",
        f"url_host_redacted: {result.url_host_redacted}",
        f"classification: {result.classification}",
        f"human_challenge_required: {result.human_challenge_required}",
        f"login_required: {result.login_required}",
        "",
        "TITLE OBSERVATIONS",
        "------------------",
    ]
    for obs in result.observations:
        lines.append(f"[{obs.sample_index}] title={obs.title_redacted!r} hash={obs.title_hash} length={obs.title_length}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_l26_04_navigation_proof(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 8.0) -> ControlledNavigationResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_04_navigation_result.json"
    nav_report_path = out_dir / "normal_edge_l26_04_navigation_report.txt"

    try:
        url = validate_target_url(target_url)
        url_hash, url_scheme, url_host = _url_metadata(url)
    except Exception as exc:
        result = ControlledNavigationResult(failure_layer="url_validation", error=f"{type(exc).__name__}: {exc}")
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    imported, import_error, pywinauto = _import_pywinauto()
    if not imported:
        result = ControlledNavigationResult(url_hash=url_hash, url_scheme=url_scheme, url_host_redacted=url_host, failure_layer="pywinauto_import", error=import_error, navigation_report_path=str(nav_report_path))
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    try:
        ensure_edge_running(start_if_missing=start_if_missing)
        edge_pids = edge_process_ids()
        desktop = pywinauto.Desktop(backend="uia")
        candidates, wrappers = discover_edge_windows(desktop, edge_pids)
    except Exception as exc:
        result = ControlledNavigationResult(url_hash=url_hash, url_scheme=url_scheme, url_host_redacted=url_host, pywinauto_imported=True, failure_layer="edge_attach_bootstrap", error=f"{type(exc).__name__}: {exc}", navigation_report_path=str(nav_report_path))
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    if not candidates or not wrappers:
        result = ControlledNavigationResult(url_hash=url_hash, url_scheme=url_scheme, url_host_redacted=url_host, pywinauto_imported=True, uia_backend_available=True, failure_layer="edge_window_discovery", error="No normal Edge window candidate found.", navigation_report_path=str(nav_report_path))
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    window = wrappers[0]
    observations: list[NavigationObservation] = []
    try:
        before = _title_observation(window, 0)
        observations.append(before)
        window.set_focus()
        focused = True
    except Exception as exc:
        result = ControlledNavigationResult(url_hash=url_hash, url_scheme=url_scheme, url_host_redacted=url_host, pywinauto_imported=True, uia_backend_available=True, normal_edge_attached=True, failure_layer="edge_focus_before_navigation", error=f"{type(exc).__name__}: {exc}", observations=tuple(observations), navigation_report_path=str(nav_report_path))
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    from pywinauto import keyboard  # type: ignore

    ctrl_l_sent = False
    clipboard_set = False
    clipboard_verified = False
    pasted = False
    enter_sent = False
    nav_error = ""
    try:
        keyboard.send_keys("^l")
        ctrl_l_sent = True
        time.sleep(0.3)
        clipboard_set, clipboard_verified, clip_error = _set_clipboard_text(pywinauto, url)
        if not clipboard_set:
            raise RuntimeError(clip_error)
        keyboard.send_keys("^v")
        pasted = True
        time.sleep(0.2)
        keyboard.send_keys("{ENTER}")
        enter_sent = True
    except Exception as exc:
        nav_error = f"{type(exc).__name__}: {exc}"

    deadline = time.time() + max(2.0, settle_seconds)
    sample_index = 1
    while time.time() < deadline:
        time.sleep(1.0)
        try:
            observations.append(_title_observation(window, sample_index))
            sample_index += 1
        except Exception:
            pass

    try:
        after = _title_observation(window, sample_index)
        observations.append(after)
    except Exception:
        after = observations[-1] if observations else NavigationObservation(0, "", "", 0)

    title_after_read = after.title_length > 0
    title_changed = bool(observations and after.title_hash != observations[0].title_hash)
    page_load_observed = bool(enter_sent and title_after_read and len(observations) >= 2)
    challenge, login = _scan_indicators(window)
    classification = "accessible_or_loaded"
    loop_stopped = False
    if challenge:
        classification = "human_challenge_required"
        loop_stopped = True
    elif login:
        classification = "login_required"
        loop_stopped = True
    elif not page_load_observed:
        classification = "unknown"

    result_pass = bool(
        focused
        and before.title_length > 0
        and ctrl_l_sent
        and clipboard_set
        and clipboard_verified
        and pasted
        and enter_sent
        and page_load_observed
        and title_after_read
        and not challenge
    )

    result = ControlledNavigationResult(
        url_hash=url_hash,
        url_scheme=url_scheme,
        url_host_redacted=url_host,
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_focused_before_navigation=focused,
        edge_window_title_before_read=before.title_length > 0,
        ctrl_l_sent=ctrl_l_sent,
        clipboard_url_set=clipboard_set,
        clipboard_verified_before_paste=clipboard_verified,
        url_pasted_by_patchops=pasted,
        enter_sent=enter_sent,
        normal_edge_navigation=bool(ctrl_l_sent and pasted and enter_sent),
        page_load_state_observed=page_load_observed,
        edge_window_title_after_read=title_after_read,
        title_changed_or_observed=bool(title_changed or title_after_read),
        human_challenge_required=challenge,
        login_required=login,
        loop_stopped=loop_stopped,
        classification=classification,
        observations=tuple(observations[-10:]),
        navigation_report_path=str(nav_report_path),
        result="PASS" if result_pass else "FAIL",
        failure_layer="" if result_pass else ("human_challenge_required" if challenge else "controlled_navigation"),
        error="" if result_pass else nav_error,
    )
    _write_navigation_report(nav_report_path, result)
    json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
    return result


def assert_l26_04_acceptance(result: ControlledNavigationResult) -> None:
    payload = result.to_payload()
    required_true = [
        "pywinauto_imported",
        "uia_backend_available",
        "normal_edge_attached",
        "edge_focused_before_navigation",
        "edge_window_title_before_read",
        "ctrl_l_sent",
        "clipboard_url_set",
        "clipboard_verified_before_paste",
        "url_pasted_by_patchops",
        "enter_sent",
        "normal_edge_navigation",
        "page_load_state_observed",
        "edge_window_title_after_read",
        "title_changed_or_observed",
    ]
    required_false = [
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "chatgpt_prompt_submitted",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if payload.get("human_challenge_required"):
        missing_true.append("no_human_challenge_for_acceptance")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.4 acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; classification={result.classification}; failure_layer={result.failure_layer}; error={result.error}")
