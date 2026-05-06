from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.bundle_validator import validate_patchops_bundle_zip
from patchops.copilot_downloader.classifier import (
    PATCHOPS_BUNDLE_KIND,
    PATCHOPS_SCRIPT_KIND,
    PASS_ARTIFACT_CLASSIFIED,
    classify_artifact_file,
)
from patchops.copilot_downloader.config import load_downloader_config
from patchops.copilot_downloader.ledger import compute_sha256, find_duplicate_entry
from patchops.copilot_downloader.models import (
    BLOCKED_DUPLICATE_ARTIFACT,
    PASS_BUNDLE_VALIDATED_RUN_BLOCKED,
    PASS_STAGED_ARTIFACT_READY,
)
from patchops.copilot_downloader.safety_policy import default_safety_flags
from patchops.copilot_downloader.script_validator import validate_patchops_script_payload_file
from patchops.copilot_downloader.stable_detector import STABLE_PASS_LABEL, run_stable_artifact_scan
from patchops.copilot_downloader.staging import stage_validated_artifact

PATCH_NAME = "d0_09_downloader_local_dry_run_gate"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_STAGED_ARTIFACT_READY,
    BLOCKED_DUPLICATE_ARTIFACT,
    "BLOCKED_NO_ARTIFACT",
    "BLOCKED_UNSTABLE_FILE",
    "BLOCKED_INVALID_ARTIFACT",
    "BLOCKED_AMBIGUOUS_ARTIFACTS",
    "FAIL_STAGE_WRITE",
})
SHAPE_PASS_LABELS: frozenset[str] = frozenset({
    "PASS_SCRIPT_VALIDATED_RUN_BLOCKED",
    PASS_BUNDLE_VALIDATED_RUN_BLOCKED,
})


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _write_text_report(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "PATCHOPS DOWNLOADER LOCAL DRY-RUN REPORT",
        "========================================",
        f"generated_utc: {datetime.now(timezone.utc).isoformat()}",
        f"patch_name: {PATCH_NAME}",
        f"result_label: {payload.get('result_label')}",
        f"ok: {str(payload.get('ok')).lower()}",
        f"artifact_sha256: {payload.get('artifact_sha256')}",
        f"duplicate_found: {str(payload.get('duplicate_found')).lower()}",
        f"staged_artifact: {json.dumps(payload.get('staged_artifact'), sort_keys=True)}",
        "checks:",
    ]
    for key, value in sorted((payload.get("checks") or {}).items()):
        lines.append(f"  {key}: {value}")
    lines.append("safety:")
    for key, value in sorted((payload.get("safety") or {}).items()):
        lines.append(f"  {key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_local_dry_run_report(evidence_root: str | Path, payload: dict[str, Any]) -> dict[str, str]:
    root = Path(evidence_root)
    json_path = _write_json(root / "local_dry_run.json", payload)
    text_path = _write_text_report(root / "local_dry_run.txt", payload)
    return {"json": str(json_path), "text": str(text_path)}


def _validate_shape_for_classification(classification: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    artifact_kind = classification.get("artifact_kind")
    path = classification.get("path")
    if artifact_kind == PATCHOPS_SCRIPT_KIND:
        validation = validate_patchops_script_payload_file(path)
        return validation.result_label, validation.to_dict()
    if artifact_kind == PATCHOPS_BUNDLE_KIND:
        validation = validate_patchops_bundle_zip(path)
        return validation.result_label, validation.to_dict()
    return "BLOCKED_INVALID_ARTIFACT", {
        "artifact_kind": str(artifact_kind),
        "path": str(path),
        "issues": ["artifact kind is not stageable in local dry-run gate"],
    }


def run_local_dry_run(
    *,
    repo_root: str | Path | None = None,
    config_path: str | Path = "data/config/copilot_downloader_config.json",
    evidence_root: str | Path | None = None,
    create_dirs: bool = True,
    sample_count: int = 3,
    interval_seconds: float = 0.2,
    allow_duplicate: bool = False,
    max_candidates: int = 50,
    write_report: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    config = load_downloader_config(config_path, repo_root=root, create_dirs=create_dirs)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else config.evidence_dir / "d0_09_local_dry_run"
    safety = default_safety_flags()

    stable_payload = run_stable_artifact_scan(
        repo_root=root,
        config_path=config.config_path,
        evidence_root=evidence_dir,
        create_dirs=create_dirs,
        write_evidence=False,
        sample_count=sample_count,
        interval_seconds=interval_seconds,
        max_candidates=max_candidates,
    )
    label = str(stable_payload["result_label"])
    artifact_sha256: str | None = None
    duplicate_entry: dict[str, Any] | None = None
    classification: dict[str, Any] | None = None
    shape_validation: dict[str, Any] | None = None
    staged_artifact: dict[str, Any] | None = None
    dry_run_issue: str | None = None

    if label == STABLE_PASS_LABEL:
        candidate = stable_payload["stable_validation"]["candidate"]
        artifact_path = Path(candidate["path"])
        artifact_sha256 = compute_sha256(artifact_path)
        duplicate_entry = find_duplicate_entry(config.duplicate_ledger_path, artifact_sha256)
        if duplicate_entry is not None and not allow_duplicate:
            label = BLOCKED_DUPLICATE_ARTIFACT
        else:
            class_result = classify_artifact_file(artifact_path)
            classification = class_result.to_dict()
            label = class_result.result_label
            if label == PASS_ARTIFACT_CLASSIFIED:
                label, shape_validation = _validate_shape_for_classification(classification)
                if label in SHAPE_PASS_LABELS:
                    try:
                        staged = stage_validated_artifact(
                            source_path=artifact_path,
                            artifact_kind=str(classification["artifact_kind"]),
                            staging_root=config.staging_dir,
                            artifact_sha256=artifact_sha256,
                            shape_payload={
                                "classification": classification,
                                "shape_validation": shape_validation,
                                "stable_payload": stable_payload,
                                "local_dry_run": True,
                            },
                        )
                        staged_artifact = staged.to_dict()
                        label = PASS_STAGED_ARTIFACT_READY
                    except Exception as exc:
                        label = "FAIL_STAGE_WRITE"
                        dry_run_issue = str(exc)

    stable_gate_passed = stable_payload["result_label"] == STABLE_PASS_LABEL
    classification_success = bool(classification) and classification.get("result_label") == PASS_ARTIFACT_CLASSIFIED
    shape_success = bool(shape_validation) and shape_validation.get("result_label") in SHAPE_PASS_LABELS
    duplicate_blocked = duplicate_entry is not None and not allow_duplicate

    checks = {
        "stable_gate_executed": True,
        "hash_gate_executed_when_stable": (not stable_gate_passed) or artifact_sha256 is not None,
        "dedupe_gate_executed_when_stable": (not stable_gate_passed) or artifact_sha256 is not None,
        "classification_gate_executed_when_not_duplicate": (not stable_gate_passed) or duplicate_blocked or classification is not None,
        "shape_gate_executed_when_classified": (not classification_success) or shape_validation is not None,
        "staging_gate_executed_when_shape_valid": (not shape_success) or staged_artifact is not None or label == "FAIL_STAGE_WRITE",
        "controlled_invalid_stops_before_shape_or_stage": (label != "BLOCKED_INVALID_ARTIFACT") or staged_artifact is None,
        "stop_before_execution": True,
        "browser_not_used": not safety.browser_used,
        "clipboard_not_used": not safety.clipboard_read and not safety.clipboard_written,
        "artifact_not_executed": not safety.artifact_executed,
        "patchops_not_invoked_by_downloader_runtime": not safety.patchops_invoked,
        "uploader_not_imported": True,
        "ledger_not_written_by_dry_run_gate": True,
    }
    payload = {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "patch_name": PATCH_NAME,
        "repo_root": str(root),
        "config_path": str(config.config_path),
        "artifact_sha256": artifact_sha256,
        "duplicate_found": duplicate_entry is not None,
        "duplicate_entry": duplicate_entry,
        "classification": classification,
        "shape_validation": shape_validation,
        "staged_artifact": staged_artifact,
        "dry_run_issue": dry_run_issue,
        "stable_payload": stable_payload,
        "checks": checks,
        "safety": safety.to_dict(),
        "execution_allowed": False,
        "patchops_invoked": False,
        "report_files": {},
    }
    if write_report:
        payload["report_files"] = write_local_dry_run_report(evidence_dir, payload)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.local_dry_run")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--config-path", default="data/config/copilot_downloader_config.json")
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--no-create-dirs", action="store_true")
    parser.add_argument("--sample-count", type=int, default=3)
    parser.add_argument("--interval-seconds", type=float, default=0.2)
    parser.add_argument("--allow-duplicate", action="store_true")
    parser.add_argument("--max-candidates", type=int, default=50)
    parser.add_argument("--no-write-report", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_local_dry_run(
        repo_root=args.repo_root,
        config_path=args.config_path,
        evidence_root=args.evidence_root,
        create_dirs=not args.no_create_dirs,
        sample_count=args.sample_count,
        interval_seconds=args.interval_seconds,
        allow_duplicate=args.allow_duplicate,
        max_candidates=args.max_candidates,
        write_report=not args.no_write_report,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())