from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.edge_rpa.edge_window_inventory import (
    discover_edge_windows,
    edge_process_ids,
    ensure_edge_running,
)

PATCH_NAME = "l26_03_normal_edge_safe_uia_control_tree_report"
_ALLOWED_NAME_CONTROL_TYPES = {"Window", "ToolBar", "TabItem", "Button", "Edit", "ComboBox", "MenuItem", "Text"}
_ALWAYS_REDACT_TYPES = {"Document", "Pane", "List", "Group", "Custom", "DataItem"}


@dataclass(frozen=True)
class SafeUiaControlRecord:
    index: int
    parent_index: int | None
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


@dataclass(frozen=True)
class UiaTreeReportResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    pywinauto_imported: bool = False
    uia_backend_available: bool = False
    normal_edge_attached: bool = False
    edge_window_title_read: bool = False
    edge_focused: bool = False
    uia_control_tree_dumped: bool = False
    control_count_reported: bool = False
    control_count: int = 0
    max_depth_observed: int = 0
    tree_report_written: bool = False
    control_type_summary_written: bool = False
    address_bar_candidate_found: bool = False
    input_candidate_count: int = 0
    controls: tuple[SafeUiaControlRecord, ...] = ()
    control_type_counts: dict[str, int] = field(default_factory=dict)
    tree_report_path: str = ""
    summary_report_path: str = ""
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    browser_navigation_performed: bool = False
    chatgpt_interaction_performed: bool = False
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
        payload["controls"] = [asdict(item) for item in self.controls]
        payload["control_type_counts"] = dict(self.control_type_counts)
        return payload


def _with(result: UiaTreeReportResult, **changes: Any) -> UiaTreeReportResult:
    payload = result.to_payload()
    payload.update(changes)
    controls = tuple(SafeUiaControlRecord(**item) for item in payload.pop("controls", []))
    counts = dict(payload.pop("control_type_counts", {}))
    return UiaTreeReportResult(controls=controls, control_type_counts=counts, **payload)


def _hash_text(value: object) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def safe_text(value: object, *, control_type: str = "", max_chars: int = 60) -> tuple[str, str, int]:
    text = "" if value is None else str(value)
    text = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    digest = _hash_text(text)
    length = len(text)
    if not text:
        return "", digest, 0
    if control_type in _ALWAYS_REDACT_TYPES:
        return f"<name redacted by policy sha256={digest}>", digest, length
    if control_type in _ALLOWED_NAME_CONTROL_TYPES and length <= max_chars:
        return text, digest, length
    return f"<redacted length={length} sha256={digest}>", digest, length


def _rect_text(control: object) -> str:
    try:
        rect = control.rectangle()
        return f"L{rect.left} T{rect.top} R{rect.right} B{rect.bottom}"
    except Exception:
        return ""


def _info_text(info: object, name: str) -> str:
    try:
        value = getattr(info, name)
        return "" if value is None else str(value)
    except Exception:
        return ""


def classify_candidate(control_type: str, class_name: str, name_text: str, automation_id: str, depth: int) -> tuple[str, int]:
    text = " ".join([control_type, class_name, name_text, automation_id]).lower()
    score = 0
    kind = "none"
    if control_type in {"Edit", "ComboBox"}:
        score += 20
        kind = "input_candidate"
    if "address" in text or "search or enter web address" in text or "omnibox" in text:
        score += 80
        kind = "address_bar_candidate"
    elif "search" in text and control_type in {"Edit", "ComboBox"}:
        score += 35
        kind = "search_input_candidate"
    elif "message" in text and control_type in {"Edit", "Document", "Text"}:
        score += 30
        kind = "message_input_candidate_hint"
    if depth <= 3:
        score += 5
    if score <= 0:
        return "none", 0
    return kind, score


def _walk_controls(root: object, *, max_depth: int, max_controls: int) -> list[SafeUiaControlRecord]:
    records: list[SafeUiaControlRecord] = []
    queue: list[tuple[object, int, int | None]] = [(root, 0, None)]
    while queue and len(records) < max_controls:
        control, depth, parent_index = queue.pop(0)
        info = getattr(control, "element_info", None)
        control_type = _info_text(info, "control_type") if info is not None else ""
        class_name = _info_text(info, "class_name") if info is not None else ""
        raw_name = _info_text(info, "name") if info is not None else ""
        automation_id = _info_text(info, "automation_id") if info is not None else ""
        name_redacted, name_hash, name_length = safe_text(raw_name, control_type=control_type, max_chars=60)
        automation_redacted, _, _ = safe_text(automation_id, control_type="Button", max_chars=40)
        candidate_kind, candidate_score = classify_candidate(control_type, class_name, raw_name, automation_id, depth)
        record_index = len(records)
        records.append(SafeUiaControlRecord(
            index=record_index,
            parent_index=parent_index,
            depth=depth,
            control_type=control_type,
            class_name=class_name,
            name_redacted=name_redacted,
            name_hash=name_hash,
            name_length=name_length,
            automation_id_redacted=automation_redacted,
            rectangle=_rect_text(control),
            candidate_kind=candidate_kind,
            candidate_score=candidate_score,
        ))
        if depth >= max_depth:
            continue
        try:
            children = list(control.children())
        except Exception:
            children = []
        for child in children[: max(0, max_controls - len(records))]:
            queue.append((child, depth + 1, record_index))
    return records[:max_controls]


def _control_counts(records: list[SafeUiaControlRecord]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        key = record.control_type or "<unknown>"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[0]))


