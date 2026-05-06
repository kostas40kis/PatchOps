from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

from patchops.copilot_downloader.artifact_detector import PARTIAL_OR_TEMP_SUFFIXES, scan_local_artifacts
from patchops.copilot_downloader.config import load_downloader_config
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import ArtifactCandidate, DownloaderEvidenceRecord
from patchops.copilot_downloader.safety_policy import default_safety_flags

PATCH_NAME = "d0_04_downloader_stable_size_detector"
STABLE_PASS_LABEL = "PASS_STABLE_ARTIFACT_VALIDATED"
UNSTABLE_LABEL = "BLOCKED_UNSTABLE_FILE"
NO_ARTIFACT_LABEL = "BLOCKED_NO_ARTIFACT"
AMBIGUOUS_LABEL = "BLOCKED_AMBIGUOUS_ARTIFACTS"


@dataclass(frozen=True)
class FileSizeSample:
    index: int
    size_bytes: int
    modified_timestamp: float
    sampled_timestamp: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "size_bytes": self.size_bytes,
            "modified_timestamp": self.modified_timestamp,
            "sampled_timestamp": self.sampled_timestamp,
        }


@dataclass(frozen=True)
class StableArtifactValidation:
    result_label: str
    candidate: ArtifactCandidate | None
    samples: tuple[FileSizeSample, ...]
    issue: str | None = None

    @property
    def ok(self) -> bool:
        return self.result_label in {STABLE_PASS_LABEL, UNSTABLE_LABEL, NO_ARTIFACT_LABEL, AMBIGUOUS_LABEL}

    @property
    def stable_after_seconds(self) -> float | None:
        if len(self.samples) < 2:
            return None
        return max(0.0, self.samples[-1].sampled_timestamp - self.samples[0].sampled_timestamp)

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_label": self.result_label,
            "candidate": None if self.candidate is None else self.candidate.to_dict(),
            "samples": [sample.to_dict() for sample in self.samples],
            "first_seen": None if not self.samples else self.samples[0].sampled_timestamp,
            "last_seen": None if not self.samples else self.samples[-1].sampled_timestamp,
            "stable_after_seconds": self.stable_after_seconds,
            "issue": self.issue,
        }


def _is_partial_path(path: Path) -> bool:
    lower = path.name.lower()
    return any(lower.endswith(suffix) for suffix in PARTIAL_OR_TEMP_SUFFIXES)


def sample_file_sizes(
    path: Path,
    *,
    sample_count: int = 3,
    interval_seconds: float = 0.2,
    sleep_fn: Callable[[float], None] = time.sleep,
    stat_fn: Callable[[Path], Any] | None = None,
    clock_fn: Callable[[], float] = time.time,
) -> tuple[FileSizeSample, ...]:
    if sample_count < 2:
        raise ValueError("sample_count must be at least 2")
    if interval_seconds < 0:
        raise ValueError("interval_seconds must be non-negative")
    statter = stat_fn or (lambda item: item.stat())
    samples: list[FileSizeSample] = []
    for index in range(sample_count):
        stat_result = statter(path)
        samples.append(
            FileSizeSample(
                index=index,
                size_bytes=int(stat_result.st_size),
                modified_timestamp=float(stat_result.st_mtime),
                sampled_timestamp=float(clock_fn()),
            )
        )
        if index < sample_count - 1 and interval_seconds > 0:
            sleep_fn(interval_seconds)
    return tuple(samples)


