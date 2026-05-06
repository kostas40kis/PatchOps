from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.config import load_downloader_config
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import (
    ARTIFACT_KINDS,
    PASS_ARTIFACT_CLASSIFIED,
    ArtifactClassification,
    DownloaderEvidenceRecord,
)
from patchops.copilot_downloader.safety_policy import default_safety_flags
from patchops.copilot_downloader.stable_detector import STABLE_PASS_LABEL, run_stable_artifact_scan

PATCH_NAME = "d0_06_downloader_artifact_classifier"
SCRIPT_PAYLOAD_BEGIN = "PATCHOPS_SCRIPT_PAYLOAD_BEGIN"
SCRIPT_PAYLOAD_END = "PATCHOPS_SCRIPT_PAYLOAD_END"
PATCHOPS_SCRIPT_KIND = "patchops_script_payload"
PATCHOPS_MANIFEST_KIND = "patchops_manifest_json"
PATCHOPS_BUNDLE_KIND = "patchops_bundle_zip"
UNKNOWN_ZIP_KIND = "unknown_zip"
UNSUPPORTED_KIND = "unsupported_file"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_ARTIFACT_CLASSIFIED,
    "BLOCKED_NO_ARTIFACT",
    "BLOCKED_UNSTABLE_FILE",
    "BLOCKED_INVALID_ARTIFACT",
    "BLOCKED_AMBIGUOUS_ARTIFACTS",
})


def _safe_read_text(path: Path, *, max_bytes: int = 1024 * 1024) -> str:
    data = path.read_bytes()[:max_bytes]
    return data.decode("utf-8", errors="replace")


def classify_script_like_file(path: Path) -> ArtifactClassification:
    text = _safe_read_text(path)
    reasons: list[str] = []
    has_begin = SCRIPT_PAYLOAD_BEGIN in text
    has_end = SCRIPT_PAYLOAD_END in text
    has_invocation = "& {" in text
    has_strict = "Set-StrictMode" in text
    if has_begin and has_end and has_invocation and has_strict:
        return ArtifactClassification(
            artifact_kind=PATCHOPS_SCRIPT_KIND,
            result_label=PASS_ARTIFACT_CLASSIFIED,
            path=path,
            reasons=("marked_patchops_script_payload",),
            metadata={
                "contains_payload_begin_marker": has_begin,
                "contains_payload_end_marker": has_end,
                "contains_powershell_invocation_block": has_invocation,
                "contains_strict_mode": has_strict,
            },
        )
    if not has_begin:
        reasons.append("missing_payload_begin_marker")
    if not has_end:
        reasons.append("missing_payload_end_marker")
    if not has_invocation:
        reasons.append("missing_powershell_invocation_block")
    if not has_strict:
        reasons.append("missing_strict_mode")
    return ArtifactClassification(
        artifact_kind=UNSUPPORTED_KIND,
        result_label="BLOCKED_INVALID_ARTIFACT",
        path=path,
        reasons=tuple(reasons),
        metadata={"text_probe_bytes_limit": 1024 * 1024},
    )


def classify_json_file(path: Path) -> ArtifactClassification:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return ArtifactClassification(
            artifact_kind=UNSUPPORTED_KIND,
            result_label="BLOCKED_INVALID_ARTIFACT",
            path=path,
            reasons=(f"json_parse_failed:{exc}",),
        )
    if not isinstance(payload, dict):
        return ArtifactClassification(
            artifact_kind=UNSUPPORTED_KIND,
            result_label="BLOCKED_INVALID_ARTIFACT",
            path=path,
            reasons=("json_root_not_object",),
        )
    manifest_markers = {
        "manifest_version": payload.get("manifest_version"),
        "patch_name": payload.get("patch_name"),
        "files_to_write_is_list": isinstance(payload.get("files_to_write"), list),
        "target_project_root_present": "target_project_root" in payload,
    }
    if manifest_markers["manifest_version"] and manifest_markers["patch_name"] and manifest_markers["files_to_write_is_list"]:
        return ArtifactClassification(
            artifact_kind=PATCHOPS_MANIFEST_KIND,
            result_label=PASS_ARTIFACT_CLASSIFIED,
            path=path,
            reasons=("patchops_manifest_shape",),
            metadata={"manifest_markers": manifest_markers, "patch_name": payload.get("patch_name")},
        )
    return ArtifactClassification(
        artifact_kind=UNSUPPORTED_KIND,
        result_label="BLOCKED_INVALID_ARTIFACT",
        path=path,
        reasons=("json_not_patchops_manifest_shape",),
        metadata={"manifest_markers": manifest_markers},
    )


