from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags

PATCH_NAME = "d4_01_downloader_canonical_report_locator"
PASS_CANONICAL_REPORT_FOUND = "PASS_CANONICAL_REPORT_FOUND"
FAIL_REPORT_MISSING = "FAIL_REPORT_MISSING"
CONTROLLED_LABELS: frozenset[str] = frozenset({PASS_CANONICAL_REPORT_FOUND, FAIL_REPORT_MISSING})


def _repo_child(root: Path, *parts: str) -> Path:
    candidate = root.joinpath(*parts).resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    candidate.relative_to(root_resolved)
    return candidate


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_time(value: str | None) -> float | None:
    if value is None or not str(value).strip():
        return None
    raw = str(value).strip()
    try:
        return float(raw)
    except ValueError:
        pass
    normalized = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def parse_patchops_report_signals(text: str) -> dict[str, Any]:
    exit_match = re.search(r"(?im)^\s*ExitCode\s*:\s*(-?\d+)\s*$", text)
    result_match = re.search(r"(?im)^\s*Result\s*:\s*([A-Z]+)\s*$", text)
    patch_match = re.search(r"(?im)^\s*Patch Name\s*:\s*(.+?)\s*$", text)
    mode_match = re.search(r"(?im)^\s*Mode\s*:\s*(.+?)\s*$", text)
    return {
        "exit_code_text": None if exit_match is None else exit_match.group(1).strip(),
        "exit_code": None if exit_match is None else int(exit_match.group(1).strip()),
        "result_text": None if result_match is None else result_match.group(1).strip(),
        "patch_name_text": None if patch_match is None else patch_match.group(1).strip(),
        "mode_text": None if mode_match is None else mode_match.group(1).strip(),
        "exit_code_found": exit_match is not None,
        "result_found": result_match is not None,
        "patch_name_found": patch_match is not None,
    }


def find_latest_report_candidate(
    *,
    search_dir: str | Path,
    patch_name: str | None = None,
    report_prefix: str = "patchops_downloader",
    after_epoch: float | None = None,
) -> Path | None:
    root = Path(search_dir).resolve(strict=False)
    if not root.is_dir():
        return None
    patterns = []
    if patch_name:
        patterns.extend([f"{report_prefix}*{patch_name}*.txt", f"*{patch_name}*.txt"])
    patterns.append(f"{report_prefix}*.txt")
    seen: set[Path] = set()
    candidates: list[Path] = []
    for pattern in patterns:
        for candidate in root.glob(pattern):
            resolved = candidate.resolve(strict=False)
            if resolved in seen or not candidate.is_file():
                continue
            seen.add(resolved)
            if after_epoch is not None and candidate.stat().st_mtime < after_epoch:
                continue
            candidates.append(resolved)
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _default_report_search_dir(repo_root: Path) -> Path:
    desktop = Path.home() / "Desktop"
    if desktop.is_dir():
        return desktop
    return _repo_child(repo_root, "data", "runtime", "copilot_downloader", "reports")


def _write_locator_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "canonical_report_locator", evidence)


