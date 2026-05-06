from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Sequence

from patchops.copilot_downloader.browser_target_config import load_browser_target_config
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags

PATCH_NAME = "d1_03_downloader_browser_clipboard_probe"
CLIPBOARD_CONFIRM_TEXT = "PATCHOPS_CONFIRM_CLIPBOARD_READ"
PASS_CLIPBOARD_PROBE_RECORDED = "PASS_CLIPBOARD_PROBE_RECORDED"
PASS_CLIPBOARD_MARKER_DETECTED = "PASS_CLIPBOARD_MARKER_DETECTED"
BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED = "BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED"
BLOCKED_CLIPBOARD_EMPTY = "BLOCKED_CLIPBOARD_EMPTY"
BLOCKED_CLIPBOARD_TOO_LARGE = "BLOCKED_CLIPBOARD_TOO_LARGE"
BLOCKED_CLIPBOARD_UNAVAILABLE = "BLOCKED_CLIPBOARD_UNAVAILABLE"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_CLIPBOARD_PROBE_RECORDED,
    PASS_CLIPBOARD_MARKER_DETECTED,
    BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED,
    BLOCKED_CLIPBOARD_EMPTY,
    BLOCKED_CLIPBOARD_TOO_LARGE,
    BLOCKED_CLIPBOARD_UNAVAILABLE,
})
SCRIPT_BEGIN = "PATCHOPS_SCRIPT_PAYLOAD_BEGIN"
SCRIPT_END = "PATCHOPS_SCRIPT_PAYLOAD_END"
CONFIRM_RUN = "PATCHOPS_CONFIRM_RUN"
DEFAULT_MAX_CHARS = 512_000


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def read_clipboard_text_with_tkinter() -> str:
    try:
        import tkinter as tk  # noqa: PLC0415
    except Exception as exc:
        raise RuntimeError(f"tkinter_unavailable:{exc}") from exc
    root = tk.Tk()
    try:
        root.withdraw()
        value = root.clipboard_get()
    finally:
        root.destroy()
    return str(value)


def summarize_clipboard_text(text: str) -> dict[str, Any]:
    encoded = text.encode("utf-8", errors="replace")
    has_begin = SCRIPT_BEGIN in text
    has_end = SCRIPT_END in text
    has_confirm_run = CONFIRM_RUN in text
    return {
        "sha256": sha256_text(text),
        "size_chars": len(text),
        "size_bytes_utf8": len(encoded),
        "line_count": 0 if text == "" else text.count("\n") + 1,
        "has_patchops_script_payload_begin": has_begin,
        "has_patchops_script_payload_end": has_end,
        "has_patchops_confirm_run_marker": has_confirm_run,
        "has_complete_patchops_script_payload_markers": has_begin and has_end,
        "artifact_marker_detected": has_begin and has_end,
        "content_logged": False,
        "content_preview_logged": False,
    }


def _blocked_payload(
    *,
    label: str,
    issue: str,
    repo_root: Path,
    browser_target: dict[str, Any],
    evidence_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    safety = DownloaderSafetyFlags()
    checks = {
        "clipboard_read_requires_confirmation": True,
        "clipboard_not_read_without_confirmation": True,
        "clipboard_not_written": not safety.clipboard_written,
        "raw_clipboard_text_not_logged": True,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "browser_not_started": not safety.browser_used,
        "selenium_not_used": not safety.selenium_used,
        "webdriver_not_used": not safety.webdriver_used,
        "dom_automation_not_used": not safety.browser_dom_automation_used,
        "copy_not_performed_by_downloader": True,
        "submit_not_performed": not safety.chatgpt_submit_performed,
        "artifact_not_extracted": True,
        "artifact_not_executed": not safety.artifact_executed,
        "uploader_not_imported": True,
    }
    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "repo_root": str(repo_root),
        "browser_target": browser_target,
        "clipboard_summary": None,
        "issue": issue,
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files or {},
    }


def _write_probe_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "clipboard_probe", evidence)