def validate_candidate_stable_size(
    candidate: ArtifactCandidate,
    *,
    sample_count: int = 3,
    interval_seconds: float = 0.2,
    sleep_fn: Callable[[float], None] = time.sleep,
    stat_fn: Callable[[Path], Any] | None = None,
    clock_fn: Callable[[], float] = time.time,
) -> StableArtifactValidation:
    if _is_partial_path(candidate.path):
        return StableArtifactValidation(
            result_label=UNSTABLE_LABEL,
            candidate=candidate,
            samples=(),
            issue="partial_or_temporary_extension",
        )
    try:
        samples = sample_file_sizes(
            candidate.path,
            sample_count=sample_count,
            interval_seconds=interval_seconds,
            sleep_fn=sleep_fn,
            stat_fn=stat_fn,
            clock_fn=clock_fn,
        )
    except OSError as exc:
        return StableArtifactValidation(
            result_label=UNSTABLE_LABEL,
            candidate=candidate,
            samples=(),
            issue=f"stat_failed:{exc}",
        )
    sizes = [sample.size_bytes for sample in samples]
    modified = [sample.modified_timestamp for sample in samples]
    if any(size <= 0 for size in sizes):
        return StableArtifactValidation(result_label=UNSTABLE_LABEL, candidate=candidate, samples=samples, issue="empty_or_zero_size_sample")
    if len(set(sizes)) != 1:
        return StableArtifactValidation(result_label=UNSTABLE_LABEL, candidate=candidate, samples=samples, issue="size_changed_across_samples")
    if len(set(modified)) != 1:
        return StableArtifactValidation(result_label=UNSTABLE_LABEL, candidate=candidate, samples=samples, issue="modified_timestamp_changed_across_samples")
    return StableArtifactValidation(result_label=STABLE_PASS_LABEL, candidate=candidate, samples=samples)


def run_stable_artifact_scan(
    *,
    repo_root: str | Path | None = None,
    config_path: str | Path = "data/config/copilot_downloader_config.json",
    evidence_root: str | Path | None = None,
    create_dirs: bool = True,
    write_evidence: bool = True,
    sample_count: int = 3,
    interval_seconds: float = 0.2,
    max_candidates: int = 50,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    config = load_downloader_config(config_path, repo_root=root, create_dirs=create_dirs)
    safety = default_safety_flags()
    scan_result = scan_local_artifacts(
        inbox_dir=config.inbox_dir,
        browser_downloads_dir=config.browser_downloads_dir,
        max_candidates=max_candidates,
    )
    if scan_result.result_label == NO_ARTIFACT_LABEL:
        validation = StableArtifactValidation(result_label=NO_ARTIFACT_LABEL, candidate=None, samples=(), issue="no_artifact")
    elif scan_result.result_label == AMBIGUOUS_LABEL:
        validation = StableArtifactValidation(result_label=AMBIGUOUS_LABEL, candidate=None, samples=(), issue="ambiguous_artifacts")
    else:
        validation = validate_candidate_stable_size(
            scan_result.candidates[0],
            sample_count=sample_count,
            interval_seconds=interval_seconds,
        )

    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else config.evidence_dir / "d0_04_stable_scan"
    checks = {
        "browser_not_used": not safety.browser_used,
        "clipboard_not_used": not safety.clipboard_read and not safety.clipboard_written,
        "artifact_not_executed": not safety.artifact_executed,
        "hash_not_computed": True,
        "staging_not_performed": True,
        "sample_count_at_least_two": sample_count >= 2,
        "partial_downloads_rejected_by_detector": True,
    }
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=validation.result_label,
        safety=safety,
        details={
            "checks": checks,
            "config": config.to_dict(),
            "scan": scan_result.to_dict(),
            "stable_validation": validation.to_dict(),
            "sample_count": sample_count,
            "interval_seconds": interval_seconds,
        },
    )
    evidence_files: dict[str, str] = {}
    if write_evidence:
        evidence_files = write_evidence_pair(evidence_dir, "stable_artifact_scan", evidence)
    return {
        "ok": validation.ok and all(checks.values()),
        "result_label": validation.result_label,
        "candidate_count": len(scan_result.candidates),
        "candidates": [candidate.to_dict() for candidate in scan_result.candidates],
        "stable_validation": validation.to_dict(),
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.stable_detector")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--config-path", default="data/config/copilot_downloader_config.json")
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--no-create-dirs", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    parser.add_argument("--sample-count", type=int, default=3)
    parser.add_argument("--interval-seconds", type=float, default=0.2)
    parser.add_argument("--max-candidates", type=int, default=50)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_stable_artifact_scan(
        repo_root=args.repo_root,
        config_path=args.config_path,
        evidence_root=args.evidence_root,
        create_dirs=not args.no_create_dirs,
        write_evidence=not args.no_write_evidence,
        sample_count=args.sample_count,
        interval_seconds=args.interval_seconds,
        max_candidates=args.max_candidates,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())