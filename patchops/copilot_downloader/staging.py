from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.classifier import PATCHOPS_BUNDLE_KIND, PATCHOPS_SCRIPT_KIND
from patchops.copilot_downloader.config import load_downloader_config
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.ledger import compute_sha256
from patchops.copilot_downloader.models import (
    BLOCKED_STAGE_MISSING_SOURCE,
    FAIL_STAGE_WRITE,
    PASS_BUNDLE_VALIDATED_RUN_BLOCKED,
    PASS_STAGED_ARTIFACT_READY,
    DownloaderEvidenceRecord,
    StagedArtifact,
)
from patchops.copilot_downloader.safety_policy import default_safety_flags
from patchops.copilot_downloader.script_validator import extract_single_marked_payload, read_script_text
from patchops.copilot_downloader.shape_validator import run_shape_validation_scan

PATCH_NAME = "d0_08_downloader_quarantine_staging"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_STAGED_ARTIFACT_READY,
    BLOCKED_STAGE_MISSING_SOURCE,
    FAIL_STAGE_WRITE,
    "BLOCKED_NO_ARTIFACT",
    "BLOCKED_UNSTABLE_FILE",
    "BLOCKED_INVALID_ARTIFACT",
    "BLOCKED_AMBIGUOUS_ARTIFACTS",
})


def _assert_sha256(value: str) -> None:
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError(f"invalid sha256 folder name: {value!r}")


def _assert_under_root(root: Path, candidate: Path) -> None:
    root_resolved = root.resolve(strict=False)
    candidate_resolved = candidate.resolve(strict=False)
    candidate_resolved.relative_to(root_resolved)


def normalized_script_from_marked_payload_file(path: str | Path) -> str:
    artifact_path = Path(path)
    payload, issues = extract_single_marked_payload(read_script_text(artifact_path))
    if payload is None:
        raise ValueError("cannot normalize script payload: " + "; ".join(issues))
    match = re.search(r"(?s)&\s*\{.*\}\s*$", payload.strip())
    if match is None:
        raise ValueError("cannot normalize script payload: missing terminal & { ... } block")
    return match.group(0).rstrip() + "\n"


def build_staging_metadata(
    *,
    artifact_sha256: str,
    artifact_kind: str,
    source_path: Path,
    raw_artifact_path: Path,
    normalized_script_path: Path | None,
    shape_payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "producer": "patchops.copilot_downloader",
        "patch_name": PATCH_NAME,
        "staged_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_sha256": artifact_sha256,
        "artifact_kind": artifact_kind,
        "source_path": str(source_path),
        "raw_artifact_path": str(raw_artifact_path),
        "normalized_script_path": None if normalized_script_path is None else str(normalized_script_path),
        "shape_payload": shape_payload,
        "execution_allowed": False,
        "patchops_invoked": False,
        "browser_or_clipboard_source_executed_directly": False,
    }


def stage_validated_artifact(
    *,
    source_path: str | Path,
    artifact_kind: str,
    staging_root: str | Path,
    artifact_sha256: str | None = None,
    shape_payload: dict[str, Any] | None = None,
) -> StagedArtifact:
    source = Path(source_path).resolve(strict=False)
    if not source.is_file():
        raise FileNotFoundError(f"source artifact missing: {source}")
    sha256 = (artifact_sha256 or compute_sha256(source)).lower()
    _assert_sha256(sha256)
    root = Path(staging_root).resolve(strict=False)
    staging_dir = root / sha256
    _assert_under_root(root, staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    suffix = source.suffix.lower() or ".artifact"
    raw_artifact_path = staging_dir / f"raw_artifact{suffix}"
    shutil.copy2(source, raw_artifact_path)

    normalized_script_path: Path | None = None
    if artifact_kind == PATCHOPS_SCRIPT_KIND:
        normalized_script_path = staging_dir / "normalized_script.ps1"
        normalized_script_path.write_text(normalized_script_from_marked_payload_file(source), encoding="utf-8")
    elif artifact_kind == PATCHOPS_BUNDLE_KIND:
        normalized_script_path = None
    else:
        raise ValueError(f"artifact kind is not stageable in D0.8: {artifact_kind}")

    metadata_path = staging_dir / "metadata.json"
    metadata = build_staging_metadata(
        artifact_sha256=sha256,
        artifact_kind=artifact_kind,
        source_path=source,
        raw_artifact_path=raw_artifact_path,
        normalized_script_path=normalized_script_path,
        shape_payload=shape_payload or {},
    )
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return StagedArtifact(
        artifact_sha256=sha256,
        artifact_kind=artifact_kind,
        staging_dir=staging_dir,
        raw_artifact_path=raw_artifact_path,
        normalized_script_path=normalized_script_path,
        metadata_path=metadata_path,
    )


def run_staging_scan(
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
    shape_payload = run_shape_validation_scan(
        repo_root=root,
        config_path=config.config_path,
        evidence_root=evidence_root,
        create_dirs=create_dirs,
        write_evidence=False,
        sample_count=sample_count,
        interval_seconds=interval_seconds,
        max_candidates=max_candidates,
    )
    label = str(shape_payload["result_label"])
    staged: StagedArtifact | None = None
    artifact_sha256: str | None = None
    stage_issue: str | None = None

    if label in {"PASS_SCRIPT_VALIDATED_RUN_BLOCKED", PASS_BUNDLE_VALIDATED_RUN_BLOCKED}:
        shape_validation = shape_payload.get("shape_validation") or {}
        source_path = shape_validation.get("path")
        artifact_kind = shape_validation.get("artifact_kind")
        if not source_path or not Path(source_path).is_file():
            label = BLOCKED_STAGE_MISSING_SOURCE
            stage_issue = "validated artifact source file is missing"
        else:
            try:
                artifact_sha256 = compute_sha256(source_path)
                staged = stage_validated_artifact(
                    source_path=source_path,
                    artifact_kind=artifact_kind,
                    staging_root=config.staging_dir,
                    artifact_sha256=artifact_sha256,
                    shape_payload=shape_payload,
                )
                label = PASS_STAGED_ARTIFACT_READY
            except Exception as exc:
                label = FAIL_STAGE_WRITE
                stage_issue = str(exc)

    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else config.evidence_dir / "d0_08_staging"
    checks = {
        "browser_not_used": not safety.browser_used,
        "clipboard_not_used": not safety.clipboard_read and not safety.clipboard_written,
        "artifact_not_executed": not safety.artifact_executed,
        "patchops_not_invoked_by_downloader_runtime": not safety.patchops_invoked,
        "no_browser_or_clipboard_direct_execution": True,
        "zip_not_extracted": True,
        "staging_root_ready": config.staging_dir.exists(),
    }
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details={
            "checks": checks,
            "config": config.to_dict(),
            "shape_payload": shape_payload,
            "artifact_sha256": artifact_sha256,
            "staged_artifact": None if staged is None else staged.to_dict(),
            "stage_issue": stage_issue,
        },
    )
    evidence_files: dict[str, str] = {}
    if write_evidence:
        evidence_files = write_evidence_pair(evidence_dir, "quarantine_staging", evidence)
    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "artifact_sha256": artifact_sha256,
        "staged_artifact": None if staged is None else staged.to_dict(),
        "stage_issue": stage_issue,
        "checks": checks,
        "safety": safety.to_dict(),
        "shape_payload": shape_payload,
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.staging")
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
    payload = run_staging_scan(
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