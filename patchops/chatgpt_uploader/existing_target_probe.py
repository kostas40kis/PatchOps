from __future__ import annotations

import csv
import hashlib
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit


CHATGPT_TITLE_HINTS = ("chatgpt", "chat.openai", "openai")
EDGE_PROCESS_NAMES = ("msedge.exe", "msedge")


@dataclass(frozen=True)
class ExistingTargetProbeResult:
    existing_target_probe_attempted: bool
    existing_target_found: bool
    existing_target_focused: bool
    launch_skipped_existing_target: bool
    normal_edge_launch_attempted: bool
    candidate_count: int
    candidate_match_count: int
    edge_candidate_count: int
    non_edge_chatgpt_candidate_count: int
    candidate_rejected_non_edge_count: int
    dependency_available: bool
    failure_layer: str
    classification: str
    title_hashes: tuple[str, ...]
    handle_hexes: tuple[str, ...]
    process_ids: tuple[int, ...]
    process_name_hashes: tuple[str, ...]
    target_host_hint: str
    target_path_depth_hint: int
    conversation_text_logged: bool = False
    file_upload_attempted: bool = False
    chatgpt_submit_performed: bool = False
    selenium_used: bool = False
    webdriver_used: bool = False
    browser_dom_automation_used: bool = False

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _sha256_text(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8", errors="replace")).hexdigest()


def _target_host_hint(target_url: str | None) -> str:
    parsed = urlsplit(target_url or "")
    return parsed.netloc.lower() or "chatgpt.com"


def _target_path_depth_hint(target_url: str | None) -> int:
    parsed = urlsplit(target_url or "")
    return len([part for part in (parsed.path or "").split("/") if part])


def _title_matches_target(title: str, target_url: str | None = None) -> bool:
    lowered = (title or "").lower()
    if any(hint in lowered for hint in CHATGPT_TITLE_HINTS):
        return True
    host = _target_host_hint(target_url)
    return bool(host and host in lowered)


def _normalize_process_name(value: str | None) -> str:
    raw = str(value or "").strip().strip('"').lower()
    if not raw:
        return ""
    return Path(raw).name.lower()


def _is_edge_process_name(value: str | None) -> bool:
    return _normalize_process_name(value) in EDGE_PROCESS_NAMES


def _tasklist_process_name(pid: int) -> str:
    if os.name != "nt" or not pid:
        return ""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {int(pid)}", "/FO", "CSV", "/NH"],
            text=True,
            capture_output=True,
            timeout=5,
            shell=False,
        )
    except Exception:
        return ""

    output = (result.stdout or "").strip()
    if not output or "No tasks" in output:
        return ""

    try:
        rows = list(csv.reader(output.splitlines()))
        if rows and rows[0]:
            return _normalize_process_name(rows[0][0])
    except Exception:
        return ""

    return ""


def _candidate_title(candidate: Any) -> str:
    if isinstance(candidate, dict):
        return str(candidate.get("title") or candidate.get("window_text") or "")
    try:
        return str(candidate.window_text() or "")
    except Exception:
        return ""


def _candidate_handle(candidate: Any) -> int:
    if isinstance(candidate, dict):
        return int(candidate.get("handle") or 0)
    return int(getattr(candidate, "handle", 0) or 0)


def _candidate_pid(candidate: Any) -> int:
    if isinstance(candidate, dict):
        return int(candidate.get("process_id") or candidate.get("pid") or 0)
    try:
        return int(candidate.process_id())
    except Exception:
        return 0


def _candidate_process_name(candidate: Any) -> str:
    if isinstance(candidate, dict):
        return _normalize_process_name(candidate.get("process_name") or candidate.get("image_name") or candidate.get("exe"))
    pid = _candidate_pid(candidate)
    return _tasklist_process_name(pid)


def _focus_candidate(candidate: Any) -> tuple[bool, str]:
    if isinstance(candidate, dict):
        return bool(candidate.get("focus_ok", True)), ""

    try:
        try:
            candidate.set_focus()
        except Exception:
            candidate.wrapper_object().set_focus()
        return True, ""
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def _empty_result(
    *,
    target_url: str | None,
    candidate_count: int = 0,
    dependency_available: bool = True,
    failure_layer: str,
    classification: str,
    edge_candidate_count: int = 0,
    non_edge_chatgpt_candidate_count: int = 0,
    candidate_rejected_non_edge_count: int = 0,
) -> ExistingTargetProbeResult:
    return ExistingTargetProbeResult(
        existing_target_probe_attempted=True,
        existing_target_found=False,
        existing_target_focused=False,
        launch_skipped_existing_target=False,
        normal_edge_launch_attempted=False,
        candidate_count=candidate_count,
        candidate_match_count=0,
        edge_candidate_count=edge_candidate_count,
        non_edge_chatgpt_candidate_count=non_edge_chatgpt_candidate_count,
        candidate_rejected_non_edge_count=candidate_rejected_non_edge_count,
        dependency_available=dependency_available,
        failure_layer=failure_layer,
        classification=classification,
        title_hashes=tuple(),
        handle_hexes=tuple(),
        process_ids=tuple(),
        process_name_hashes=tuple(),
        target_host_hint=_target_host_hint(target_url),
        target_path_depth_hint=_target_path_depth_hint(target_url),
    )


