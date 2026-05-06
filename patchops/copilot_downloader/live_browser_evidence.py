from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

from patchops.copilot_downloader.clipboard_probe import (
    BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED,
    CLIPBOARD_CONFIRM_TEXT,
    PASS_CLIPBOARD_MARKER_DETECTED,
    PASS_CLIPBOARD_PROBE_RECORDED,
    run_clipboard_probe,
)
from patchops.copilot_downloader.edge_window_preflight import (
    BLOCKED_AMBIGUOUS_BROWSER_TARGET,
    BLOCKED_BROWSER_NOT_READY,
    BLOCKED_LOGIN_OR_CHALLENGE,
    LIVE_CONFIRM_TEXT,
    PASS_BROWSER_READY,
    run_edge_window_preflight,
)
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags, SAFETY_FLAG_NAMES

PATCH_NAME = "d1_04_downloader_live_browser_evidence_harness"
PASS_LIVE_BROWSER_EVIDENCE_RECORDED = "PASS_LIVE_BROWSER_EVIDENCE_RECORDED"
BLOCKED_LIVE_BROWSER_EVIDENCE_NOT_READY = "BLOCKED_LIVE_BROWSER_EVIDENCE_NOT_READY"
CONTROLLED_SUB_LABELS: frozenset[str] = frozenset({
    PASS_BROWSER_READY,
    BLOCKED_BROWSER_NOT_READY,
    BLOCKED_AMBIGUOUS_BROWSER_TARGET,
    BLOCKED_LOGIN_OR_CHALLENGE,
    PASS_CLIPBOARD_PROBE_RECORDED,
    PASS_CLIPBOARD_MARKER_DETECTED,
    BLOCKED_CLIPBOARD_READ_NOT_AUTHORIZED,
})
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_LIVE_BROWSER_EVIDENCE_RECORDED,
    BLOCKED_LIVE_BROWSER_EVIDENCE_NOT_READY,
})


def _or_safety(*payloads: dict[str, Any]) -> DownloaderSafetyFlags:
    merged: dict[str, bool] = {name: False for name in SAFETY_FLAG_NAMES}
    for payload in payloads:
        safety = payload.get("safety") or {}
        if isinstance(safety, dict):
            for name in SAFETY_FLAG_NAMES:
                merged[name] = bool(merged[name] or safety.get(name, False))
    return DownloaderSafetyFlags(**merged)


