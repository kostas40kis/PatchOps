"""U0.7A normal Edge focus/target guard for the ChatGPT uploader.

This module provides a conservative target guard for a normal Microsoft Edge
ChatGPT window. U0.7A repairs the live Edge target matcher by allowing a
safe title-based match for normal Edge windows when the current URL is not
visible through UI Automation. It also includes bounded candidate diagnostics
in local evidence so blocked states can be repaired without guessing.

The module never uploads, pastes, sends, reads conversation text, uses DOM
automation, uses Selenium/WebDriver, or bypasses CAPTCHA/Cloudflare.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Protocol
from urllib.parse import urlparse


SAFETY_FLAGS: dict[str, bool] = {
    "webdriver_used": False,
    "selenium_used": False,
    "browser_dom_automation_used": False,
    "cloudflare_bypass_attempted": False,
    "captcha_bypass_attempted": False,
    "file_upload_attempted": False,
    "chatgpt_submit_performed": False,
    "conversation_text_logged": False,
    "random_page_click_performed": False,
    "clipboard_written": False,
}


@dataclass(frozen=True)
class EdgeWindowSnapshot:
    """Safe, bounded metadata about a normal Edge window candidate."""

    handle: str
    title: str = ""
    url: str | None = None
    process_name: str = "msedge.exe"
    is_foreground: bool = False
    class_name: str | None = None
    process_id: int | None = None

    def safe_payload(self) -> dict[str, object]:
        # Do not log page/body/conversation text. Titles and URLs are enough
        # for target readiness evidence in this phase.
        return {
            "handle": self.handle,
            "title": self.title[:160],
            "url": self.url,
            "process_name": self.process_name,
            "process_id": self.process_id,
            "is_foreground": self.is_foreground,
            "class_name": self.class_name,
        }


@dataclass(frozen=True)
class EdgeTargetCandidate:
    window: EdgeWindowSnapshot
    score: int
    reasons: tuple[str, ...] = ()

    def safe_payload(self) -> dict[str, object]:
        return {
            "window": self.window.safe_payload(),
            "score": self.score,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class EdgeFocusGuardResult:
    status: str
    target_url: str
    target_host: str | None
    provider: str
    candidate_count: int
    matching_candidate_count: int
    selected: EdgeTargetCandidate | None = None
    candidates: tuple[EdgeTargetCandidate, ...] = ()
    focus_allowed: bool = False
    focus_attempted: bool = False
    focus_confirmed: bool = False
    reason: str = ""
    safety_flags: Mapping[str, bool] = field(default_factory=lambda: dict(SAFETY_FLAGS))

    @property
    def ok(self) -> bool:
        return self.status in {"PASS_TARGET_READY", "PASS_TARGET_FOCUSED"}

    def to_payload(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "status": self.status,
            "target_url": self.target_url,
            "target_url_sha256": hashlib.sha256(self.target_url.encode("utf-8")).hexdigest(),
            "target_host": self.target_host,
            "provider": self.provider,
            "candidate_count": self.candidate_count,
            "matching_candidate_count": self.matching_candidate_count,
            "selected": self.selected.safe_payload() if self.selected else None,
            "candidates": [candidate.safe_payload() for candidate in self.candidates],
            "focus_allowed": self.focus_allowed,
            "focus_attempted": self.focus_attempted,
            "focus_confirmed": self.focus_confirmed,
            "reason": self.reason,
            "safety_flags": dict(self.safety_flags),
        }

    def to_text(self) -> str:
        payload = self.to_payload()
        lines = [
            "PATCHOPS_CHATGPT_UPLOADER_EDGE_FOCUS_GUARD",
            f"Status              : {payload['status']}",
            f"Provider            : {payload['provider']}",
            f"TargetHost          : {payload['target_host']}",
            f"CandidateCount      : {payload['candidate_count']}",
            f"MatchingCandidates  : {payload['matching_candidate_count']}",
            f"FocusAllowed        : {str(payload['focus_allowed']).lower()}",
            f"FocusAttempted      : {str(payload['focus_attempted']).lower()}",
            f"FocusConfirmed      : {str(payload['focus_confirmed']).lower()}",
            f"Reason              : {payload['reason']}",
            "CANDIDATES",
        ]
        candidates = payload.get("candidates") or []
        if not candidates:
            lines.append("<none>")
        else:
            for index, candidate in enumerate(candidates, 1):
                window = candidate["window"]
                reasons = ",".join(candidate.get("reasons") or []) or "<none>"
                lines.append(f"[{index}] score={candidate['score']} reasons={reasons}")
                lines.append(f"  title:{window.get('title')}")
                lines.append(f"  process_name:{window.get('process_name')}")
                lines.append(f"  process_id:{window.get('process_id')}")
                lines.append(f"  class_name:{window.get('class_name')}")
                lines.append(f"  handle:{window.get('handle')}")
        lines.append("SAFETY_FLAGS")
        for key, value in sorted(dict(payload["safety_flags"]).items()):
            lines.append(f"{key}:{str(value).lower()}")
        lines.append("END_PATCHOPS_CHATGPT_UPLOADER_EDGE_FOCUS_GUARD")
        return "\n".join(lines) + "\n"


class EdgeAdapter(Protocol):
    provider_name: str

    def list_windows(self) -> tuple[EdgeWindowSnapshot, ...]:
        ...

    def focus_window(self, handle: str) -> bool:
        ...


class FakeEdgeAdapter:
    """Deterministic adapter used by default tests and smoke runs."""

    provider_name = "fake"

    def __init__(self, windows: Iterable[EdgeWindowSnapshot] | None = None) -> None:
        self._windows = tuple(windows or ())
        self.focused_handles: list[str] = []

    def list_windows(self) -> tuple[EdgeWindowSnapshot, ...]:
        return self._windows

    def focus_window(self, handle: str) -> bool:
        if any(window.handle == handle for window in self._windows):
            self.focused_handles.append(handle)
            return True
        return False


def _normalized_text(value: str | None) -> str:
    if not value:
        return ""
    # Edge titles can include zero-width format characters, for example
    # "Microsoft\u200b Edge". Remove Unicode control/format chars before matching.
    return "".join(ch for ch in value.lower() if not unicodedata.category(ch).startswith("C"))


def _windows_process_name_for_pid(pid: int) -> str | None:  # pragma: no cover - Windows/operator env only
    if pid <= 0:
        return None
    try:
        completed = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5,
        )
    except Exception:
        return None
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    try:
        rows = list(csv.reader(io.StringIO(completed.stdout)))
    except Exception:
        return None
    if not rows or not rows[0]:
        return None
    name = rows[0][0].strip()
    if name.upper().startswith("INFO:"):
        return None
    return name or None


def _infer_process_name(title: str, class_name: str, pid: int | None = None) -> str:
    if pid is not None:
        process_name = _windows_process_name_for_pid(pid)
        if process_name:
            return process_name
    normalized_title = _normalized_text(title)
    if "microsoft edge" in normalized_title or normalized_title.endswith(" edge"):
        return "msedge.exe"
    if "opera" in normalized_title:
        return "opera.exe"
    if "brave" in normalized_title:
        return "brave.exe"
    if "chrome" in normalized_title and "chrome_widgetwin" not in _normalized_text(class_name):
        return "chrome.exe"
    return "unknown"


class PywinautoEdgeAdapter:
    """Minimal real normal-Edge adapter, gated by caller consent.

    This adapter avoids DOM access and Selenium/WebDriver. It enumerates top
    windows through pywinauto UIA and can focus the selected top-level Edge
    window. It intentionally does not click page controls, inspect
    conversation content, paste text, upload files, or submit messages.
    """

    provider_name = "pywinauto"

    def __init__(self) -> None:
        try:
            from pywinauto import Desktop  # type: ignore
        except Exception as exc:  # pragma: no cover - depends on operator env
            raise RuntimeError(f"pywinauto unavailable: {exc}") from exc
        self._desktop = Desktop(backend="uia")
        self._window_by_handle: dict[str, object] = {}

    def list_windows(self) -> tuple[EdgeWindowSnapshot, ...]:  # pragma: no cover - real UIA only
        snapshots: list[EdgeWindowSnapshot] = []
        self._window_by_handle.clear()
        for window in self._desktop.windows():
            try:
                title = str(window.window_text() or "")
                class_name = str(window.class_name() or "")
                handle = str(int(window.handle))
                process_id = int(window.process_id())
            except Exception:
                continue
            process_name = _infer_process_name(title, class_name, process_id)
            title_norm = _normalized_text(title)
            class_norm = _normalized_text(class_name)
            process_norm = _normalized_text(process_name)
            edge_like = (
                process_norm == "msedge.exe"
                or "microsoft edge" in title_norm
                or title_norm.endswith(" edge")
            )
            chatgpt_like = "chatgpt" in title_norm or "openai" in title_norm
            chromium_window = class_norm == "chrome_widgetwin_1"
            if not (edge_like or chatgpt_like or chromium_window):
                continue
            snapshots.append(
                EdgeWindowSnapshot(
                    handle=handle,
                    title=title,
                    url=None,
                    process_name=process_name,
                    process_id=process_id,
                    is_foreground=False,
                    class_name=class_name,
                )
            )
            self._window_by_handle[handle] = window
        return tuple(snapshots)

    def focus_window(self, handle: str) -> bool:  # pragma: no cover - real UIA only
        window = self._window_by_handle.get(handle)
        if window is None:
            return False
        try:
            window.set_focus()
            return True
        except Exception:
            return False


def target_host_from_url(target_url: str) -> str | None:
    parsed = urlparse(target_url)
    if parsed.scheme != "https":
        return None
    host = (parsed.hostname or "").lower()
    if host == "chatgpt.com" or host.endswith(".chatgpt.com"):
        return host
    return None


def _is_normal_edge_window(window: EdgeWindowSnapshot) -> bool:
    title = _normalized_text(window.title)
    process_name = _normalized_text(window.process_name)
    return (
        process_name == "msedge.exe"
        or "microsoft edge" in title
        or title.endswith(" edge")
    )


def score_window(window: EdgeWindowSnapshot, target_url: str, target_host: str) -> EdgeTargetCandidate:
    reasons: list[str] = []
    score = 0
    url = (window.url or "").strip()
    title = _normalized_text(window.title)
    process_name = _normalized_text(window.process_name)
    class_name = _normalized_text(window.class_name)

    if url:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if url.rstrip("/") == target_url.rstrip("/"):
            score += 100
            reasons.append("exact_target_url")
        if host == target_host:
            score += 30
            reasons.append("target_host_match")
        if host == "chatgpt.com" or host.endswith(".chatgpt.com"):
            score += 20
            reasons.append("chatgpt_host")

    if target_host and target_host in title:
        score += 40
        reasons.append("title_contains_target_host")
    if "chatgpt" in title:
        score += 40
        reasons.append("chatgpt_title")
    if "openai" in title:
        score += 30
        reasons.append("openai_title")
    if _is_normal_edge_window(window):
        score += 30
        reasons.append("normal_edge_window")
    if class_name == "chrome_widgetwin_1":
        score += 10
        reasons.append("chromium_top_window")
    if process_name and process_name not in {"msedge.exe", "unknown"}:
        reasons.append(f"non_edge_process:{process_name}")
        if not _is_normal_edge_window(window):
            score -= 20

    return EdgeTargetCandidate(window=window, score=score, reasons=tuple(reasons))


def _strong_candidates(candidates: Iterable[EdgeTargetCandidate]) -> list[EdgeTargetCandidate]:
    result: list[EdgeTargetCandidate] = []
    for candidate in candidates:
        reasons = set(candidate.reasons)
        is_exact = "exact_target_url" in reasons
        is_title_edge = (
            ("chatgpt_title" in reasons or "title_contains_target_host" in reasons or "openai_title" in reasons)
            and "normal_edge_window" in reasons
        )
        if is_exact or (is_title_edge and candidate.score >= 60):
            result.append(candidate)
    return sorted(result, key=lambda item: item.score, reverse=True)


def guard_target(
    target_url: str,
    adapter: EdgeAdapter,
    *,
    allow_focus: bool = False,
) -> EdgeFocusGuardResult:
    target_host = target_host_from_url(target_url)
    if target_host is None:
        return EdgeFocusGuardResult(
            status="BLOCKED_INVALID_TARGET_URL",
            target_url=target_url,
            target_host=None,
            provider=adapter.provider_name,
            candidate_count=0,
            matching_candidate_count=0,
            reason="Target URL must be an https://chatgpt.com URL.",
        )

    windows = adapter.list_windows()
    candidates = tuple(score_window(window, target_url, target_host) for window in windows)
    matches = _strong_candidates(candidates)

    if not matches:
        return EdgeFocusGuardResult(
            status="BLOCKED_TARGET_NOT_FOUND",
            target_url=target_url,
            target_host=target_host,
            provider=adapter.provider_name,
            candidate_count=len(windows),
            matching_candidate_count=0,
            candidates=candidates,
            reason="No normal Edge ChatGPT target window was found.",
        )
    if len(matches) > 1:
        return EdgeFocusGuardResult(
            status="BLOCKED_AMBIGUOUS_TARGET",
            target_url=target_url,
            target_host=target_host,
            provider=adapter.provider_name,
            candidate_count=len(windows),
            matching_candidate_count=len(matches),
            candidates=candidates,
            reason="Multiple normal Edge ChatGPT target windows were found.",
        )

    selected = matches[0]

    if allow_focus:
        focus_confirmed = adapter.focus_window(selected.window.handle)
        return EdgeFocusGuardResult(
            status="PASS_TARGET_FOCUSED" if focus_confirmed else "BLOCKED_FOCUS_FAILED",
            target_url=target_url,
            target_host=target_host,
            provider=adapter.provider_name,
            candidate_count=len(windows),
            matching_candidate_count=1,
            selected=selected,
            candidates=candidates,
            focus_allowed=True,
            focus_attempted=True,
            focus_confirmed=focus_confirmed,
            reason="Target window focus confirmed." if focus_confirmed else "Target window focus failed.",
        )

    return EdgeFocusGuardResult(
        status="PASS_TARGET_READY",
        target_url=target_url,
        target_host=target_host,
        provider=adapter.provider_name,
        candidate_count=len(windows),
        matching_candidate_count=1,
        selected=selected,
        candidates=candidates,
        focus_allowed=False,
        focus_attempted=False,
        focus_confirmed=False,
        reason="Target window found; focus not attempted because allow_focus is false.",
    )


def build_adapter(provider: str, *, target_url: str, allow_real_edge: bool) -> EdgeAdapter:
    if provider == "fake":
        return FakeEdgeAdapter(
            [
                EdgeWindowSnapshot(
                    handle="fake-edge-1",
                    title="ChatGPT - Microsoft Edge",
                    url=target_url,
                    process_name="msedge.exe",
                )
            ]
        )
    if provider == "fake-missing":
        return FakeEdgeAdapter(
            [
                EdgeWindowSnapshot(
                    handle="fake-edge-1",
                    title="New tab - Microsoft Edge",
                    url="https://example.com/",
                    process_name="msedge.exe",
                )
            ]
        )
    if provider == "pywinauto":
        if not allow_real_edge:
            raise PermissionError("Real Edge access requires --allow-real-edge.")
        return PywinautoEdgeAdapter()
    raise ValueError(f"Unknown provider: {provider}")


def run_guard(
    *,
    target_url: str,
    provider: str = "fake",
    allow_focus: bool = False,
    allow_real_edge: bool = False,
) -> EdgeFocusGuardResult:
    try:
        adapter = build_adapter(provider, target_url=target_url, allow_real_edge=allow_real_edge)
    except PermissionError as exc:
        host = target_host_from_url(target_url)
        return EdgeFocusGuardResult(
            status="BLOCKED_REAL_EDGE_NOT_ALLOWED",
            target_url=target_url,
            target_host=host,
            provider=provider,
            candidate_count=0,
            matching_candidate_count=0,
            reason=str(exc),
        )
    except Exception as exc:
        host = target_host_from_url(target_url)
        return EdgeFocusGuardResult(
            status="BLOCKED_ADAPTER_ERROR",
            target_url=target_url,
            target_host=host,
            provider=provider,
            candidate_count=0,
            matching_candidate_count=0,
            reason=str(exc),
        )
    return guard_target(target_url, adapter, allow_focus=allow_focus)


def write_evidence(result: EdgeFocusGuardResult, output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "edge_focus_guard_result.json"
    txt_path = output_dir / "edge_focus_guard_result.txt"
    json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
    txt_path.write_text(result.to_text(), encoding="utf-8")
    return {"json_path": str(json_path), "txt_path": str(txt_path)}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PatchOps ChatGPT uploader U0.7A Edge focus/target guard")
    parser.add_argument("--target-url", default="https://chatgpt.com/", help="Expected ChatGPT target URL")
    parser.add_argument("--provider", choices=("fake", "fake-missing", "pywinauto"), default="fake")
    parser.add_argument("--allow-focus", action="store_true", help="Allow focusing the selected Edge window")
    parser.add_argument("--allow-real-edge", action="store_true", help="Allow real pywinauto Edge enumeration/focus")
    parser.add_argument("--output-dir", default="data/runtime/u0_07_chatgpt_uploader_edge_focus_guard")
    parser.add_argument("--json", action="store_true", help="Print JSON payload instead of text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    result = run_guard(
        target_url=args.target_url,
        provider=args.provider,
        allow_focus=args.allow_focus,
        allow_real_edge=args.allow_real_edge,
    )
    paths = write_evidence(result, Path(args.output_dir))
    payload = result.to_payload()
    payload["evidence_paths"] = paths
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(result.to_text(), end="")
        print(f"EvidenceJson       : {paths['json_path']}")
        print(f"EvidenceText       : {paths['txt_path']}")
    return 0 if result.ok else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