def _zip_names(path: Path) -> tuple[str, ...]:
    with zipfile.ZipFile(path) as archive:
        return tuple(sorted(info.filename.replace("\\", "/") for info in archive.infolist()))


def classify_zip_file(path: Path) -> ArtifactClassification:
    try:
        names = _zip_names(path)
    except Exception as exc:
        return ArtifactClassification(
            artifact_kind=UNSUPPORTED_KIND,
            result_label="BLOCKED_INVALID_ARTIFACT",
            path=path,
            reasons=(f"zip_open_failed:{exc}",),
        )
    lower_names = tuple(name.lower() for name in names)
    has_manifest = any(name.endswith("manifest.json") for name in lower_names)
    has_bundle_metadata = any(name.endswith("bundle_metadata.json") or name.endswith("patchops_bundle.json") for name in lower_names)
    has_patchops_dir = any("patchops" in name for name in lower_names)
    if has_manifest or has_bundle_metadata or has_patchops_dir:
        return ArtifactClassification(
            artifact_kind=PATCHOPS_BUNDLE_KIND,
            result_label=PASS_ARTIFACT_CLASSIFIED,
            path=path,
            reasons=("zip_index_contains_patchops_markers",),
            metadata={
                "zip_entry_count": len(names),
                "has_manifest": has_manifest,
                "has_bundle_metadata": has_bundle_metadata,
                "has_patchops_dir_marker": has_patchops_dir,
                "zip_entries_preview": list(names[:25]),
            },
        )
    return ArtifactClassification(
        artifact_kind=UNKNOWN_ZIP_KIND,
        result_label=PASS_ARTIFACT_CLASSIFIED,
        path=path,
        reasons=("zip_opened_without_patchops_markers",),
        metadata={"zip_entry_count": len(names), "zip_entries_preview": list(names[:25])},
    )


def classify_artifact_file(path: str | Path) -> ArtifactClassification:
    artifact_path = Path(path).resolve(strict=False)
    extension = artifact_path.suffix.lower()
    if extension in {".ps1", ".txt", ".md"}:
        return classify_script_like_file(artifact_path)
    if extension == ".json":
        return classify_json_file(artifact_path)
    if extension == ".zip":
        return classify_zip_file(artifact_path)
    return ArtifactClassification(
        artifact_kind=UNSUPPORTED_KIND,
        result_label="BLOCKED_INVALID_ARTIFACT",
        path=artifact_path,
        reasons=(f"unsupported_extension:{extension}",),
    )


def run_classifier_scan(
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
    stable_payload = run_stable_artifact_scan(
        repo_root=root,
        config_path=config.config_path,
        evidence_root=evidence_root,
        create_dirs=create_dirs,
        write_evidence=False,
        sample_count=sample_count,
        interval_seconds=interval_seconds,
        max_candidates=max_candidates,
    )
    label = str(stable_payload["result_label"])
    classification: ArtifactClassification | None = None
    if label == STABLE_PASS_LABEL:
        candidate = stable_payload["stable_validation"]["candidate"]
        classification = classify_artifact_file(candidate["path"])
        label = classification.result_label

    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else config.evidence_dir / "d0_06_classifier"
    checks = {
        "browser_not_used": not safety.browser_used,
        "clipboard_not_used": not safety.clipboard_read and not safety.clipboard_written,
        "artifact_not_executed": not safety.artifact_executed,
        "staging_not_performed": True,
        "hash_not_computed_by_classifier": True,
        "zip_index_only_no_extract": True,
        "artifact_kinds_declared": set(ARTIFACT_KINDS) == {PATCHOPS_SCRIPT_KIND, PATCHOPS_MANIFEST_KIND, PATCHOPS_BUNDLE_KIND, UNKNOWN_ZIP_KIND, UNSUPPORTED_KIND},
    }
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details={
            "checks": checks,
            "config": config.to_dict(),
            "stable_payload": stable_payload,
            "classification": None if classification is None else classification.to_dict(),
            "artifact_kinds": list(ARTIFACT_KINDS),
        },
    )
    evidence_files: dict[str, str] = {}
    if write_evidence:
        evidence_files = write_evidence_pair(evidence_dir, "artifact_classification", evidence)
    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "classification": None if classification is None else classification.to_dict(),
        "artifact_kind": None if classification is None else classification.artifact_kind,
        "checks": checks,
        "safety": safety.to_dict(),
        "stable_payload": stable_payload,
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.classifier")
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
    payload = run_classifier_scan(
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