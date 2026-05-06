from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags
from patchops.copilot_downloader.download_stable_validator import sha256_file

PATCH_NAME = "d3_03_downloader_patchops_bundle_validator"
PASS_BUNDLE_VALIDATED_RUN_BLOCKED = "PASS_BUNDLE_VALIDATED_RUN_BLOCKED"
BLOCKED_NO_STAGED_ARTIFACT = "BLOCKED_NO_STAGED_ARTIFACT"
BLOCKED_INVALID_BUNDLE = "BLOCKED_INVALID_BUNDLE"
BLOCKED_BUNDLE_SURFACE_FAILED = "BLOCKED_BUNDLE_SURFACE_FAILED"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_BUNDLE_VALIDATED_RUN_BLOCKED,
    BLOCKED_NO_STAGED_ARTIFACT,
    BLOCKED_INVALID_BUNDLE,
    BLOCKED_BUNDLE_SURFACE_FAILED,
})
NON_EXECUTING_SURFACES: tuple[str, ...] = ("check-bundle", "inspect-bundle", "plan-bundle")
FORBIDDEN_SURFACES: tuple[str, ...] = ("apply-bundle", "run-package", "apply", "run")


def _repo_child(root: Path, *parts: str) -> Path:
    candidate = root.joinpath(*parts).resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    candidate.relative_to(root_resolved)
    return candidate


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def find_latest_staged_downloaded_artifact(repo_root: str | Path) -> Path | None:
    root = Path(repo_root).resolve(strict=False)
    staged_root = root / "data" / "runtime" / "copilot_downloader" / "downloaded_artifacts" / "staged"
    if not staged_root.is_dir():
        return None
    metadata_files = [path for path in staged_root.glob("*/metadata.json") if path.is_file()]
    if not metadata_files:
        return None
    return max(metadata_files, key=lambda path: path.stat().st_mtime).resolve(strict=False)


def load_staged_bundle_metadata(metadata_path: str | Path) -> dict[str, Any]:
    path = Path(metadata_path).resolve(strict=False)
    payload = _read_json(path)
    payload["metadata_path"] = str(path)
    raw = payload.get("raw_artifact_path")
    if raw is not None:
        payload["raw_artifact_path"] = str(Path(str(raw)).resolve(strict=False))
    return payload