def _write_tree_text(path: Path, records: list[SafeUiaControlRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.3 bounded normal Edge UIA control tree report",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "Only safe redacted metadata is recorded: control type, class, name hash/length, optional short UI labels, automation id, rectangle, candidate class.",
        "",
    ]
    for record in records:
        indent = "  " * record.depth
        lines.append(
            f"{indent}[{record.index}] parent={record.parent_index} type={record.control_type!r} class={record.class_name!r} "
            f"name={record.name_redacted!r} name_hash={record.name_hash} name_length={record.name_length} "
            f"automation_id={record.automation_id_redacted!r} rect={record.rectangle!r} "
            f"candidate={record.candidate_kind}:{record.candidate_score}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary_text(path: Path, result: UiaTreeReportResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.3 normal Edge UIA control type and candidate summary",
        "conversation_text_logged:false",
        "",
        "CONTROL TYPE COUNTS",
        "-------------------",
    ]
    for key, value in result.control_type_counts.items():
        lines.append(f"{key}: {value}")
    lines.extend(["", "CANDIDATES", "----------"])
    for record in result.controls:
        if record.candidate_kind != "none":
            lines.append(f"[{record.index}] {record.candidate_kind} score={record.candidate_score} type={record.control_type!r} class={record.class_name!r} name={record.name_redacted!r}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _import_pywinauto() -> tuple[bool, str, Any]:
    try:
        import pywinauto  # type: ignore
        return True, "", pywinauto
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}", None


def run_l26_03_tree_report(*, output_dir: str | Path, start_if_missing: bool = True, max_depth: int = 4, max_controls: int = 180) -> UiaTreeReportResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_03_uia_tree_result.json"
    tree_path = out_dir / "normal_edge_l26_03_uia_tree_redacted.txt"
    summary_path = out_dir / "normal_edge_l26_03_control_summary.txt"

    imported, import_error, pywinauto = _import_pywinauto()
    if not imported:
        result = UiaTreeReportResult(failure_layer="pywinauto_import", error=import_error, tree_report_path=str(tree_path), summary_report_path=str(summary_path))
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    try:
        ensure_edge_running(start_if_missing=start_if_missing)
        edge_pids = edge_process_ids()
        desktop = pywinauto.Desktop(backend="uia")
    except Exception as exc:
        result = UiaTreeReportResult(pywinauto_imported=True, failure_layer="uia_or_edge_bootstrap", error=f"{type(exc).__name__}: {exc}", tree_report_path=str(tree_path), summary_report_path=str(summary_path))
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    try:
        candidates, wrappers = discover_edge_windows(desktop, edge_pids)
    except Exception as exc:
        result = UiaTreeReportResult(pywinauto_imported=True, uia_backend_available=True, failure_layer="edge_window_discovery", error=f"{type(exc).__name__}: {exc}", tree_report_path=str(tree_path), summary_report_path=str(summary_path))
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    if not candidates or not wrappers:
        result = UiaTreeReportResult(pywinauto_imported=True, uia_backend_available=True, failure_layer="edge_window_discovery", error="No normal Edge window candidates discovered.", tree_report_path=str(tree_path), summary_report_path=str(summary_path))
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    selected = wrappers[0]
    title_read = candidates[0].title_length > 0
    focused = False
    focus_error = ""
    try:
        selected.set_focus()
        focused = True
    except Exception as exc:
        focus_error = f"{type(exc).__name__}: {exc}"

    records: list[SafeUiaControlRecord] = []
    tree_written = False
    summary_written = False
    error = focus_error
    try:
        records = _walk_controls(selected, max_depth=max_depth, max_controls=max_controls)
        _write_tree_text(tree_path, records)
        tree_written = True
    except Exception as exc:
        error = f"{error}; tree failed: {type(exc).__name__}: {exc}".strip("; ")
    counts = _control_counts(records)
    address_found = any(record.candidate_kind == "address_bar_candidate" for record in records)
    input_count = sum(1 for record in records if record.candidate_kind != "none" and "input" in record.candidate_kind)
    max_depth_observed = max((record.depth for record in records), default=0)

    result_pass = bool(records and tree_written and focused and title_read)
    result = UiaTreeReportResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_window_title_read=title_read,
        edge_focused=focused,
        uia_control_tree_dumped=tree_written,
        control_count_reported=True,
        control_count=len(records),
        max_depth_observed=max_depth_observed,
        tree_report_written=tree_written,
        control_type_summary_written=False,
        address_bar_candidate_found=address_found,
        input_candidate_count=input_count,
        controls=tuple(records[:80]),
        control_type_counts=counts,
        tree_report_path=str(tree_path),
        summary_report_path=str(summary_path),
        result="PASS" if result_pass else "FAIL",
        failure_layer="" if result_pass else "uia_tree_report",
        error="" if result_pass else error,
    )
    try:
        _write_summary_text(summary_path, result)
        summary_written = True
    except Exception as exc:
        result = _with(result, result="FAIL", failure_layer="uia_summary_write", error=f"{type(exc).__name__}: {exc}")
    result = _with(result, control_type_summary_written=summary_written)
    json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
    return result


def assert_l26_03_acceptance(result: UiaTreeReportResult) -> None:
    payload = result.to_payload()
    required_true = [
        "pywinauto_imported",
        "uia_backend_available",
        "normal_edge_attached",
        "edge_window_title_read",
        "edge_focused",
        "uia_control_tree_dumped",
        "control_count_reported",
        "tree_report_written",
        "control_type_summary_written",
    ]
    required_false = [
        "conversation_text_logged",
        "full_conversation_text_logged",
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "browser_navigation_performed",
        "chatgpt_interaction_performed",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if payload.get("control_count", 0) < 1:
        missing_true.append("control_count>=1")
    if not payload.get("control_type_counts"):
        missing_true.append("control_type_counts_present")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.3 acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; failure_layer={result.failure_layer}; error={result.error}")
