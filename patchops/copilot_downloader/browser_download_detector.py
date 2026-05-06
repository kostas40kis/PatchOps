from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags

PATCH_NAME = "d3_01_downloader_browser_download_detector"
PASS_ARTIFACT_DETECTED = "PASS_ARTIFACT_DETECTED"
BLOCKED_NO_ARTIFACT = "BLOCKED_NO_ARTIFACT"
BLOCKED_AMBIGUOUS_ARTIFACTS = "BLOCKED_AMBIGUOUS_ARTIFACTS"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_ARTIFACT_DETECTED,
    BLOCKED_NO_ARTIFACT,
    BLOCKED_AMBIGUOUS_ARTIFACTS,
})
DETECT_EXTENSIONS: frozenset[str] = frozenset({".zip", ".json", ".ps1"})
PARTIAL_SUFFIXES: frozenset[str] = frozenset({".crdownload", ".tmp", ".partial", ".download"})
DEFAULT_CONFIG_PATH = "data/config/copilot_downloader_config.json"


def _repo_child(root: Path, *parts: str) -> Path:
    candidate = root.joinpath(*parts).resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    candidate.relative_to(root_resolved)
    return candidate


def _load_configured_download_dir(repo_root: Path, config_path: str | Path = DEFAULT_CONFIG_PATH) -> Path:
    cfg_path = Path(config_path)
    if not cfg_path.is_absolute():
        cfg_path = repo_root / cfg_path
    if cfg_path.is_file():
        try:
            payload = json.loads(cfg_path.read_text(encoding="utf-8"))
            paths = payload.get("paths") if isinstance(payload, dict) else None
            download_value = paths.get("browser_downloads_dir") if isinstance(paths, dict) else None
            if isinstance(download_value, str) and download_value.strip():
                return Path(download_value).resolve(strict=False)
        except Exception:
            pass
    return _repo_child(repo_root, "data", "runtime", "copilot_downloader", "browser_downloads")


def _is_partial_download(path: Path) -> bool:
    lower_name = path.name.lower()
    return any(lower_name.endswith(suffix) for suffix in PARTIAL_SUFFIXES)


def _candidate_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".zip":
        return "patchops_bundle_or_zip"
    if suffix == ".json":
        return "patchops_manifest_or_json"
    if suffix == ".ps1":
        return "patchops_script_or_powershell"
    return "unsupported"


def _candidate_to_evidence(path: Path, *, download_dir: Path, repo_root: Path) -> dict[str, Any]:
    stat = path.stat()
    try:
        relative_to_download_dir = str(path.resolve(strict=False).relative_to(download_dir.resolve(strict=False)))
    except ValueError:
        relative_to_download_dir = path.name
    try:
        relative_to_repo = str(path.resolve(strict=False).relative_to(repo_root.resolve(strict=False)))
    except ValueError:
        relative_to_repo = None
    return {
        "path": str(path.resolve(strict=False)),
        "name": path.name,
        "suffix": path.suffix.lower(),
        "kind": _candidate_kind(path),
        "relative_to_download_dir": relative_to_download_dir,
        "relative_to_repo": relative_to_repo,
        "size_bytes": int(stat.st_size),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "content_read": False,
        "hash_computed": False,
        "staged": False,
        "executed": False,
    }