def probe_existing_target_from_candidates(
    candidates: Iterable[Any],
    *,
    target_url: str | None = None,
    focused: bool = False,
    require_edge_process: bool = True,
) -> ExistingTargetProbeResult:
    all_candidates = list(candidates)

    edge_title_matches: list[Any] = []
    non_edge_chatgpt_count = 0
    edge_candidate_count = 0
    rejected_non_edge_count = 0

    for candidate in all_candidates:
        title = _candidate_title(candidate)
        process_name = _candidate_process_name(candidate)
        is_edge = _is_edge_process_name(process_name)

        if is_edge:
            edge_candidate_count += 1

        title_match = _title_matches_target(title, target_url)
        if not title_match:
            continue

        if require_edge_process and not is_edge:
            non_edge_chatgpt_count += 1
            rejected_non_edge_count += 1
            continue

        edge_title_matches.append(candidate)

    if not edge_title_matches:
        if non_edge_chatgpt_count:
            return _empty_result(
                target_url=target_url,
                candidate_count=len(all_candidates),
                edge_candidate_count=edge_candidate_count,
                non_edge_chatgpt_candidate_count=non_edge_chatgpt_count,
                candidate_rejected_non_edge_count=rejected_non_edge_count,
                failure_layer="non_edge_browser_ignored",
                classification="non_edge_chatgpt_window_ignored",
            )

        return _empty_result(
            target_url=target_url,
            candidate_count=len(all_candidates),
            edge_candidate_count=edge_candidate_count,
            non_edge_chatgpt_candidate_count=non_edge_chatgpt_count,
            candidate_rejected_non_edge_count=rejected_non_edge_count,
            failure_layer="existing_target_not_found",
            classification="existing_edge_target_not_found",
        )

    title_hashes: list[str] = []
    handle_hexes: list[str] = []
    process_ids: list[int] = []
    process_name_hashes: list[str] = []

    for candidate in edge_title_matches:
        title_hashes.append(_sha256_text(_candidate_title(candidate)))

        handle = _candidate_handle(candidate)
        if handle:
            handle_hexes.append(hex(handle))

        pid = _candidate_pid(candidate)
        process_ids.append(pid)

        process_name = _candidate_process_name(candidate)
        process_name_hashes.append(_sha256_text(process_name))

    did_focus = False
    focus_error = ""

    if focused:
        did_focus = True
    else:
        did_focus, focus_error = _focus_candidate(edge_title_matches[0])

    classification = "existing_edge_target_found"
    failure_layer = ""

    if not did_focus:
        classification = "existing_edge_target_found_not_focusable"
        failure_layer = "target_found_but_not_focusable"

    if focus_error:
        classification = f"{classification}:{focus_error}"

    return ExistingTargetProbeResult(
        existing_target_probe_attempted=True,
        existing_target_found=True,
        existing_target_focused=did_focus,
        launch_skipped_existing_target=True,
        normal_edge_launch_attempted=False,
        candidate_count=len(all_candidates),
        candidate_match_count=len(edge_title_matches),
        edge_candidate_count=edge_candidate_count,
        non_edge_chatgpt_candidate_count=non_edge_chatgpt_count,
        candidate_rejected_non_edge_count=rejected_non_edge_count,
        dependency_available=True,
        failure_layer=failure_layer,
        classification=classification,
        title_hashes=tuple(title_hashes),
        handle_hexes=tuple(handle_hexes),
        process_ids=tuple(process_ids),
        process_name_hashes=tuple(process_name_hashes),
        target_host_hint=_target_host_hint(target_url),
        target_path_depth_hint=_target_path_depth_hint(target_url),
    )


def probe_existing_target_from_titles(
    titles: Iterable[str],
    *,
    target_url: str | None = None,
    focused: bool = False,
) -> ExistingTargetProbeResult:
    # Backward-compatible synthetic helper for tests only.
    # Real live probing must use process identity and will reject Opera/Chrome.
    candidates = [
        {
            "title": str(title or ""),
            "process_name": "msedge.exe",
            "process_id": 0,
            "handle": 0,
            "focus_ok": bool(focused),
        }
        for title in titles
    ]
    return probe_existing_target_from_candidates(candidates, target_url=target_url, focused=focused)


def probe_existing_edge_target(
    *,
    target_url: str | None = None,
    focus: bool = True,
) -> ExistingTargetProbeResult:
    try:
        from pywinauto import Desktop  # type: ignore
    except Exception:
        return _empty_result(
            target_url=target_url,
            dependency_available=False,
            failure_layer="pywinauto_missing",
            classification="blocked_dependency_missing",
        )

    candidates: list[Any] = []
    for backend in ("uia", "win32"):
        try:
            candidates.extend(Desktop(backend=backend).windows())
        except Exception:
            continue

    seen_handles: set[int] = set()
    normalized_candidates: list[Any] = []
    for candidate in candidates:
        handle = _candidate_handle(candidate)
        if handle and handle in seen_handles:
            continue
        if handle:
            seen_handles.add(handle)
        normalized_candidates.append(candidate)

    return probe_existing_target_from_candidates(
        normalized_candidates,
        target_url=target_url,
        focused=not focus,
        require_edge_process=True,
    )


def start_normal_edge_target(target_url: str) -> bool:
    if os.name != "nt":
        return False
    try:
        subprocess.Popen(f'start "" msedge "{target_url}"', shell=True)
        return True
    except Exception:
        return False
