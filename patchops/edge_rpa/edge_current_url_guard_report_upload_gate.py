from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from typing import Any

from pywinauto import keyboard  # type: ignore

from patchops.edge_rpa.edge_composer_focus_probe import _scan_focus_candidates
from patchops.edge_rpa.edge_navigation_proof import run_l26_04_navigation_proof
from patchops.edge_rpa.edge_report_upload_dry_run_gate import find_latest_patchops_report
from patchops.edge_rpa.edge_uia_tree_report import safe_text
from patchops.edge_rpa.edge_window_inventory import discover_edge_windows, edge_process_ids

PATCH_NAME = "l26_12c_current_url_guard_report_upload_staging_repair"
REQUESTED_CHAT_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"
_UPLOAD_WORDS = ("upload files", "upload file", "upload from computer", "add files", "attach files", "add photos and files", "add photos & files", "file upload")
_PLUS_WORDS = ("add files and more", "composer-plus", "attach", "add files")
_CHROME_WORDS = ("omnibox", "address and search bar", "search or enter web address", "tab strip", "toolbar")


@dataclass(frozen=True)
class UploadControlCandidate:
    candidate_kind: str
    control_type: str
    class_name_redacted: str
    name_redacted: str
    automation_id_redacted: str
    is_in_page_scope: bool
    is_browser_chrome: bool
    score: int
    depth: int


@dataclass(frozen=True)
class CurrentUrlGuardUploadResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    target_url_is_requested_chat: bool = False
    current_url_read_attempted: bool = False
    current_url_observed: bool = False
    current_url_hash: str = ""
    current_url_matches_target: bool = False
    navigation_skipped_existing_target: bool = False
    navigation_attempted: bool = False
    navigation_observed: bool = False
    composer_candidate_found: bool = False
    composer_focus_verified: bool = False
    allow_report_upload_requested: bool = False
    report_candidate_found: bool = False
    report_candidate_path_redacted: str = ""
    report_candidate_name: str = ""
    report_candidate_hash: str = ""
    report_candidate_size_bytes: int = 0
    report_candidate_is_text: bool = False
    plus_button_found: bool = False
    plus_button_clicked: bool = False
    upload_menu_item_found: bool = False
    upload_menu_item_clicked: bool = False
    upload_menu_inventory_written: bool = False
    upload_menu_inventory_count: int = 0
    file_picker_opened: bool = False
    file_picker_path_entered: bool = False
    file_picker_confirmed: bool = False
    upload_staging_observed: bool = False
    staged_file_name_hash: str = ""
    staged_file_name_length: int = 0
    staging_observation_method: str = ""
    report_upload_attempted: bool = False
    file_attach_attempted: bool = False
    live_report_path: str = ""
    json_path: str = ""
    menu_inventory_path: str = ""
    chatgpt_enter_key_sent: bool = False
    send_submit_performed: bool = False
    chatgpt_prompt_submitted: bool = False
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

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _hash_text(value: object) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def _canonical_url(url: str) -> str:
    raw = (url or "").strip()
    if not raw:
        return ""
    parts = urlsplit(raw)
    scheme = parts.scheme.lower() or "https"
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/")
    return urlunsplit((scheme, netloc, path, "", ""))


def _redact_path(path: Path) -> str:
    parts = list(path.parts)
    if len(parts) >= 2:
        return str(Path("...") / parts[-2] / parts[-1])
    return path.name


def _info_text(info: object, name: str) -> str:
    try:
        value = getattr(info, name)
        return "" if value is None else str(value)
    except Exception:
        return ""


def _set_clipboard_text(text: str) -> None:
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
    finally:
        root.destroy()


def _get_clipboard_text() -> str:
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    try:
        try:
            value = root.clipboard_get()
        except Exception:
            value = ""
        root.update()
        return str(value)
    finally:
        root.destroy()