def run_clipboard_probe(
    *,
    repo_root: str | Path | None = None,
    browser_config_path: str | Path = "data/config/copilot_downloader_browser_target.json",
    evidence_root: str | Path | None = None,
    live_clipboard: bool = False,
    confirm_clipboard_text: str = "",
    max_chars: int = DEFAULT_MAX_CHARS,
    write_evidence: bool = True,
    clipboard_provider: Callable[[], str] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    config = load_browser_target_config(browser_config_path, repo_root=root, create_dirs=True)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else config.evidence_dir / "d1_03_clipboard_probe"
    browser_target = config.to_evidence_dict()

    if not live_clipboard:
        label = BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED
        details = {"issue": "live_clipboard_flag_required", "browser_target": browser_target}
        safety = DownloaderSafetyFlags()
        evidence_files = _write_probe_evidence(evidence_dir, label, safety, details) if write_evidence else {}
        return _blocked_payload(label=label, issue="live_clipboard_flag_required", repo_root=root, browser_target=browser_target, evidence_files=evidence_files)
    if confirm_clipboard_text != CLIPBOARD_CONFIRM_TEXT:
        label = BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED
        details = {"issue": "clipboard_confirmation_required", "browser_target": browser_target, "confirmation_supplied": bool(confirm_clipboard_text)}
        safety = DownloaderSafetyFlags()
        evidence_files = _write_probe_evidence(evidence_dir, label, safety, details) if write_evidence else {}
        return _blocked_payload(label=label, issue="clipboard_confirmation_required", repo_root=root, browser_target=browser_target, evidence_files=evidence_files)

    safety = DownloaderSafetyFlags(clipboard_read=True)
    issue: str | None = None
    try:
        provider = clipboard_provider or read_clipboard_text_with_tkinter
        text = str(provider())
    except Exception as exc:
        text = ""
        issue = f"clipboard_read_failed:{exc}"
        label = BLOCKED_CLIPBOARD_UNAVAILABLE
        summary = None
    else:
        if text == "":
            label = BLOCKED_CLIPBOARD_EMPTY
            summary = summarize_clipboard_text(text)
            issue = "clipboard_empty"
        elif len(text) > max_chars:
            label = BLOCKED_CLIPBOARD_TOO_LARGE
            summary = summarize_clipboard_text(text)
            issue = "clipboard_too_large"
        else:
            summary = summarize_clipboard_text(text)
            label = PASS_CLIPBOARD_MARKER_DETECTED if summary["artifact_marker_detected"] else PASS_CLIPBOARD_PROBE_RECORDED

    checks = {
        "clipboard_read_requires_confirmation": True,
        "clipboard_read_confirmation_supplied": confirm_clipboard_text == CLIPBOARD_CONFIRM_TEXT,
        "clipboard_read_performed_only_after_confirmation": safety.clipboard_read and confirm_clipboard_text == CLIPBOARD_CONFIRM_TEXT,
        "clipboard_not_written": not safety.clipboard_written,
        "raw_clipboard_text_not_logged": True,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "browser_not_started": not safety.browser_used,
        "selenium_not_used": not safety.selenium_used,
        "webdriver_not_used": not safety.webdriver_used,
        "dom_automation_not_used": not safety.browser_dom_automation_used,
        "copy_not_performed_by_downloader": True,
        "submit_not_performed": not safety.chatgpt_submit_performed,
        "artifact_not_extracted": True,
        "artifact_not_executed": not safety.artifact_executed,
        "uploader_not_imported": True,
    }
    details = {
        "checks": checks,
        "browser_target": browser_target,
        "clipboard_summary": summary,
        "issue": issue,
        "live_clipboard": live_clipboard,
        "confirmation_supplied": True,
        "max_chars": max_chars,
    }
    evidence_files = _write_probe_evidence(evidence_dir, label, safety, details) if write_evidence else {}
    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "repo_root": str(root),
        "browser_target": browser_target,
        "clipboard_summary": summary,
        "issue": issue,
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.clipboard_probe")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--browser-config-path", default="data/config/copilot_downloader_browser_target.json")
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--live-clipboard", action="store_true")
    parser.add_argument("--confirm-clipboard-text", default="")
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_clipboard_probe(
        repo_root=args.repo_root,
        browser_config_path=args.browser_config_path,
        evidence_root=args.evidence_root,
        live_clipboard=args.live_clipboard,
        confirm_clipboard_text=args.confirm_clipboard_text,
        max_chars=args.max_chars,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())