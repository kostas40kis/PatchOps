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
from typing import Any, Iterable

PATCH_NAME = "l26_01a_pywinauto_runtime_json_repair"
_SAFE_NAME_CONTROL_TYPES = {"Window", "ToolBar", "TabItem", "Button", "Edit", "MenuItem"}


@dataclass(frozen=True)
class UiControlSummary:
    depth: int
    control_type: str
    class_name: str
    name: str
    automation_id: str


@dataclass(frozen=True)
class EdgeLiveProbeResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    python_version: str = sys.version.replace("\n", " ")
    platform: str = platform.platform()
    pywinauto_imported: bool = False
    uia_backend_available: bool = False
    normal_edge_attached: bool = False
    normal_edge_started: bool = False
    edge_process_count: int = 0
    edge_window_title: str = ""
    edge_window_title_read: bool = False
    edge_focused: bool = False
    uia_control_tree_dumped: bool = False
    control_count_reported: bool = False
    uia_control_count: int = 0
    top_level_control_summary: tuple[UiControlSummary, ...] = ()
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_navigation_performed: bool = False
    chatgpt_interaction_performed: bool = False
    download_click_performed: bool = False
    run_package_invoked: bool = False
    pasteback_or_send_performed: bool = False
    conversation_text_logged: bool = False
    json_written: bool = False
    tree_summary_path: str = ""
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["top_level_control_summary"] = [asdict(item) for item in self.top_level_control_summary]
        return payload


def _replace(result: EdgeLiveProbeResult, **changes: Any) -> EdgeLiveProbeResult:
    payload = result.to_payload()
    payload.update(changes)
    summaries = tuple(UiControlSummary(**item) for item in payload.pop("top_level_control_summary", []))
    return EdgeLiveProbeResult(top_level_control_summary=summaries, **payload)


def _redact_text(value: object, *, max_chars: int = 60) -> str:
    text = "" if value is None else str(value)
    text = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:12]
    return f"<redacted length={len(text)} sha256={digest}>"


