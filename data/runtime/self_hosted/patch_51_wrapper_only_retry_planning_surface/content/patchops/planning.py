from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from patchops.manifest_loader import load_manifest
from patchops.profiles.base import resolve_profile
from patchops.workflows.common import default_report_directory, infer_workspace_root
from patchops.workflows.wrapper_retry import (
    build_wrapper_only_retry_state,
    wrapper_only_retry_state_as_dict,
)

SUPPORTED_PLAN_MODES = ("apply", "verify", "wrapper_retry")
WRAPPER_RETRY_PLAN_MODE = "wrapper_retry"


def _render_path(value: Path | None) -> str | None:
    if value is None:
        return None
    return str(value)


def _safe_patch_name(patch_name: str) -> str:
    return patch_name.lower().replace(" ", "_")


def _effective_backup_files(manifest) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for path in list(manifest.backup_files) + [item.path for item in manifest.files_to_write]:
        if path not in seen:
            seen.add(path)
            ordered.append(path)
    return ordered


def plan_manifest(
    manifest_path: str | Path,
    wrapper_project_root: str | Path | None = None,
    mode: str = "apply",
    retry_reason: str | None = None,
) -> dict:
    if mode not in SUPPORTED_PLAN_MODES:
        raise ValueError(
            f"Unsupported plan mode: {mode!r}. Expected one of {SUPPORTED_PLAN_MODES!r}."
        )

    manifest_path = Path(manifest_path).resolve()
    wrapper_root = (
        Path(wrapper_project_root).resolve()
        if wrapper_project_root
        else Path(__file__).resolve().parents[1]
    )
    manifest = load_manifest(manifest_path)
    resolved_profile = resolve_profile(manifest, wrapper_root)
    target_root = (
        Path(manifest.target_project_root)
        if manifest.target_project_root
        else resolved_profile.default_target_root
    )
    if target_root is None:
        raise ValueError("No target project root could be resolved from the manifest/profile.")

    workspace_root = infer_workspace_root(target_root)
    report_dir = (
        Path(manifest.report_preferences.report_dir)
        if manifest.report_preferences.report_dir
        else default_report_directory()
    )

    report_prefix = manifest.report_preferences.report_name_prefix or resolved_profile.report_prefix
    if mode == "verify":
        report_prefix = (
            manifest.report_preferences.report_name_prefix
            or f"{resolved_profile.report_prefix}_verify"
        )
    elif mode == WRAPPER_RETRY_PLAN_MODE:
        report_prefix = (
            manifest.report_preferences.report_name_prefix
            or f"{resolved_profile.report_prefix}_wrapper_retry"
        )

    safe_patch = _safe_patch_name(manifest.patch_name)
    report_path_pattern = report_dir / f"{report_prefix}_{safe_patch}_<timestamp>.txt"
    backup_root_pattern = None
    if mode == "apply":
        backup_root_pattern = (
            target_root / resolved_profile.backup_root_name / f"{safe_patch}_<timestamp>"
        )

    payload = {
        "mode": mode,
        "manifest_path": str(manifest_path),
        "manifest_version": manifest.manifest_version,
        "patch_name": manifest.patch_name,
        "active_profile": resolved_profile.name,
        "workspace_root": _render_path(workspace_root),
        "wrapper_project_root": _render_path(wrapper_root),
        "target_project_root": _render_path(target_root),
        "runtime_path": _render_path(resolved_profile.runtime_path),
        "report_dir": _render_path(report_dir),
        "report_path_pattern": _render_path(report_path_pattern),
        "backup_root_pattern": _render_path(backup_root_pattern),
        "backup_files": _effective_backup_files(manifest),
        "target_files": [str((target_root / item.path).resolve()) for item in manifest.files_to_write],
        "validation_commands": [asdict(item) for item in manifest.validation_commands],
        "smoke_commands": [asdict(item) for item in manifest.smoke_commands],
        "audit_commands": [asdict(item) for item in manifest.audit_commands],
        "cleanup_commands": [asdict(item) for item in manifest.cleanup_commands],
        "archive_commands": [asdict(item) for item in manifest.archive_commands],
        "tags": list(manifest.tags),
        "notes": manifest.notes,
    }

    if mode == WRAPPER_RETRY_PLAN_MODE:
        retry_state = build_wrapper_only_retry_state(
            asdict(manifest),
            target_root,
            reason=retry_reason,
        )
        retry_payload = wrapper_only_retry_state_as_dict(retry_state)
        payload["rerun_preview"] = retry_payload
        payload["retry_reason"] = retry_payload["reason"]
        payload["writes_skipped"] = retry_payload["writes_skipped"]
        payload["needs_escalation"] = retry_payload["needs_escalation"]

    return payload