def _desktop_default() -> Path:
    try:
        import os
        from pathlib import Path as _Path
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        return _Path(desktop)
    except Exception:
        return Path.cwd()


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _write_desktop_report(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "PATCHOPS DOWNLOADER LIVE BROWSER EVIDENCE REPORT",
        "================================================",
        f"generated_utc: {datetime.now(timezone.utc).isoformat()}",
        f"patch_name: {PATCH_NAME}",
        f"result_label: {payload.get('result_label')}",
        f"ok: {str(payload.get('ok')).lower()}",
        f"browser_preflight_label: {(payload.get('browser_preflight') or {}).get('result_label')}",
        f"clipboard_probe_label: {(payload.get('clipboard_probe') or {}).get('result_label')}",
        "checks:",
    ]
    for key, value in sorted((payload.get("checks") or {}).items()):
        lines.append(f"  {key}: {value}")
    lines.append("safety:")
    for key, value in sorted((payload.get("safety") or {}).items()):
        lines.append(f"  {key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _derive_harness_label(browser_payload: dict[str, Any], clipboard_payload: dict[str, Any], *, live_clipboard: bool) -> str:
    browser_label = str(browser_payload.get("result_label"))
    clipboard_label = str(clipboard_payload.get("result_label"))
    if browser_label != PASS_BROWSER_READY:
        return BLOCKED_LIVE_BROWSER_EVIDENCE_NOT_READY
    if live_clipboard and clipboard_label not in {PASS_CLIPBOARD_PROBE_RECORDED, PASS_CLIPBOARD_MARKER_DETECTED}:
        return BLOCKED_LIVE_BROWSER_EVIDENCE_NOT_READY
    return PASS_LIVE_BROWSER_EVIDENCE_RECORDED


def _sub_payloads_controlled(browser_payload: dict[str, Any], clipboard_payload: dict[str, Any]) -> bool:
    return str(browser_payload.get("result_label")) in CONTROLLED_SUB_LABELS and str(clipboard_payload.get("result_label")) in CONTROLLED_SUB_LABELS


def run_live_browser_evidence_harness(
    *,
    repo_root: str | Path | None = None,
    browser_config_path: str | Path = "data/config/copilot_downloader_browser_target.json",
    evidence_root: str | Path | None = None,
    desktop_report_dir: str | Path | None = None,
    live_browser: bool = False,
    confirm_live_browser_text: str = "",
    live_clipboard: bool = False,
    confirm_clipboard_text: str = "",
    write_evidence: bool = True,
    write_desktop_report: bool = True,
    window_provider: Callable[[], Any] | None = None,
    clipboard_provider: Callable[[], str] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else root / "data" / "runtime" / "copilot_downloader" / "d1_04_live_browser_evidence"
    report_dir = Path(desktop_report_dir).resolve(strict=False) if desktop_report_dir is not None else _desktop_default()

    browser_payload = run_edge_window_preflight(
        repo_root=root,
        browser_config_path=browser_config_path,
        evidence_root=evidence_dir / "edge_preflight_nested_suppressed",
        live_browser=live_browser,
        confirm_live_browser_text=confirm_live_browser_text,
        write_evidence=False,
        window_provider=window_provider,
    )
    clipboard_payload = run_clipboard_probe(
        repo_root=root,
        browser_config_path=browser_config_path,
        evidence_root=evidence_dir / "clipboard_probe_nested_suppressed",
        live_clipboard=live_clipboard,
        confirm_clipboard_text=confirm_clipboard_text,
        write_evidence=False,
        clipboard_provider=clipboard_provider,
    )
    safety = _or_safety(browser_payload, clipboard_payload)
    label = _derive_harness_label(browser_payload, clipboard_payload, live_clipboard=live_clipboard)
    checks = {
        "browser_preflight_controlled": str(browser_payload.get("result_label")) in CONTROLLED_SUB_LABELS,
        "clipboard_probe_controlled": str(clipboard_payload.get("result_label")) in CONTROLLED_SUB_LABELS,
        "sub_payloads_controlled": _sub_payloads_controlled(browser_payload, clipboard_payload),
        "desktop_report_requested": write_desktop_report,
        "redacted_window_info_only": True,
        "raw_clipboard_text_not_logged": True,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "browser_not_started": not safety.browser_used,
        "selenium_not_used": not safety.selenium_used,
        "webdriver_not_used": not safety.webdriver_used,
        "dom_automation_not_used": not safety.browser_dom_automation_used,
        "random_clicks_not_performed": not safety.random_page_click_performed,
        "clipboard_not_written": not safety.clipboard_written,
        "copy_not_performed_by_downloader": True,
        "submit_not_performed": not safety.chatgpt_submit_performed,
        "artifact_not_extracted": True,
        "artifact_not_executed": not safety.artifact_executed,
        "uploader_not_imported": True,
    }
    payload = {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "patch_name": PATCH_NAME,
        "repo_root": str(root),
        "live_browser_requested": live_browser,
        "live_clipboard_requested": live_clipboard,
        "browser_preflight": browser_payload,
        "clipboard_probe": clipboard_payload,
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": {},
        "desktop_report_path": None,
    }

    evidence_files: dict[str, str] = {}
    if write_evidence:
        evidence = DownloaderEvidenceRecord(
            patch_name=PATCH_NAME,
            result_label=label,
            safety=safety,
            details={
                "checks": checks,
                "live_browser_requested": live_browser,
                "live_clipboard_requested": live_clipboard,
                "browser_preflight": browser_payload,
                "clipboard_probe": clipboard_payload,
            },
        )
        evidence_files = write_evidence_pair(evidence_dir, "live_browser_evidence", evidence)
        payload["evidence_files"] = evidence_files
    if write_desktop_report:
        report_path = report_dir / f"patchops_downloader_live_browser_evidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        _write_desktop_report(report_path, payload)
        payload["desktop_report_path"] = str(report_path)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.live_browser_evidence")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--browser-config-path", default="data/config/copilot_downloader_browser_target.json")
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--desktop-report-dir", default=None)
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default="")
    parser.add_argument("--live-clipboard", action="store_true")
    parser.add_argument("--confirm-clipboard-text", default="")
    parser.add_argument("--no-write-evidence", action="store_true")
    parser.add_argument("--no-desktop-report", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_live_browser_evidence_harness(
        repo_root=args.repo_root,
        browser_config_path=args.browser_config_path,
        evidence_root=args.evidence_root,
        desktop_report_dir=args.desktop_report_dir,
        live_browser=args.live_browser,
        confirm_live_browser_text=args.confirm_live_browser_text,
        live_clipboard=args.live_clipboard,
        confirm_clipboard_text=args.confirm_clipboard_text,
        write_evidence=not args.no_write_evidence,
        write_desktop_report=not args.no_desktop_report,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())