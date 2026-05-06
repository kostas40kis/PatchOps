from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from patchops.copilot_downloader.browser_target_config import load_browser_target_config
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord
from patchops.copilot_downloader.safety_policy import default_safety_flags

PATCH_NAME = "d1_02_downloader_edge_window_preflight"
LIVE_CONFIRM_TEXT = "PATCHOPS_CONFIRM_LIVE_BROWSER"
PASS_BROWSER_READY = "PASS_BROWSER_READY"
BLOCKED_BROWSER_NOT_READY = "BLOCKED_BROWSER_NOT_READY"
BLOCKED_AMBIGUOUS_BROWSER_TARGET = "BLOCKED_AMBIGUOUS_BROWSER_TARGET"
BLOCKED_LOGIN_OR_CHALLENGE = "BLOCKED_LOGIN_OR_CHALLENGE"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_BROWSER_READY,
    BLOCKED_BROWSER_NOT_READY,
    BLOCKED_AMBIGUOUS_BROWSER_TARGET,
    BLOCKED_LOGIN_OR_CHALLENGE,
})
LOGIN_OR_CHALLENGE_HINTS: tuple[str, ...] = (
    "log in",
    "login",
    "sign in",
    "verify you are human",
    "are you human",
    "captcha",
    "cloudflare",
    "challenge",
    "checking your browser",
)
EDGE_PROCESS_NAMES: frozenset[str] = frozenset({"msedge.exe", "msedge"})


@dataclass(frozen=True)
class WindowSnapshot:
    title: str
    process_name: str = ""
    handle: int | None = None
    class_name: str = ""
    visible: bool = True

    def to_private_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "process_name": self.process_name,
            "handle": self.handle,
            "class_name": self.class_name,
            "visible": self.visible,
        }


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def redact_window_title(title: str) -> str:
    lowered = title.lower()
    if any(hint in lowered for hint in ("captcha", "cloudflare", "verify you are human", "challenge", "checking your browser")):
        return "Microsoft Edge - <challenge-or-verification>"
    if "sign in" in lowered or "log in" in lowered or "login" in lowered:
        return "Microsoft Edge - <login>"
    if "chatgpt" in lowered or "chat.openai.com" in lowered or "chatgpt.com" in lowered:
        return "ChatGPT - Microsoft Edge"
    if "microsoft edge" in lowered:
        return "Microsoft Edge - <redacted-title>"
    return "<redacted-window-title>"


def window_evidence(snapshot: WindowSnapshot) -> dict[str, Any]:
    return {
        "title_sha256": sha256_text(snapshot.title),
        "title_redacted": redact_window_title(snapshot.title),
        "process_name": snapshot.process_name.lower(),
        "handle_present": snapshot.handle is not None,
        "class_name_sha256": sha256_text(snapshot.class_name) if snapshot.class_name else None,
        "visible": snapshot.visible,
    }


def is_edge_window(snapshot: WindowSnapshot) -> bool:
    process = snapshot.process_name.lower()
    title = snapshot.title.lower()
    return snapshot.visible and (process in EDGE_PROCESS_NAMES or "microsoft edge" in title)


def is_target_window(snapshot: WindowSnapshot) -> bool:
    title = snapshot.title.lower()
    return is_edge_window(snapshot) and ("chatgpt" in title or "chat.openai.com" in title or "chatgpt.com" in title)


def has_login_or_challenge(snapshot: WindowSnapshot) -> bool:
    title = snapshot.title.lower()
    return any(hint in title for hint in LOGIN_OR_CHALLENGE_HINTS)


def analyze_edge_windows(windows: Iterable[WindowSnapshot]) -> dict[str, Any]:
    all_windows = tuple(windows)
    edge_windows = tuple(window for window in all_windows if is_edge_window(window))
    target_windows = tuple(window for window in edge_windows if is_target_window(window))
    challenged_windows = tuple(window for window in target_windows if has_login_or_challenge(window))

    if len(edge_windows) == 0:
        label = BLOCKED_BROWSER_NOT_READY
        issue = "no_visible_edge_windows"
    elif len(target_windows) == 0:
        label = BLOCKED_BROWSER_NOT_READY
        issue = "no_visible_chatgpt_edge_window"
    elif len(target_windows) > 1:
        label = BLOCKED_AMBIGUOUS_BROWSER_TARGET
        issue = "multiple_visible_chatgpt_edge_windows"
    elif challenged_windows:
        label = BLOCKED_LOGIN_OR_CHALLENGE
        issue = "login_or_challenge_indicator_detected"
    else:
        label = PASS_BROWSER_READY
        issue = None

    return {
        "result_label": label,
        "ok": label in CONTROLLED_LABELS,
        "issue": issue,
        "observed_window_count": len(all_windows),
        "edge_window_count": len(edge_windows),
        "target_window_count": len(target_windows),
        "windows": [window_evidence(window) for window in edge_windows],
        "selected_window": window_evidence(target_windows[0]) if len(target_windows) == 1 else None,
    }