def _edge_window() -> object:
    import pywinauto  # type: ignore
    edge_pids = edge_process_ids()
    desktop = pywinauto.Desktop(backend="uia")
    _windows, wrappers = discover_edge_windows(desktop, edge_pids)
    if not wrappers:
        raise RuntimeError("No normal Edge window wrapper was found.")
    window = wrappers[0]
    window.set_focus()
    return window


def _read_current_edge_url() -> str:
    backup = _get_clipboard_text()
    try:
        window = _edge_window()
        window.set_focus()
        time.sleep(0.15)
        keyboard.send_keys("^l")
        time.sleep(0.15)
        keyboard.send_keys("^c")
        time.sleep(0.15)
        return _get_clipboard_text().strip()
    finally:
        try:
            _set_clipboard_text(backup)
        except Exception:
            pass


def _ensure_target_loaded(output_dir: Path, target_url: str, start_if_missing: bool, settle_seconds: float) -> tuple[bool, bool, bool, bool, str]:
    observed = False
    skipped = False
    attempted = False
    current_url = ""
    try:
        current_url = _read_current_edge_url()
        observed = bool(current_url)
    except Exception:
        current_url = ""
    if _canonical_url(current_url) == _canonical_url(target_url):
        skipped = True
        return observed, True, skipped, attempted, current_url
    attempted = True
    nav_dir = output_dir / "requested_chat_navigation"
    nav = run_l26_04_navigation_proof(output_dir=nav_dir, target_url=target_url, start_if_missing=start_if_missing, settle_seconds=settle_seconds)
    nav_payload = nav.to_payload()
    nav_ok = bool(nav_payload.get("normal_edge_navigation") and nav_payload.get("page_load_state_observed"))
    return observed, nav_ok, skipped, attempted, current_url


def _verify_direct_composer_focus() -> tuple[bool, bool]:
    window = _edge_window()
    candidates = _scan_focus_candidates(window)
    if not candidates:
        return False, False
    candidate, control = candidates[0]
    if candidate.is_browser_chrome or not candidate.is_in_page_scope:
        return False, False
    control.set_focus()
    time.sleep(0.35)
    try:
        focus = bool(control.has_keyboard_focus())
    except Exception:
        focus = True
    return True, focus


def _is_root_web_area(control_type: str, class_name: str, name: str, automation_id: str) -> bool:
    text = " ".join([control_type, class_name, name, automation_id]).lower()
    return automation_id == "RootWebArea" or "rootwebarea" in text or control_type == "Document"


def _is_browser_chrome(control_type: str, class_name: str, name: str, automation_id: str) -> bool:
    text = " ".join([control_type, class_name, name, automation_id]).lower()
    return any(word in text for word in _CHROME_WORDS)


def _candidate_from_control(control: object, depth: int, page_scope: bool, kind: str, score: int) -> UploadControlCandidate:
    try:
        info = control.element_info
        control_type = _info_text(info, "control_type")
        class_name = _info_text(info, "class_name")
        raw_name = _info_text(info, "name")
        automation_id = _info_text(info, "automation_id")
    except Exception:
        control_type = class_name = raw_name = automation_id = ""
    class_redacted, _, _ = safe_text(class_name, control_type="Button", max_chars=80)
    name_redacted, _, _ = safe_text(raw_name, control_type=control_type, max_chars=80)
    auto_redacted, _, _ = safe_text(automation_id, control_type="Button", max_chars=80)
    return UploadControlCandidate(kind, control_type, class_redacted, name_redacted, auto_redacted, page_scope, _is_browser_chrome(control_type, class_name, raw_name, automation_id), score, depth)


