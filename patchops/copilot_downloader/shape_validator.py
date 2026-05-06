from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.bundle_validator import validate_patchops_bundle_zip
from patchops.copilot_downloader.classifier import (
    PATCHOPS_BUNDLE_KIND,
    PATCHOPS_SCRIPT_KIND,
    UNKNOWN_ZIP_KIND,
    PASS_ARTIFACT_CLASSIFIED,
    run_classifier_scan,
)
from patchops.copilot_downloader.config import load_downloader_config
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord
from patchops.copilot_downloader.safety_policy import default_safety_flags
from patchops.copilot_downloader.script_validator import validate_patchops_script_payload_file

PATCH_NAME = "d0_07_downloader_shape_validators"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    "PASS_SCRIPT_VALIDATED_RUN_BLOCKED",
    "PASS_BUNDLE_VALIDATED_RUN_BLOCKED",
    "BLOCKED_NO_ARTIFACT",
    "BLOCKED_UNSTABLE_FILE",
    "BLOCKED_INVALID_ARTIFACT",
    "BLOCKED_AMBIGUOUS_ARTIFACTS",
})


def run_shape_validation_scan(
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
    classifier_payload = run_classifier_scan(
        repo_root=root,
        config_path=config.config_path,
        evidence_root=evidence_root,
        create_dirs=create_dirs,
        write_evidence=False,
        sample_count=sample_count,
        interval_seconds=interval_seconds,
        max_candidates=max_candidates,
    )
    label = str(classifier_payload["result_label"])
    validation = None
    if label == PASS_ARTIFACT_CLASSIFIED:
        classification = classifier_payload.get("classification") or {}
        artifact_kind = classification.get("artifact_kind")
        path = classification.get("path")
        if artifact_kind == PATCHOPS_SCRIPT_KIND:
            validation = validate_patchops_script_payload_file(path)
            label = validation.result_label
        elif artifact_kind in {PATCHOPS_BUNDLE_KIND, UNKNOWN_ZIP_KIND}:
            validation = validate_patchops_bundle_zip(path)
            label = validation.result_label
        else:
            label = "BLOCKED_INVALID_ARTIFACT"
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else config.evidence_dir / "d0_07_shape_validation"
    checks = {
        "browser_not_used": not safety.browser_used,
        "clipboard_not_used": not safety.clipboard_read and not safety.clipboard_written,
        "artifact_not_executed": not safety.artifact_executed,
        "staging_not_performed": True,
        "patchops_not_invoked_by_downloader_runtime": not safety.patchops_invoked,
        "zip_index_only_no_extract": True,
    }
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details={
            "checks": checks,
            "config": config.to_dict(),
            "classifier_payload": classifier_payload,
            "shape_validation": None if validation is None else validation.to_dict(),
        },
    )
    evidence_files: dict[str, str] = {}
    if write_evidence:
        evidence_files = write_evidence_pair(evidence_dir, "shape_validation", evidence)
    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "shape_validation": None if validation is None else validation.to_dict(),
        "checks": checks,
        "safety": safety.to_dict(),
        "classifier_payload": classifier_payload,
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.shape_validator")
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
    payload = run_shape_validation_scan(
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