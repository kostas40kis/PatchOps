from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Sequence

from patchops.copilot_downloader.config import load_downloader_config
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import ArtifactCandidate, ArtifactScanResult, DownloaderEvidenceRecord
from patchops.copilot_downloader.safety_policy import default_safety_flags

PATCH_NAME = "d0_03_downloader_local_artifact_detector"
SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({".ps1", ".zip", ".json", ".txt", ".md"})
PARTIAL_OR_TEMP_SUFFIXES: tuple[str, ...] = (".crdownload", ".tmp", ".part", ".partial", ".download")
RUNTIME_INTERNAL_PARTS: frozenset[str] = frozenset({
    "direct_patches",
    "patch_backups",
    "staged",
    "evidence",
    "ledger",
    "__pycache__",
})


def _is_hidden_or_runtime_internal(path: Path) -> bool:
    for part in path.parts:
        if part.startswith("."):
            return True
        if part in RUNTIME_INTERNAL_PARTS:
            return True
    return False


def _ignore_reason(path: Path) -> str | None:
    name_lower = path.name.lower()
    if _is_hidden_or_runtime_internal(path):
        return "hidden_or_runtime_internal"
    if any(name_lower.endswith(suffix) for suffix in PARTIAL_OR_TEMP_SUFFIXES):
        return "partial_or_temporary_extension"
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return "unsupported_extension"
    try:
        if path.stat().st_size <= 0:
            return "empty_file"
    except OSError:
        return "unreadable_stat"
    return None


def _candidate_from_file(path: Path, source: str) -> ArtifactCandidate:
    stat = path.stat()
    return ArtifactCandidate(
        path=path.resolve(strict=False),
        source=source,
        extension=path.suffix.lower(),
        size_bytes=int(stat.st_size),
        modified_timestamp=float(stat.st_mtime),
    )


def iter_local_artifact_candidates(scan_roots: Iterable[tuple[str, Path]]) -> tuple[ArtifactCandidate, ...]:
    candidates: list[ArtifactCandidate] = []
    for source, root in scan_roots:
        if not root.exists() or not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if _ignore_reason(path) is not None:
                continue
            candidates.append(_candidate_from_file(path, source))
    return tuple(sorted(candidates, key=lambda item: (item.modified_timestamp, str(item.path)), reverse=True))


def scan_local_artifacts(
    *,
    inbox_dir: Path,
    browser_downloads_dir: Path,
    max_candidates: int = 50,
) -> ArtifactScanResult:
    scan_roots = (
        ("inbox_dir", inbox_dir),
        ("browser_downloads_dir", browser_downloads_dir),
    )
    candidates = iter_local_artifact_candidates(scan_roots)
    ignored: list[dict[str, Any]] = []
    for source, root in scan_roots:
        if not root.exists() or not root.is_dir():
            ignored.append({"source": source, "path": str(root), "reason": "scan_root_missing"})
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            reason = _ignore_reason(path)
            if reason is not None:
                ignored.append({"source": source, "path": str(path.resolve(strict=False)), "reason": reason})
    candidates = candidates[:max_candidates]
    if len(candidates) == 0:
        label = "BLOCKED_NO_ARTIFACT"
    elif len(candidates) == 1:
        label = "PASS_ARTIFACT_DETECTED"
    else:
        label = "BLOCKED_AMBIGUOUS_ARTIFACTS"
    return ArtifactScanResult(result_label=label, candidates=candidates, ignored=tuple(ignored))


def run_artifact_scan(
    *,
    repo_root: str | Path | None = None,
    config_path: str | Path = "data/config/copilot_downloader_config.json",
    evidence_root: str | Path | None = None,
    create_dirs: bool = True,
    write_evidence: bool = True,
    max_candidates: int = 50,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    config = load_downloader_config(config_path, repo_root=root, create_dirs=create_dirs)
    safety = default_safety_flags()
    if not config.allow_artifact_detection:
        scan_result = ArtifactScanResult(result_label="BLOCKED_INVALID_ARTIFACT", candidates=(), ignored=({"reason": "local_artifact_detection_disabled_by_config"},))
    else:
        scan_result = scan_local_artifacts(
            inbox_dir=config.inbox_dir,
            browser_downloads_dir=config.browser_downloads_dir,
            max_candidates=max_candidates,
        )

    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else config.evidence_dir / "d0_03_artifact_scan"
    checks = {
        "config_allows_local_artifact_detection": config.allow_artifact_detection,
        "browser_not_used": not safety.browser_used,
        "clipboard_not_used": not safety.clipboard_read and not safety.clipboard_written,
        "artifact_not_executed": not safety.artifact_executed,
        "no_hash_or_staging_performed": True,
    }
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=scan_result.result_label,
        safety=safety,
        details={
            "checks": checks,
            "config": config.to_dict(),
            "scan": scan_result.to_dict(),
            "supported_extensions": sorted(SUPPORTED_EXTENSIONS),
            "partial_or_temp_suffixes": list(PARTIAL_OR_TEMP_SUFFIXES),
        },
    )
    evidence_files: dict[str, str] = {}
    if write_evidence:
        evidence_files = write_evidence_pair(evidence_dir, "artifact_scan", evidence)

    return {
        "ok": scan_result.ok and all(checks.values()),
        "result_label": scan_result.result_label,
        "candidate_count": len(scan_result.candidates),
        "candidates": [candidate.to_dict() for candidate in scan_result.candidates],
        "ignored": list(scan_result.ignored),
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.artifact_detector")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--config-path", default="data/config/copilot_downloader_config.json")
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--no-create-dirs", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    parser.add_argument("--max-candidates", type=int, default=50)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_artifact_scan(
        repo_root=args.repo_root,
        config_path=args.config_path,
        evidence_root=args.evidence_root,
        create_dirs=not args.no_create_dirs,
        write_evidence=not args.no_write_evidence,
        max_candidates=args.max_candidates,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())