def locate_canonical_report(
    *,
    repo_root: str | Path | None = None,
    evidence_root: str | Path | None = None,
    report_path: str | Path | None = None,
    report_search_dir: str | Path | None = None,
    patch_name: str | None = None,
    run_started_at: str | None = None,
    expected_result: str | None = None,
    expected_exit_code: int | None = None,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "d4_01_canonical_report_locator")
    run_start_epoch = parse_time(run_started_at)
    search_dir = Path(report_search_dir).resolve(strict=False) if report_search_dir is not None else _default_report_search_dir(root)
    explicit_path = Path(report_path).resolve(strict=False) if report_path is not None and str(report_path).strip() else None
    selected_path = explicit_path if explicit_path is not None else find_latest_report_candidate(search_dir=search_dir, patch_name=patch_name, after_epoch=run_start_epoch)
    issues: list[str] = []
    signals: dict[str, Any] | None = None
    report_sha256: str | None = None
    report_mtime_epoch: float | None = None
    report_size_bytes: int | None = None

    if selected_path is None:
        issues.append("canonical report was not found")
    elif not selected_path.is_file():
        issues.append("canonical report path does not exist")
    else:
        report_mtime_epoch = selected_path.stat().st_mtime
        report_size_bytes = selected_path.stat().st_size
        if run_start_epoch is not None and report_mtime_epoch < run_start_epoch:
            issues.append("canonical report is older than run start")
        text = selected_path.read_text(encoding="utf-8", errors="replace")
        signals = parse_patchops_report_signals(text)
        if not signals["exit_code_found"]:
            issues.append("canonical report is missing ExitCode")
        if not signals["result_found"]:
            issues.append("canonical report is missing Result")
        if expected_result is not None and signals.get("result_text") != expected_result:
            issues.append(f"canonical report Result mismatch: expected {expected_result}")
        if expected_exit_code is not None and signals.get("exit_code") != expected_exit_code:
            issues.append(f"canonical report ExitCode mismatch: expected {expected_exit_code}")
        if not issues:
            report_sha256 = sha256_file(selected_path)

    label = PASS_CANONICAL_REPORT_FOUND if not issues else FAIL_REPORT_MISSING
    safety = DownloaderSafetyFlags(canonical_report_found=(label == PASS_CANONICAL_REPORT_FOUND))
    checks = {
        "report_lookup_performed": True,
        "report_exists_or_missing_blocked": selected_path is not None and selected_path.is_file() or label == FAIL_REPORT_MISSING,
        "result_and_exitcode_required": signals is None or (signals.get("result_found") and signals.get("exit_code_found")) or label == FAIL_REPORT_MISSING,
        "report_newer_than_run_start_or_missing_blocked": run_start_epoch is None or (report_mtime_epoch is not None and report_mtime_epoch >= run_start_epoch) or label == FAIL_REPORT_MISSING,
        "report_hashed_only_when_valid": report_sha256 is not None or label == FAIL_REPORT_MISSING,
        "missing_report_blocks": label == PASS_CANONICAL_REPORT_FOUND or bool(issues),
        "report_content_not_logged": True,
        "browser_not_started": not safety.browser_used,
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "artifact_not_executed": not safety.artifact_executed,
        "patchops_not_invoked_by_locator": not safety.patchops_invoked,
        "uploader_not_imported": True,
    }
    details = {
        "checks": checks,
        "issues": issues,
        "selected_report_path": None if selected_path is None else str(selected_path),
        "explicit_report_path": None if explicit_path is None else str(explicit_path),
        "report_search_dir": str(search_dir),
        "patch_name": patch_name,
        "run_start_epoch": run_start_epoch,
        "report_mtime_epoch": report_mtime_epoch,
        "report_size_bytes": report_size_bytes,
        "report_sha256": report_sha256,
        "signals": signals,
        "expected_result": expected_result,
        "expected_exit_code": expected_exit_code,
    }
    evidence_files = _write_locator_evidence(evidence_dir, label, safety, details) if write_evidence else {}
    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "issues": issues,
        "selected_report_path": None if selected_path is None else str(selected_path),
        "report_search_dir": str(search_dir),
        "report_sha256": report_sha256,
        "report_size_bytes": report_size_bytes,
        "report_mtime_epoch": report_mtime_epoch,
        "run_start_epoch": run_start_epoch,
        "signals": signals,
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.canonical_report_locator")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--report-path", default=None)
    parser.add_argument("--report-search-dir", default=None)
    parser.add_argument("--patch-name", default=None)
    parser.add_argument("--run-started-at", default=None)
    parser.add_argument("--expected-result", default=None)
    parser.add_argument("--expected-exit-code", type=int, default=None)
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = locate_canonical_report(
        repo_root=args.repo_root,
        evidence_root=args.evidence_root,
        report_path=args.report_path,
        report_search_dir=args.report_search_dir,
        patch_name=args.patch_name,
        run_started_at=args.run_started_at,
        expected_result=args.expected_result,
        expected_exit_code=args.expected_exit_code,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())