def _write_json(path: Path, result: EdgeLiveProbeResult) -> EdgeLiveProbeResult:
    path.parent.mkdir(parents=True, exist_ok=True)
    written = _replace(result, json_written=True)
    path.write_text(json.dumps(written.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
    return written


def _edge_executable_candidates() -> list[Path]:
    candidates: list[Path] = []
    for raw in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"), os.environ.get("LOCALAPPDATA")):
        if not raw:
            continue
        root = Path(raw)
        candidates.append(root / "Microsoft" / "Edge" / "Application" / "msedge.exe")
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
        completed = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq msedge.exe", "/FO", "CSV", "/NH"],
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
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


def ensure_edge_running(*, start_if_missing: bool, settle_seconds: float = 3.0) -> bool:
    if edge_process_ids():
        return False
    if not start_if_missing:
        return False
    edge_exe = find_edge_executable()
    if edge_exe is None:
        return False
    subprocess.Popen([str(edge_exe)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + max(1.0, settle_seconds)
    while time.time() < deadline:
        if edge_process_ids():
            return True
        time.sleep(0.25)
    return bool(edge_process_ids())


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


def _window_title(window: object) -> str:
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


def _is_edge_window(window: object, edge_pids: set[int]) -> bool:
    pid = _window_pid(window)
    title = _window_title(window)
    class_name = ""
    try:
        class_name = str(window.element_info.class_name)
    except Exception:
        pass
    if pid is not None and pid in edge_pids and title:
        return True
    if "microsoft edge" in title.lower():
        return True
    if class_name == "Chrome_WidgetWin_1" and pid is not None and pid in edge_pids:
        return True
    return False


def _select_edge_window(desktop: object, edge_pids: set[int]) -> object | None:
    try:
        windows = desktop.windows()
    except Exception:
        return None
    candidates = [window for window in windows if _is_edge_window(window, edge_pids)]
    if not candidates:
        return None
    titled = [window for window in candidates if _window_title(window)]
    return titled[0] if titled else candidates[0]


def _safe_control_name(control_type: str, raw_name: object) -> str:
    if control_type not in _SAFE_NAME_CONTROL_TYPES:
        text = "" if raw_name is None else str(raw_name)
        if not text.strip():
            return ""
        digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:12]
        return f"<name redacted by policy sha256={digest}>"
    return _redact_text(raw_name)


def _control_summary(control: object, depth: int) -> UiControlSummary:
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
    return UiControlSummary(depth=depth, control_type=control_type, class_name=class_name, name=name, automation_id=automation_id)


def _bounded_children(root: object, *, max_depth: int, max_controls: int) -> list[UiControlSummary]:
    summaries: list[UiControlSummary] = []
    stack: list[tuple[object, int]] = [(root, 0)]
    while stack and len(summaries) < max_controls:
        control, depth = stack.pop(0)
        summaries.append(_control_summary(control, depth))
        if depth >= max_depth:
            continue
        try:
            children = list(control.children())
        except Exception:
            children = []
        for child in children[: max(0, max_controls - len(summaries))]:
            stack.append((child, depth + 1))
    return summaries[:max_controls]


def _write_tree_text(path: Path, controls: Iterable[UiControlSummary]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.1A bounded normal Edge UIA tree summary",
        "conversation_text_logged:false",
        "Only bounded, redacted control metadata is recorded.",
        "",
    ]
    for item in controls:
        indent = "  " * item.depth
        lines.append(
            f"{indent}- type={item.control_type!r} class={item.class_name!r} "
            f"name={item.name!r} automation_id={item.automation_id!r}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def probe_normal_edge(*, output_dir: str | Path, start_if_missing: bool = True, focus: bool = True, max_depth: int = 2, max_controls: int = 80) -> EdgeLiveProbeResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_01_probe_result.json"

    imported, import_error, pywinauto = _import_pywinauto()
    if not imported:
        return _write_json(json_path, EdgeLiveProbeResult(failure_layer="pywinauto_import", error=import_error))

    try:
        edge_started = ensure_edge_running(start_if_missing=start_if_missing)
        edge_pids = edge_process_ids()
    except Exception as exc:
        return _write_json(json_path, EdgeLiveProbeResult(pywinauto_imported=True, failure_layer="edge_process_discovery", error=f"{type(exc).__name__}: {exc}"))

    try:
        desktop = pywinauto.Desktop(backend="uia")
        uia_backend_available = True
    except Exception as exc:
        return _write_json(json_path, EdgeLiveProbeResult(pywinauto_imported=True, normal_edge_started=edge_started, edge_process_count=len(edge_pids), failure_layer="uia_backend", error=f"{type(exc).__name__}: {exc}"))

    try:
        edge_window = _select_edge_window(desktop, edge_pids)
    except Exception as exc:
        return _write_json(json_path, EdgeLiveProbeResult(pywinauto_imported=True, uia_backend_available=uia_backend_available, normal_edge_started=edge_started, edge_process_count=len(edge_pids), failure_layer="edge_window_discovery", error=f"{type(exc).__name__}: {exc}"))

    if edge_window is None:
        return _write_json(json_path, EdgeLiveProbeResult(pywinauto_imported=True, uia_backend_available=uia_backend_available, normal_edge_started=edge_started, edge_process_count=len(edge_pids), failure_layer="edge_window_discovery", error="No normal Microsoft Edge UIA window was discovered."))

    title = _redact_text(_window_title(edge_window), max_chars=100)
    focused = False
    focus_error = ""
    if focus:
        try:
            edge_window.set_focus()
            focused = True
        except Exception as exc:
            focus_error = f"{type(exc).__name__}: {exc}"

    controls: list[UiControlSummary] = []
    tree_path = out_dir / "normal_edge_uia_tree_summary.txt"
    tree_dumped = False
    try:
        controls = _bounded_children(edge_window, max_depth=max_depth, max_controls=max_controls)
        _write_tree_text(tree_path, controls)
        tree_dumped = True
    except Exception as exc:
        focus_error = f"{focus_error}; tree dump failed: {type(exc).__name__}: {exc}".strip("; ")

    result_pass = bool(imported and uia_backend_available and edge_pids and title and focused and tree_dumped and controls)
    return _write_json(
        json_path,
        EdgeLiveProbeResult(
            pywinauto_imported=True,
            uia_backend_available=uia_backend_available,
            normal_edge_attached=True,
            normal_edge_started=edge_started,
            edge_process_count=len(edge_pids),
            edge_window_title=title,
            edge_window_title_read=bool(title),
            edge_focused=focused,
            uia_control_tree_dumped=tree_dumped,
            control_count_reported=True,
            uia_control_count=len(controls),
            top_level_control_summary=tuple(controls[:25]),
            tree_summary_path=str(tree_path),
            result="PASS" if result_pass else "FAIL",
            failure_layer="" if result_pass else "edge_focus_or_tree",
            error="" if result_pass else focus_error,
        ),
    )


def assert_l26_01_acceptance(result: EdgeLiveProbeResult) -> None:
    payload = result.to_payload()
    required_true = ["pywinauto_imported", "uia_backend_available", "edge_window_title_read", "edge_focused", "uia_control_tree_dumped", "control_count_reported", "json_written"]
    required_false = ["webdriver_used", "selenium_imported", "cloudflare_bypass_attempted", "browser_navigation_performed", "chatgpt_interaction_performed", "download_click_performed", "run_package_invoked", "pasteback_or_send_performed", "conversation_text_logged"]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if not (payload.get("normal_edge_attached") or payload.get("normal_edge_started")):
        missing_true.append("normal_edge_attached_or_started")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.1 acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