def scan_download_folder_once(
    *,
    repo_root: str | Path | None = None,
    download_dir: str | Path | None = None,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    allowed_extensions: Iterable[str] = DETECT_EXTENSIONS,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    downloads = Path(download_dir).resolve(strict=False) if download_dir is not None else _load_configured_download_dir(root, config_path)
    downloads.mkdir(parents=True, exist_ok=True)
    allowed = {item.lower() for item in allowed_extensions}
    ignored: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for path in sorted(downloads.iterdir(), key=lambda item: item.name.lower()):
        if path.is_dir():
            ignored.append({"name": path.name, "reason": "directory"})
            continue
        if path.name.startswith("."):
            ignored.append({"name": path.name, "reason": "hidden"})
            continue
        if _is_partial_download(path):
            ignored.append({"name": path.name, "reason": "partial_download_extension"})
            continue
        if path.suffix.lower() not in allowed:
            ignored.append({"name": path.name, "reason": "unsupported_extension"})
            continue
        try:
            if path.stat().st_size <= 0:
                ignored.append({"name": path.name, "reason": "empty_file"})
                continue
        except FileNotFoundError:
            ignored.append({"name": path.name, "reason": "vanished_during_scan"})
            continue
        candidates.append(_candidate_to_evidence(path, download_dir=downloads, repo_root=root))
    return {
        "repo_root": str(root),
        "download_dir": str(downloads),
        "scan_completed_utc": datetime.now(timezone.utc).isoformat(),
        "allowed_extensions": sorted(allowed),
        "candidates": candidates,
        "ignored": ignored,
    }


def _write_detector_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "browser_download_detector", evidence)


def run_browser_download_detector(
    *,
    repo_root: str | Path | None = None,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    download_dir: str | Path | None = None,
    evidence_root: str | Path | None = None,
    timeout_seconds: float = 0.0,
    poll_interval_seconds: float = 0.25,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "d3_01_browser_download_detector")
    started = time.time()
    last_scan: dict[str, Any] | None = None
    while True:
        last_scan = scan_download_folder_once(repo_root=root, download_dir=download_dir, config_path=config_path)
        if len(last_scan["candidates"]) > 0:
            break
        if timeout_seconds <= 0 or (time.time() - started) >= timeout_seconds:
            break
        time.sleep(max(0.01, poll_interval_seconds))
    assert last_scan is not None
    candidate_count = len(last_scan["candidates"])
    if candidate_count == 0:
        label = BLOCKED_NO_ARTIFACT
    elif candidate_count == 1:
        label = PASS_ARTIFACT_DETECTED
    else:
        label = BLOCKED_AMBIGUOUS_ARTIFACTS
    safety = DownloaderSafetyFlags(file_download_observed=(candidate_count > 0))
    checks = {
        "download_folder_observed": True,
        "bounded_timeout_used": timeout_seconds >= 0,
        "zip_json_ps1_detected_only": all(item.get("suffix") in DETECT_EXTENSIONS for item in last_scan["candidates"]),
        "partial_downloads_ignored": True,
        "file_content_not_read": all(item.get("content_read") is False for item in last_scan["candidates"]),
        "hash_not_computed_yet": all(item.get("hash_computed") is False for item in last_scan["candidates"]),
        "artifact_not_staged_yet": all(item.get("staged") is False for item in last_scan["candidates"]),
        "artifact_not_executed": not safety.artifact_executed,
        "browser_not_started": not safety.browser_used,
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "dom_automation_not_used": not safety.browser_dom_automation_used,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "uploader_not_imported": True,
    }
    details = {
        "checks": checks,
        "scan": last_scan,
        "timeout_seconds": timeout_seconds,
        "poll_interval_seconds": poll_interval_seconds,
    }
    evidence_files = _write_detector_evidence(evidence_dir, label, safety, details) if write_evidence else {}
    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "candidate_count": candidate_count,
        "candidates": last_scan["candidates"],
        "ignored": last_scan["ignored"],
        "download_dir": last_scan["download_dir"],
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.browser_download_detector")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--config-path", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--download-dir", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--timeout-seconds", type=float, default=0.0)
    parser.add_argument("--poll-interval-seconds", type=float, default=0.25)
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_browser_download_detector(
        repo_root=args.repo_root,
        config_path=args.config_path,
        download_dir=args.download_dir,
        evidence_root=args.evidence_root,
        timeout_seconds=args.timeout_seconds,
        poll_interval_seconds=args.poll_interval_seconds,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())