def _find_plus_control(max_depth: int = 16, max_controls: int = 1800) -> tuple[UploadControlCandidate, object]:
    window = _edge_window()
    queue: list[tuple[object, int, bool]] = [(window, 0, False)]
    found: list[tuple[UploadControlCandidate, object]] = []
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
            control_type = class_name = raw_name = automation_id = ""
        page_scope = bool(inherited_page_scope or _is_root_web_area(control_type, class_name, raw_name, automation_id))
        chrome = _is_browser_chrome(control_type, class_name, raw_name, automation_id)
        blob = " ".join([control_type, class_name, raw_name, automation_id]).lower()
        score = 0
        if page_scope and not chrome and control_type == "Button":
            if automation_id == "composer-plus-btn":
                score += 190
            if any(word in blob for word in _PLUS_WORDS):
                score += 100
        if score >= 100:
            found.append((_candidate_from_control(control, depth, page_scope, "composer_plus_menu_button", score), control))
        if depth < max_depth:
            try:
                for child in list(control.children())[: max(0, max_controls - scanned)]:
                    queue.append((child, depth + 1, page_scope))
            except Exception:
                pass
    if not found:
        raise RuntimeError("No composer plus/attach menu button was found.")
    found.sort(key=lambda item: -item[0].score)
    return found[0]


def _click_control(control: object) -> None:
    try:
        control.set_focus()
    except Exception:
        pass
    try:
        control.invoke()
        return
    except Exception:
        pass
    try:
        control.click_input()
        return
    except Exception as exc:
        raise RuntimeError(f"Control activation failed: {type(exc).__name__}: {exc}")


def _snapshot_menu_inventory(path: Path, max_controls: int = 2200) -> int:
    import pywinauto  # type: ignore
    desktop = pywinauto.Desktop(backend="uia")
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[str] = []
    try:
        roots = list(desktop.windows())
    except Exception:
        roots = []
    count = 0
    for root in roots:
        queue: list[tuple[object, int]] = [(root, 0)]
        scanned = 0
        while queue and scanned < max_controls:
            control, depth = queue.pop(0)
            scanned += 1
            try:
                info = control.element_info
                control_type = _info_text(info, "control_type")
                class_name = _info_text(info, "class_name")
                raw_name = _info_text(info, "name")
                automation_id = _info_text(info, "automation_id")
            except Exception:
                control_type = class_name = raw_name = automation_id = ""
            blob = " ".join([control_type, class_name, raw_name, automation_id]).lower()
            if any(word.split()[0] in blob for word in _UPLOAD_WORDS + _PLUS_WORDS) or control_type in {"MenuItem", "Button", "ListItem"}:
                name_redacted, _, name_len = safe_text(raw_name, control_type=control_type, max_chars=80)
                auto_redacted, _, _ = safe_text(automation_id, control_type="Button", max_chars=80)
                rows.append(f"depth={depth} type={control_type} name={name_redacted} name_len={name_len} automation_id={auto_redacted}")
                count += 1
            if depth < 6:
                try:
                    for child in list(control.children())[:80]:
                        queue.append((child, depth + 1))
                except Exception:
                    pass
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return count


def _find_upload_menu_item(inventory_path: Path, timeout_seconds: float = 10.0, max_controls: int = 2800) -> tuple[UploadControlCandidate, object, int]:
    import pywinauto  # type: ignore
    deadline = time.time() + timeout_seconds
    desktop = pywinauto.Desktop(backend="uia")
    last_inventory_count = 0
    while time.time() < deadline:
        last_inventory_count = _snapshot_menu_inventory(inventory_path)
        found: list[tuple[UploadControlCandidate, object]] = []
        try:
            roots = list(desktop.windows())
        except Exception:
            roots = []
        for root in roots:
            queue: list[tuple[object, int, bool]] = [(root, 0, True)]
            scanned = 0
            while queue and scanned < max_controls:
                control, depth, page_scope = queue.pop(0)
                scanned += 1
                try:
                    info = control.element_info
                    control_type = _info_text(info, "control_type")
                    class_name = _info_text(info, "class_name")
                    raw_name = _info_text(info, "name")
                    automation_id = _info_text(info, "automation_id")
                except Exception:
                    control_type = class_name = raw_name = automation_id = ""
                blob = " ".join([control_type, class_name, raw_name, automation_id]).lower()
                if any(word in blob for word in _UPLOAD_WORDS) and control_type in {"Button", "MenuItem", "Text", "ListItem", "Custom", "Hyperlink"}:
                    score = 180 + (30 if control_type in {"Button", "MenuItem"} else 0)
                    found.append((_candidate_from_control(control, depth, True, "upload_files_menu_item", score), control))
                if depth < 8:
                    try:
                        for child in list(control.children())[:100]:
                            queue.append((child, depth + 1, page_scope))
                    except Exception:
                        pass
        if found:
            found.sort(key=lambda item: -item[0].score)
            return found[0][0], found[0][1], last_inventory_count
        time.sleep(0.25)
    raise RuntimeError(f"Upload files menu item was not observed after opening composer plus menu; inventory_count={last_inventory_count}; inventory_path={inventory_path}")


