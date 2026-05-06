from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import (
    FOUNDATION_RESULT_LABEL,
    RESULT_LABELS,
    DownloaderDoctorResult,
    DownloaderEvidenceRecord,
)
from patchops.copilot_downloader.safety_policy import default_safety_flags, validate_foundation_boundary

PATCH_NAME = "d0_01_copilot_downloader_foundation"


def _foundation_file_checks(repo_root: Path) -> dict[str, bool]:
    expected_files = [
        "patchops/copilot_downloader/__init__.py",
        "patchops/copilot_downloader/models.py",
        "patchops/copilot_downloader/safety_policy.py",
        "patchops/copilot_downloader/evidence.py",
        "patchops/copilot_downloader/commands.py",
        "docs/copilot_downloader_direction.md",
        "tests/test_copilot_downloader_foundation_current.py",
    ]
    return {f"exists:{relative}": (repo_root / relative).is_file() for relative in expected_files}


def run_foundation_doctor(
    repo_root: str | Path | None = None,
    evidence_root: str | Path | None = None,
    *,
    write_evidence: bool = True,
) -> dict[str, object]:
    root = Path(repo_root or Path.cwd()).resolve()
    runtime_root = root / "data" / "runtime" / "copilot_downloader" / PATCH_NAME
    evidence_dir = Path(evidence_root).resolve() if evidence_root is not None else runtime_root
    safety = default_safety_flags()
    boundary_issues = validate_foundation_boundary(safety)

    checks: dict[str, bool] = {
        "result_labels_declared": FOUNDATION_RESULT_LABEL in RESULT_LABELS,
        "stable_ladder_labels_declared": all(
            label in RESULT_LABELS
            for label in (
                "PASS_ARTIFACT_DETECTED",
                "PASS_STABLE_ARTIFACT_VALIDATED",
                "BLOCKED_RUN_NOT_AUTHORIZED",
                "FAIL_REPORT_MISSING",
            )
        ),
        "safety_boundary_clean": not boundary_issues,
        "uploader_module_not_imported": "patchops.chatgpt_uploader" not in sys.modules,
        "browser_runtime_not_used": not safety.browser_used,
        "clipboard_not_used": not safety.clipboard_read and not safety.clipboard_written,
        "artifact_not_executed": not safety.artifact_executed,
    }
    checks.update(_foundation_file_checks(root))
    ok = all(checks.values())

    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=FOUNDATION_RESULT_LABEL if ok else "FAIL_PATCHOPS_RUN",
        safety=safety,
        details={
            "repo_root": str(root),
            "boundary_issues": boundary_issues,
            "checks": checks,
        },
    )
    evidence_files: dict[str, str] = {}
    if write_evidence:
        evidence_files = write_evidence_pair(evidence_dir, "foundation_doctor", evidence)

    result = DownloaderDoctorResult(
        ok=ok,
        result_label=evidence.result_label,
        checks=checks,
        safety=safety,
        evidence_files=evidence_files,
    )
    return result.to_dict()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.commands")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_foundation_doctor(
        repo_root=args.repo_root,
        evidence_root=args.evidence_root,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())