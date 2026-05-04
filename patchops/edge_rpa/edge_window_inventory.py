from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PATCH_NAME = "l26_02_normal_edge_window_inventory_attach_proof"
_SAFE_NAME_CONTROL_TYPES = {"Window", "ToolBar", "TabItem", "Button", "Edit", "MenuItem"}


@dataclass(frozen=True)
class EdgeWindowCandidate:
    index: int
    process_id: int | None
    handle: int | None
    class_name: str
    title_redacted: str
    title_hash: str
    title_length: int
    score: int
    score_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class TopLevelControl:
    depth: int
    control_type: str
    class_name: str
    name: str
    automation_id: str


@dataclass(frozen=True)
class EdgeWindowInventoryResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    python_version: str = sys.version.replace("\n", " ")
    platform: str = platform.platform()
    pywinauto_imported: bool = False
    uia_backend_available: bool = False
    edge_process_count: int = 0
    edge_window_count: int = 0
    edge_window_inventory_written: bool = False
    selected_window_found: bool = False
    selected_window_index: int | None = None
    selected_window_score: int = 0
    selected_window_title_redacted: str = ""
    selected_window_title_hash: str = ""
    selected_window_title_length: int = 0
    normal_edge_attached: bool = False
    edge_window_title_read: bool = False
    edge_focused: bool = False
    uia_top_level_tree_dumped: bool = False
    top_level_control_count: int = 0
    candidates: tuple[EdgeWindowCandidate, ...] = ()
    top_level_controls: tuple[TopLevelControl, ...] = ()
    inventory_path: str = ""
    selected_tree_path: str = ""
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_navigation_performed: bool = False
    chatgpt_interaction_performed: bool = False
    download_click_performed: bool = False
    run_package_invoked: bool = False
    pasteback_or_send_performed: bool = False
    conversation_text_logged: bool = False
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["candidates"] = [asdict(item) for item in self.candidates]
        payload["top_level_controls"] = [asdict(item) for item in self.top_level_controls]
        return payload


def _with(result: EdgeWindowInventoryResult, **changes: Any) -> EdgeWindowInventoryResult:
    payload = result.to_payload()
    payload.update(changes)
    candidates = tuple(EdgeWindowCandidate(**item) for item in payload.pop("candidates", []))
    controls = tuple(TopLevelControl(**item) for item in payload.pop("top_level_controls", []))
    return EdgeWindowInventoryResult(candidates=candidates, top_level_controls=controls, **payload)


def _hash_text(value: object) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def _redact_text(value: object, *, max_chars: int = 80) -> str:
    text = "" if value is None else str(value)
    text = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return f"<redacted length={len(text)} sha256={_hash_text(text)}>"