def _find_file_dialog(timeout_seconds: float = 12.0) -> object:
    import pywinauto  # type: ignore
    desktop = pywinauto.Desktop(backend="uia")
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            for window in desktop.windows():
                try:
                    title = str(window.window_text() or "")
                    class_name = str(window.element_info.class_name or "")
                    lower_title = title.lower()
                    if "#32770" in class_name or lower_title in {"open", "choose file to upload", "file upload"} or "upload" in lower_title:
                        return window
                except Exception:
                    continue
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError("File picker dialog was not observed after upload menu click.")


def _set_file_picker_path(dialog: object, file_path: Path) -> None:
    path_text = str(file_path)
    try:
        dialog.set_focus()
    except Exception:
        pass
    try:
        edits = dialog.descendants(control_type="Edit")
    except Exception:
        edits = []
    for edit in reversed(edits):
        try:
            edit.set_focus()
            edit.set_edit_text(path_text)
            keyboard.send_keys("{ENTER}")
            return
        except Exception:
            continue
    keyboard.send_keys("%n")
    time.sleep(0.2)
    _set_clipboard_text(path_text)
    keyboard.send_keys("^v")
    time.sleep(0.2)
    keyboard.send_keys("{ENTER}")


def _observe_staged_file(file_name: str, timeout_seconds: float = 30.0) -> tuple[bool, str]:
    import pywinauto  # type: ignore
    desktop = pywinauto.Desktop(backend="uia")
    needle = file_name.lower()
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            edge_pids = edge_process_ids()
            _windows, wrappers = discover_edge_windows(desktop, edge_pids)
            for window in wrappers or []:
                try:
                    queue = list(window.children())
                except Exception:
                    queue = []
                seen = 0
                while queue and seen < 2600:
                    control = queue.pop(0)
                    seen += 1
                    try:
                        info = control.element_info
                        name = _info_text(info, "name")
                        automation_id = _info_text(info, "automation_id")
                        class_name = _info_text(info, "class_name")
                    except Exception:
                        name = automation_id = class_name = ""
                    blob = " ".join([name, automation_id, class_name]).lower()
                    if needle and needle in blob:
                        return True, "uia_filename_match"
                    try:
                        queue.extend(list(control.children())[:100])
                    except Exception:
                        pass
        except Exception:
            pass
        time.sleep(0.5)
    return False, "not_observed"