def collect_visible_edge_windows_with_pywinauto() -> tuple[WindowSnapshot, ...]:
    try:
        from pywinauto import Desktop  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"pywinauto_unavailable:{exc}") from exc

    snapshots: list[WindowSnapshot] = []
    desktop = Desktop(backend="uia")
    for window in desktop.windows(visible_only=True):
        title = ""
        process_name = ""
        class_name = ""
        handle = None
        try:
            title = str(window.window_text() or "")
        except Exception:
            title = ""
        try:
            process_name = str(window.process_name() or "")
        except Exception:
            process_name = ""
        try:
            class_name = str(window.class_name() or "")
        except Exception:
            class_name = ""
        try:
            handle = int(window.handle)
        except Exception:
            handle = None
        if title or process_name:
            snapshot = WindowSnapshot(title=title, process_name=process_name, handle=handle, class_name=class_name, visible=True)
            if is_edge_window(snapshot):
                snapshots.append(snapshot)
    return tuple(snapshots)


def _blocked_analysis(issue: str) -> dict[str, Any]:
    return {
        "result_label": BLOCKED_BROWSER_NOT_READY,
        "ok": True,
        "issue": issue,
        "observed_window_count": 0,
        "edge_window_count": 0,
        "target_window_count": 0,
        "windows": [],
        "selected_window": None,
    }


def run_edge_window_preflight(
    *,
    repo_root: str | Path | None = None,
    browser_config_path: str | Path = "data/config/copilot_downloader_browser_target.json",
    evidence_root: str | Path | None = None,
    live_browser: bool = False,
    confirm_live_browser_text: str = "",
    write_evidence: bool = True,
    window_provider: Any | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    config = load_browser_target_config(browser_config_path, repo_root=root, create_dirs=True)
    safety = default_safety_flags()
    issues: list[str] = []
    provider_error: str | None = None

    confirmed_live = live_browser and confirm_live_browser_text == LIVE_CONFIRM_TEXT
    if not live_browser:
        analysis = _blocked_analysis("live_browser_flag_required")
    elif not confirmed_live:
        analysis = _blocked_analysis("live_browser_confirmation_required")
    else:
        try:
            provider = window_provider or collect_visible_edge_windows_with_pywinauto
            windows = tuple(provider())
            analysis = analyze_edge_windows(windows)
        except Exception as exc:
            provider_error = str(exc)
            analysis = _blocked_analysis("window_provider_failed")
            issues.append(provider_error)

    label = str(analysis["result_label"])
    confirmation_gate_enforced = (not live_browser) or confirmed_live or analysis.get("issue") == "live_browser_confirmation_required"
    window_scan_was_blocked_without_confirmation = confirmed_live or int(analysis.get("observed_window_count", 0)) == 0
    checks = {
        "live_confirmation_gate_enforced": confirmation_gate_enforced,
        "window_scan_not_attempted_without_confirmation": window_scan_was_blocked_without_confirmation,
        "selenium_not_used": not safety.selenium_used,
        "webdriver_not_used": not safety.webdriver_used,
        "browser_not_started": True,
        "dom_automation_not_used": not safety.browser_dom_automation_used,
        "random_clicks_not_performed": not safety.random_page_click_performed,
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "copy_not_performed": True,
        "submit_not_performed": not safety.chatgpt_submit_performed,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "artifact_not_executed": not safety.artifact_executed,
        "uploader_not_imported": True,
        "redacted_window_metadata_only": True,
    }
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else config.evidence_dir / "d1_02_edge_window_preflight"
    details = {
        "checks": checks,
        "browser_target": config.to_evidence_dict(),
        "live_browser": live_browser,
        "confirmation_supplied": bool(confirm_live_browser_text),
        "analysis": analysis,
        "issues": issues,
        "provider_error": provider_error,
    }
    evidence_files: dict[str, str] = {}
    if write_evidence:
        evidence = DownloaderEvidenceRecord(
            patch_name=PATCH_NAME,
            result_label=label,
            safety=safety,
            details=details,
        )
        evidence_files = write_evidence_pair(evidence_dir, "edge_window_preflight", evidence)

    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "checks": checks,
        "safety": safety.to_dict(),
        "browser_target": config.to_evidence_dict(),
        "analysis": analysis,
        "issues": issues,
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.edge_window_preflight")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--browser-config-path", default="data/config/copilot_downloader_browser_target.json")
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default="")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_edge_window_preflight(
        repo_root=args.repo_root,
        browser_config_path=args.browser_config_path,
        evidence_root=args.evidence_root,
        live_browser=args.live_browser,
        confirm_live_browser_text=args.confirm_live_browser_text,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())