def _write_result_json(path: Path, result: EdgeWindowInventoryResult) -> EdgeWindowInventoryResult:
    path.parent.mkdir(parents=True, exist_ok=True)
    written = _with(result, edge_window_inventory_written=True, inventory_path=str(path))
    path.write_text(json.dumps(written.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
    return written


def _edge_executable_candidates() -> list[Path]:
    candidates: list[Path] = []
    for raw in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"), os.environ.get("LOCALAPPDATA")):
        if raw:
            candidates.append(Path(raw) / "Microsoft" / "Edge" / "Application" / "msedge.exe")
    candidates.extend([
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ])
    unique: list[Path] = []
    seen: set[str] = set()
    for item in candidates:
        key = str(item).lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def find_edge_executable() -> Path | None:
    for candidate in _edge_executable_candidates():
        try:
            if candidate.exists():
                return candidate
        except OSError:
            continue
    return None


def _parse_tasklist_csv(output: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in csv.reader(output.splitlines()):
        if len(row) < 2:
            continue
        if row[0].strip().lower() == "image name":
            continue
        rows.append({"image_name": row[0].strip(), "pid": row[1].strip()})
    return rows


def edge_process_ids() -> set[int]:
    try:
        completed = subprocess.run(["tasklist", "/FI", "IMAGENAME eq msedge.exe", "/FO", "CSV", "/NH"], text=True, capture_output=True, timeout=10, check=False)
    except Exception:
        return set()
    pids: set[int] = set()
    for row in _parse_tasklist_csv(completed.stdout):
        try:
            if row["image_name"].lower() == "msedge.exe":
                pids.add(int(row["pid"]))
        except (KeyError, ValueError):
            continue
    return pids


def ensure_edge_running(*, start_if_missing: bool, settle_seconds: float = 3.0) -> None:
    if edge_process_ids() or not start_if_missing:
        return
    edge_exe = find_edge_executable()
    if edge_exe is None:
        return
    subprocess.Popen([str(edge_exe)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + max(1.0, settle_seconds)
    while time.time() < deadline:
        if edge_process_ids():
            return
        time.sleep(0.25)


def _import_pywinauto() -> tuple[bool, str, Any]:
    try:
        import pywinauto  # type: ignore
        return True, "", pywinauto
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}", None


def _window_pid(window: object) -> int | None:
    try:
        return int(window.element_info.process_id)
    except Exception:
        return None


def _window_handle(window: object) -> int | None:
    for attr in ("handle",):
        try:
            value = getattr(window, attr)
            if callable(value):
                value = value()
            return int(value)
        except Exception:
            continue
    try:
        return int(window.element_info.handle)
    except Exception:
        return None


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


def _window_class_name(window: object) -> str:
    try:
        return str(window.element_info.class_name or "")
    except Exception:
        return ""


def _score_window(window: object, edge_pids: set[int]) -> tuple[int, tuple[str, ...]]:
    score = 0
    reasons: list[str] = []
    pid = _window_pid(window)
    title = _window_title_raw(window)
    class_name = _window_class_name(window)
    if pid is not None and pid in edge_pids:
        score += 50
        reasons.append("pid_matches_msedge")
    if title.strip():
        score += 20
        reasons.append("title_present")
    if "microsoft edge" in title.lower() or "edge" in title.lower():
        score += 15
        reasons.append("title_mentions_edge")
    if class_name == "Chrome_WidgetWin_1":
        score += 10
        reasons.append("chromium_window_class")
    if "webdriver" in title.lower() or "selenium" in title.lower():
        score -= 100
        reasons.append("automation_title_penalty")
    return score, tuple(reasons)


def discover_edge_windows(desktop: object, edge_pids: set[int]) -> tuple[list[EdgeWindowCandidate], list[object]]:
    try:
        windows = list(desktop.windows())
    except Exception:
        return [], []
    pairs: list[tuple[EdgeWindowCandidate, object]] = []
    index = 0
    for window in windows:
        pid = _window_pid(window)
        title = _window_title_raw(window)
        class_name = _window_class_name(window)
        score, reasons = _score_window(window, edge_pids)
        if not (pid in edge_pids if pid is not None else False) and "microsoft edge" not in title.lower():
            continue
        if score <= 0:
            continue
        candidate = EdgeWindowCandidate(
            index=index,
            process_id=pid,
            handle=_window_handle(window),
            class_name=class_name,
            title_redacted=_redact_text(title, max_chars=96),
            title_hash=_hash_text(title),
            title_length=len(title),
            score=score,
            score_reasons=reasons,
        )
        pairs.append((candidate, window))
        index += 1
    pairs.sort(key=lambda pair: (-pair[0].score, pair[0].index))
    candidates = []
    wrappers = []
    for new_index, (candidate, window) in enumerate(pairs):
        candidates.append(EdgeWindowCandidate(
            index=new_index,
            process_id=candidate.process_id,
            handle=candidate.handle,
            class_name=candidate.class_name,
            title_redacted=candidate.title_redacted,
            title_hash=candidate.title_hash,
            title_length=candidate.title_length,
            score=candidate.score,
            score_reasons=candidate.score_reasons,
        ))
        wrappers.append(window)
    return candidates, wrappers


def _safe_control_name(control_type: str, raw_name: object) -> str:
    if control_type not in _SAFE_NAME_CONTROL_TYPES:
        text = "" if raw_name is None else str(raw_name)
        if not text.strip():
            return ""
        return f"<name redacted by policy sha256={_hash_text(text)}>"
    return _redact_text(raw_name, max_chars=60)


def _control_summary(control: object, depth: int) -> TopLevelControl:
    info = getattr(control, "element_info", None)
    control_type = ""
    class_name = ""
    name = ""
    automation_id = ""
    if info is not None:
        try:
            control_type = str(info.control_type or "")
        except Exception:
            pass
        try:
            class_name = str(info.class_name or "")
        except Exception:
            pass
        try:
            name = _safe_control_name(control_type, info.name)
        except Exception:
            pass
        try:
            automation_id = _redact_text(info.automation_id, max_chars=40)
        except Exception:
            pass
    return TopLevelControl(depth=depth, control_type=control_type, class_name=class_name, name=name, automation_id=automation_id)


def _bounded_tree(root: object, *, max_depth: int, max_controls: int) -> list[TopLevelControl]:
    controls: list[TopLevelControl] = []
    stack: list[tuple[object, int]] = [(root, 0)]
    while stack and len(controls) < max_controls:
        control, depth = stack.pop(0)
        controls.append(_control_summary(control, depth))
        if depth >= max_depth:
            continue
        try:
            children = list(control.children())
        except Exception:
            children = []
        for child in children[: max(0, max_controls - len(controls))]:
            stack.append((child, depth + 1))
    return controls[:max_controls]


def _write_inventory_text(path: Path, result: EdgeWindowInventoryResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.2 normal Microsoft Edge window inventory",
        "conversation_text_logged:false",
        "No URL navigation, page clicks, prompt paste/send, download clicks, or run-package actions are performed.",
        "Titles are redacted/hash summarized for durable evidence without conversation logging.",
        "",
    ]
    for item in result.candidates:
        lines.append(f"[{item.index}] pid={item.process_id} handle={item.handle} class={item.class_name!r} score={item.score} reasons={','.join(item.score_reasons)} title={item.title_redacted!r} title_hash={item.title_hash} title_length={item.title_length}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_tree_text(path: Path, controls: tuple[TopLevelControl, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["L26.2 selected normal Edge top-level UIA tree", "conversation_text_logged:false", ""]
    for item in controls:
        indent = "  " * item.depth
        lines.append(f"{indent}- type={item.control_type!r} class={item.class_name!r} name={item.name!r} automation_id={item.automation_id!r}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_l26_02_live_inventory(*, output_dir: str | Path, start_if_missing: bool = True, max_depth: int = 1, max_controls: int = 60) -> EdgeWindowInventoryResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_02_inventory_result.json"
    inventory_text_path = out_dir / "normal_edge_l26_02_window_inventory.txt"
    tree_text_path = out_dir / "normal_edge_l26_02_selected_tree.txt"

    imported, import_error, pywinauto = _import_pywinauto()
    if not imported:
        return _write_result_json(json_path, EdgeWindowInventoryResult(failure_layer="pywinauto_import", error=import_error))

    try:
        ensure_edge_running(start_if_missing=start_if_missing)
        edge_pids = edge_process_ids()
    except Exception as exc:
        return _write_result_json(json_path, EdgeWindowInventoryResult(pywinauto_imported=True, failure_layer="edge_process_discovery", error=f"{type(exc).__name__}: {exc}"))

    try:
        desktop = pywinauto.Desktop(backend="uia")
    except Exception as exc:
        return _write_result_json(json_path, EdgeWindowInventoryResult(pywinauto_imported=True, edge_process_count=len(edge_pids), failure_layer="uia_backend", error=f"{type(exc).__name__}: {exc}"))

    try:
        candidates, wrappers = discover_edge_windows(desktop, edge_pids)
    except Exception as exc:
        return _write_result_json(json_path, EdgeWindowInventoryResult(pywinauto_imported=True, uia_backend_available=True, edge_process_count=len(edge_pids), failure_layer="edge_window_inventory", error=f"{type(exc).__name__}: {exc}"))

    if not candidates or not wrappers:
        result = EdgeWindowInventoryResult(
            pywinauto_imported=True,
            uia_backend_available=True,
            edge_process_count=len(edge_pids),
            edge_window_count=0,
            candidates=tuple(),
            failure_layer="edge_window_inventory",
            error="No Microsoft Edge UIA top-level window candidates were discovered.",
        )
        result = _with(result, inventory_path=str(inventory_text_path))
        _write_inventory_text(inventory_text_path, result)
        return _write_result_json(json_path, result)

    selected = candidates[0]
    selected_window = wrappers[0]
    focused = False
    focus_error = ""
    try:
        selected_window.set_focus()
        focused = True
    except Exception as exc:
        focus_error = f"{type(exc).__name__}: {exc}"

    controls: list[TopLevelControl] = []
    tree_dumped = False
    try:
        controls = _bounded_tree(selected_window, max_depth=max_depth, max_controls=max_controls)
        tree_dumped = bool(controls)
    except Exception as exc:
        focus_error = f"{focus_error}; tree dump failed: {type(exc).__name__}: {exc}".strip("; ")

    result_pass = bool(
        edge_pids
        and candidates
        and selected.score > 0
        and selected.title_length > 0
        and focused
        and tree_dumped
        and controls
    )

    result = EdgeWindowInventoryResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        edge_process_count=len(edge_pids),
        edge_window_count=len(candidates),
        selected_window_found=True,
        selected_window_index=selected.index,
        selected_window_score=selected.score,
        selected_window_title_redacted=selected.title_redacted,
        selected_window_title_hash=selected.title_hash,
        selected_window_title_length=selected.title_length,
        normal_edge_attached=True,
        edge_window_title_read=selected.title_length > 0,
        edge_focused=focused,
        uia_top_level_tree_dumped=tree_dumped,
        top_level_control_count=len(controls),
        candidates=tuple(candidates),
        top_level_controls=tuple(controls[:25]),
        inventory_path=str(inventory_text_path),
        selected_tree_path=str(tree_text_path),
        result="PASS" if result_pass else "FAIL",
        failure_layer="" if result_pass else "edge_selected_window_focus_or_tree",
        error="" if result_pass else focus_error,
    )
    _write_inventory_text(inventory_text_path, result)
    _write_tree_text(tree_text_path, result.top_level_controls)
    return _write_result_json(json_path, result)


def assert_l26_02_acceptance(result: EdgeWindowInventoryResult) -> None:
    payload = result.to_payload()
    required_true = [
        "pywinauto_imported",
        "uia_backend_available",
        "edge_window_inventory_written",
        "selected_window_found",
        "normal_edge_attached",
        "edge_window_title_read",
        "edge_focused",
        "uia_top_level_tree_dumped",
    ]
    required_false = [
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_navigation_performed",
        "chatgpt_interaction_performed",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if payload.get("edge_process_count", 0) < 1:
        missing_true.append("edge_process_count>=1")
    if payload.get("edge_window_count", 0) < 1:
        missing_true.append("edge_window_count>=1")
    if payload.get("selected_window_score", 0) <= 0:
        missing_true.append("selected_window_score>0")
    if payload.get("top_level_control_count", 0) < 1:
        missing_true.append("top_level_control_count>=1")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.2 acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