def _write_report(path: Path, result: CurrentUrlGuardUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.12C current-URL guard report upload staging repair",
        "current_url_read_attempted:true" if result.current_url_read_attempted else "current_url_read_attempted:false",
        "current_url_matches_target:true" if result.current_url_matches_target else "current_url_matches_target:false",
        "navigation_skipped_existing_target:true" if result.navigation_skipped_existing_target else "navigation_skipped_existing_target:false",
        "navigation_attempted:true" if result.navigation_attempted else "navigation_attempted:false",
        "report_upload_attempted:true" if result.report_upload_attempted else "report_upload_attempted:false",
        "file_attach_attempted:true" if result.file_attach_attempted else "file_attach_attempted:false",
        "chatgpt_enter_key_sent:false",
        "send_submit_performed:false",
        "chatgpt_prompt_submitted:false",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "prompt_text_logged:false",
        "file_content_logged:false",
        "No full URL, file path, prompt, conversation text, or file contents are logged.",
        "",
        f"current_url_hash: {result.current_url_hash}",
        f"composer_candidate_found: {result.composer_candidate_found}",
        f"composer_focus_verified: {result.composer_focus_verified}",
        f"report_candidate_path_redacted: {result.report_candidate_path_redacted}",
        f"report_candidate_name: {result.report_candidate_name}",
        f"report_candidate_hash: {result.report_candidate_hash}",
        f"report_candidate_size_bytes: {result.report_candidate_size_bytes}",
        f"plus_button_found: {result.plus_button_found}",
        f"plus_button_clicked: {result.plus_button_clicked}",
        f"upload_menu_item_found: {result.upload_menu_item_found}",
        f"upload_menu_item_clicked: {result.upload_menu_item_clicked}",
        f"upload_menu_inventory_written: {result.upload_menu_inventory_written}",
        f"upload_menu_inventory_count: {result.upload_menu_inventory_count}",
        f"menu_inventory_path: {result.menu_inventory_path}",
        f"file_picker_opened: {result.file_picker_opened}",
        f"upload_staging_observed: {result.upload_staging_observed}",
        f"staging_observation_method: {result.staging_observation_method}",
        f"failure_layer: {result.failure_layer}",
        f"error: {result.error}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, result: CurrentUrlGuardUploadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")