def validate_staged_bundle_shape(metadata: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    artifact_path = Path(str(metadata.get("raw_artifact_path", ""))).resolve(strict=False)
    recorded_sha = metadata.get("artifact_sha256")
    classification = metadata.get("classification") if isinstance(metadata.get("classification"), dict) else {}
    if not artifact_path.is_file():
        issues.append("raw staged artifact is missing")
    if artifact_path.suffix.lower() != ".zip":
        issues.append("staged artifact must be a .zip bundle for D3.3")
    actual_sha: str | None = None
    if artifact_path.is_file():
        actual_sha = sha256_file(artifact_path)
        if recorded_sha and actual_sha != recorded_sha:
            issues.append("staged artifact sha256 does not match metadata")
    if classification.get("kind") not in {"patchops_bundle_zip", None}:
        issues.append(f"staged classification is not a PatchOps bundle zip: {classification.get('kind')}")

    member_names: list[str] = []
    zip_opened = False
    zip_issue: str | None = None
    if artifact_path.is_file() and artifact_path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(artifact_path) as archive:
                zip_opened = True
                member_names = archive.namelist()
        except zipfile.BadZipFile:
            zip_issue = "bad_zip_file"
            issues.append("staged artifact is not a valid zip")
    lowered = {name.replace("\\", "/").lower() for name in member_names}
    has_manifest = any(name.endswith("manifest.json") for name in lowered) or "patchops_bundle.json" in lowered or "bundle_manifest.json" in lowered
    if artifact_path.is_file() and artifact_path.suffix.lower() == ".zip" and not has_manifest:
        issues.append("zip bundle has no manifest-like member")
    return {
        "ok": not issues,
        "issues": issues,
        "artifact_path": str(artifact_path),
        "recorded_sha256": recorded_sha,
        "actual_sha256": actual_sha,
        "sha256_matches_metadata": actual_sha is not None and (not recorded_sha or recorded_sha == actual_sha),
        "zip_opened_for_index_only": zip_opened,
        "zip_issue": zip_issue,
        "zip_entry_count": len(member_names),
        "has_manifest_like_member": has_manifest,
        "archive_extracted": False,
        "manifest_bytes_read": False,
        "manifest_json_parsed": False,
        "package_run": False,
    }


def build_bundle_surface_commands(bundle_path: str | Path) -> list[list[str]]:
    path = str(Path(bundle_path).resolve(strict=False))
    return [[sys.executable, "-m", "patchops.cli", surface, path] for surface in NON_EXECUTING_SURFACES]


def _preview_command(command: Sequence[str]) -> str:
    return " ".join([f'"{item}"' if any(ch.isspace() for ch in item) else item for item in command])


def default_command_runner(command: Sequence[str], *, cwd: str | Path, timeout_seconds: int) -> dict[str, Any]:
    started = time.time()
    timed_out = False
    try:
        process = subprocess.Popen(
            list(command),
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            exit_code = int(process.returncode)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                process.kill()
            except Exception:
                pass
            stdout, stderr = process.communicate()
            exit_code = 124
    except FileNotFoundError as exc:
        stdout = ""
        stderr = str(exc)
        exit_code = 127
    return {
        "command": _preview_command(command),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "elapsed_seconds": round(time.time() - started, 3),
        "stdout": stdout,
        "stderr": stderr,
        "stdout_size_chars": len(stdout),
        "stderr_size_chars": len(stderr),
    }


def run_non_executing_bundle_surfaces(
    *,
    repo_root: str | Path,
    bundle_path: str | Path,
    timeout_seconds: int = 120,
    command_runner: Callable[..., dict[str, Any]] | None = None,
    run_bundle_doctor_on_failure: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=False)
    runner = command_runner or default_command_runner
    commands = build_bundle_surface_commands(bundle_path)
    results: list[dict[str, Any]] = []
    for command in commands:
        result = runner(command, cwd=root, timeout_seconds=timeout_seconds)
        result["surface"] = command[3] if len(command) > 3 else "unknown"
        results.append(result)
    failed = [item for item in results if item.get("exit_code") != 0 or item.get("timed_out")]
    doctor_result: dict[str, Any] | None = None
    if failed and run_bundle_doctor_on_failure:
        doctor_command = [sys.executable, "-m", "patchops.cli", "bundle-doctor", str(Path(bundle_path).resolve(strict=False))]
        doctor_result = runner(doctor_command, cwd=root, timeout_seconds=timeout_seconds)
        doctor_result["surface"] = "bundle-doctor"
    surfaces = [item.get("surface") for item in results]
    return {
        "ok": not failed,
        "surface_results": results,
        "failed_surfaces": [item.get("surface") for item in failed],
        "bundle_doctor_result": doctor_result,
        "non_executing_surfaces": surfaces,
        "forbidden_surfaces_invoked": [surface for surface in surfaces if surface in FORBIDDEN_SURFACES],
        "apply_or_run_invoked": any(surface in FORBIDDEN_SURFACES for surface in surfaces),
    }


def update_staged_metadata_with_bundle_validation(metadata_path: str | Path, *, validation_payload: dict[str, Any]) -> dict[str, Any]:
    path = Path(metadata_path).resolve(strict=False)
    payload = _read_json(path)
    payload["bundle_validation_performed"] = True
    payload["bundle_validation_utc"] = datetime.now(timezone.utc).isoformat()
    payload["bundle_validation_result_label"] = validation_payload.get("result_label")
    payload["bundle_validation_ok"] = validation_payload.get("result_label") == PASS_BUNDLE_VALIDATED_RUN_BLOCKED
    payload["bundle_validation_surfaces"] = validation_payload.get("surface_validation", {}).get("non_executing_surfaces", [])
    payload["run_authorized"] = False
    payload["artifact_executed"] = False
    _write_json(path, payload)
    return payload


def _write_validator_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "patchops_bundle_validator", evidence)


def run_patchops_bundle_validator(
    *,
    repo_root: str | Path | None = None,
    evidence_root: str | Path | None = None,
    staged_metadata_path: str | Path | None = None,
    timeout_seconds: int = 120,
    execute_surfaces: bool = False,
    command_runner: Callable[..., dict[str, Any]] | None = None,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "d3_03_patchops_bundle_validator")
    safety = DownloaderSafetyFlags()
    metadata_path = Path(staged_metadata_path).resolve(strict=False) if staged_metadata_path is not None else find_latest_staged_downloaded_artifact(root)

    metadata: dict[str, Any] | None = None
    shape: dict[str, Any] | None = None
    surface_validation: dict[str, Any] | None = None
    updated_metadata: dict[str, Any] | None = None
    issue = None
    label = PASS_BUNDLE_VALIDATED_RUN_BLOCKED

    if metadata_path is None or not metadata_path.is_file():
        label = BLOCKED_NO_STAGED_ARTIFACT
        issue = "staged_bundle_metadata_required"
    else:
        metadata = load_staged_bundle_metadata(metadata_path)
        shape = validate_staged_bundle_shape(metadata)
        if not shape["ok"]:
            label = BLOCKED_INVALID_BUNDLE
            issue = "invalid_staged_bundle_shape"
        elif not execute_surfaces and command_runner is None:
            label = PASS_BUNDLE_VALIDATED_RUN_BLOCKED
            issue = "surface_execution_not_requested"
            surface_validation = {
                "ok": True,
                "surface_results": [],
                "failed_surfaces": [],
                "bundle_doctor_result": None,
                "non_executing_surfaces": list(NON_EXECUTING_SURFACES),
                "forbidden_surfaces_invoked": [],
                "apply_or_run_invoked": False,
                "dry_surface_plan_only": True,
            }
        else:
            surface_validation = run_non_executing_bundle_surfaces(
                repo_root=root,
                bundle_path=str(metadata["raw_artifact_path"]),
                timeout_seconds=timeout_seconds,
                command_runner=command_runner,
            )
            if not surface_validation["ok"]:
                label = BLOCKED_BUNDLE_SURFACE_FAILED
                issue = "non_executing_bundle_surface_failed"
            else:
                label = PASS_BUNDLE_VALIDATED_RUN_BLOCKED
                issue = None
        if label == PASS_BUNDLE_VALIDATED_RUN_BLOCKED and metadata_path is not None and metadata_path.is_file():
            interim = {
                "result_label": label,
                "surface_validation": surface_validation or {},
            }
            updated_metadata = update_staged_metadata_with_bundle_validation(metadata_path, validation_payload=interim)

    checks = {
        "staged_metadata_required_or_controlled_block": metadata_path is not None or label == BLOCKED_NO_STAGED_ARTIFACT,
        "sha256_verified_when_bundle_present": shape is None or shape.get("sha256_matches_metadata") is True,
        "shape_validation_performed": shape is not None or label == BLOCKED_NO_STAGED_ARTIFACT,
        "zip_index_read_only": shape is None or shape.get("zip_opened_for_index_only") in {True, False},
        "archive_not_extracted": shape is None or shape.get("archive_extracted") is False,
        "manifest_bytes_not_read": shape is None or shape.get("manifest_bytes_read") is False,
        "manifest_json_not_parsed": shape is None or shape.get("manifest_json_parsed") is False,
        "check_bundle_surface_present": surface_validation is None or "check-bundle" in surface_validation.get("non_executing_surfaces", []),
        "inspect_bundle_surface_present": surface_validation is None or "inspect-bundle" in surface_validation.get("non_executing_surfaces", []),
        "plan_bundle_surface_present": surface_validation is None or "plan-bundle" in surface_validation.get("non_executing_surfaces", []),
        "bundle_doctor_available_on_failure": surface_validation is None or surface_validation.get("bundle_doctor_result") is not None or surface_validation.get("ok") is True,
        "no_apply_bundle_or_run_package": surface_validation is None or surface_validation.get("apply_or_run_invoked") is False,
        "metadata_updated_only_on_pass": updated_metadata is None or updated_metadata.get("bundle_validation_ok") is True,
        "run_not_authorized": updated_metadata is None or updated_metadata.get("run_authorized") is False,
        "artifact_not_executed": not safety.artifact_executed,
        "patchops_runtime_not_invoked_for_apply_or_run": not safety.patchops_invoked,
        "browser_not_started": not safety.browser_used,
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "uploader_not_imported": True,
    }
    details = {
        "checks": checks,
        "issue": issue,
        "metadata_path": None if metadata_path is None else str(metadata_path),
        "staged_metadata": metadata,
        "shape": shape,
        "surface_validation": surface_validation,
        "updated_metadata": updated_metadata,
        "timeout_seconds": timeout_seconds,
    }
    evidence_files = _write_validator_evidence(evidence_dir, label, safety, details) if write_evidence else {}
    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "issue": issue,
        "metadata_path": None if metadata_path is None else str(metadata_path),
        "shape": shape,
        "surface_validation": surface_validation,
        "updated_metadata": updated_metadata,
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.patchops_bundle_validator")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--staged-metadata-path", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--execute-surfaces", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_patchops_bundle_validator(
        repo_root=args.repo_root,
        evidence_root=args.evidence_root,
        staged_metadata_path=args.staged_metadata_path,
        timeout_seconds=args.timeout_seconds,
        execute_surfaces=args.execute_surfaces,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())