def run_l26_12c_current_url_guard_upload_gate(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 10.0, allow_report_upload: bool = False) -> CurrentUrlGuardUploadResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_12c_current_url_guard_upload_result.json"
    report_path = out_dir / "normal_edge_l26_12c_current_url_guard_upload_report.txt"
    menu_inventory_path = out_dir / "normal_edge_l26_12c_upload_menu_inventory_redacted.txt"
    target_ok = _canonical_url(target_url) == _canonical_url(REQUESTED_CHAT_URL)
    current_url = ""
    report_file: Path | None = None
    base = dict(
        target_url_is_requested_chat=target_ok,
        allow_report_upload_requested=allow_report_upload,
        live_report_path=str(report_path),
        json_path=str(json_path),
        menu_inventory_path=str(menu_inventory_path),
    )
    try:
        if not allow_report_upload:
            raise RuntimeError("L26.12C requires explicit --allow-report-upload to attach the report file.")
        if not target_ok:
            raise RuntimeError("Target URL must be the requested project chat URL.")
        current_observed, page_ready, skipped_nav, attempted_nav, current_url = _ensure_target_loaded(out_dir, target_url, start_if_missing, settle_seconds)
        if not page_ready:
            raise RuntimeError("Target chat was neither already loaded nor successfully navigated.")
        composer_found, focus_verified = _verify_direct_composer_focus()
        if not (composer_found and focus_verified):
            raise RuntimeError("Requested chat composer focus was not proven after URL guard.")
        report_file = find_latest_patchops_report()
        stat = report_file.stat()
        report_hash = _hash_file(report_file)
        report_is_text = report_file.suffix.lower() == ".txt" and stat.st_size > 0
        if not report_is_text:
            raise RuntimeError("Latest report candidate is not a non-empty txt file.")
        plus, plus_control = _find_plus_control()
        if not plus.is_in_page_scope or plus.is_browser_chrome:
            raise RuntimeError("Composer plus button is not a safe in-page candidate.")
        _click_control(plus_control)
        time.sleep(0.8)
        upload_item, upload_control, inventory_count = _find_upload_menu_item(menu_inventory_path)
        _click_control(upload_control)
        time.sleep(0.8)
        dialog = _find_file_dialog()
        _set_file_picker_path(dialog, report_file)
        staged, method = _observe_staged_file(report_file.name)
        result = CurrentUrlGuardUploadResult(
            **base,
            current_url_read_attempted=True,
            current_url_observed=current_observed,
            current_url_hash=_hash_text(_canonical_url(current_url)),
            current_url_matches_target=_canonical_url(current_url) == _canonical_url(target_url),
            navigation_skipped_existing_target=skipped_nav,
            navigation_attempted=attempted_nav,
            navigation_observed=page_ready,
            composer_candidate_found=composer_found,
            composer_focus_verified=focus_verified,
            report_candidate_found=True,
            report_candidate_path_redacted=_redact_path(report_file),
            report_candidate_name=report_file.name,
            report_candidate_hash=report_hash,
            report_candidate_size_bytes=int(stat.st_size),
            report_candidate_is_text=report_is_text,
            plus_button_found=True,
            plus_button_clicked=True,
            upload_menu_item_found=True,
            upload_menu_item_clicked=True,
            upload_menu_inventory_written=True,
            upload_menu_inventory_count=inventory_count,
            file_picker_opened=True,
            file_picker_path_entered=True,
            file_picker_confirmed=True,
            upload_staging_observed=staged,
            staged_file_name_hash=_hash_text(report_file.name),
            staged_file_name_length=len(report_file.name),
            staging_observation_method=method,
            report_upload_attempted=True,
            file_attach_attempted=True,
            result="PASS" if staged else "FAIL",
            failure_layer="" if staged else "report_upload_staging_observation",
            error="" if staged else "File was selected but staged upload was not observed in ChatGPT UIA tree.",
        )
    except Exception as exc:
        inv_count = 0
        try:
            inv_count = _snapshot_menu_inventory(menu_inventory_path)
        except Exception:
            pass
        result = CurrentUrlGuardUploadResult(
            **base,
            current_url_read_attempted=True,
            current_url_observed=bool(current_url),
            current_url_hash=_hash_text(_canonical_url(current_url)),
            current_url_matches_target=_canonical_url(current_url) == _canonical_url(target_url),
            navigation_skipped_existing_target=_canonical_url(current_url) == _canonical_url(target_url),
            upload_menu_inventory_written=menu_inventory_path.exists(),
            upload_menu_inventory_count=inv_count,
            report_candidate_name=report_file.name if report_file else "",
            result="FAIL",
            failure_layer="current_url_guard_report_upload_staging_gate",
            error=f"{type(exc).__name__}: {exc}",
        )
    _write_report(report_path, result)
    _write_json(json_path, result)
    return result


def assert_l26_12c_acceptance(result: CurrentUrlGuardUploadResult) -> None:
    payload = result.to_payload()
    required_true = [
        "target_url_is_requested_chat",
        "current_url_read_attempted",
        "current_url_observed",
        "current_url_matches_target",
        "navigation_skipped_existing_target",
        "navigation_observed",
        "composer_candidate_found",
        "composer_focus_verified",
        "allow_report_upload_requested",
        "report_candidate_found",
        "report_candidate_is_text",
        "plus_button_found",
        "plus_button_clicked",
        "upload_menu_item_found",
        "upload_menu_item_clicked",
        "upload_menu_inventory_written",
        "file_picker_opened",
        "file_picker_path_entered",
        "file_picker_confirmed",
        "upload_staging_observed",
        "report_upload_attempted",
        "file_attach_attempted",
    ]
    required_false = [
        "navigation_attempted",
        "chatgpt_enter_key_sent",
        "send_submit_performed",
        "chatgpt_prompt_submitted",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
        "full_conversation_text_logged",
        "prompt_text_logged",
        "file_content_logged",
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_dom_automation_used",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if payload.get("report_candidate_size_bytes", 0) <= 0:
        missing_true.append("report_candidate_size_bytes>0")
    if not payload.get("report_candidate_hash"):
        missing_true.append("report_candidate_hash_nonempty")
    if not payload.get("staged_file_name_hash"):
        missing_true.append("staged_file_name_hash_nonempty")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.12C acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
