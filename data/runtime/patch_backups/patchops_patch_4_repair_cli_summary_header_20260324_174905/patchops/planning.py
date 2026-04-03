from __future__ import annotations

from pathlib import Path

from patchops.manifest_loader import load_manifest
from patchops.profiles.base import resolve_profile
from patchops.workflows.common import default_report_directory, infer_workspace_root


def _safe_patch_name(patch_name: str) -> str:
    return patch_name.lower().replace(" ", "_")


def _path_text(value: Path | None) -> str | None:
    if value is None:
        return None
    return str(value.resolve())


def _command_to_dict(command) -> dict:
    return {
        "name": command.name,
        "program": command.program,
        "args": list(command.args),
        "working_directory": command.working_directory,
        "use_profile_runtime": command.use_profile_runtime,
        "allowed_exit_codes": list(command.allowed_exit_codes),
    }


def build_execution_plan(
    manifest_path: str | Path,
    wrapper_project_root: str | Path | None = None,
    mode: str = "apply",
) -> dict:
    manifest_path = Path(manifest_path).resolve()
    wrapper_root = Path(wrapper_project_root).resolve() if wrapper_project_root else Path(__file__).resolve().parents[1]

    manifest = load_manifest(manifest_path)
    resolved_profile = resolve_profile(manifest, wrapper_root)

    target_root = Path(manifest.target_project_root) if manifest.target_project_root else resolved_profile.default_target_root
    if target_root is None:
        raise ValueError("No target project root could be resolved from the manifest/profile.")

    target_root = target_root.resolve()
    workspace_root = infer_workspace_root(target_root)
    runtime_path = resolved_profile.runtime_path.resolve() if resolved_profile.runtime_path is not None else None

    safe_patch = _safe_patch_name(manifest.patch_name)
    report_dir = Path(manifest.report_preferences.report_dir) if manifest.report_preferences.report_dir else default_report_directory()
    report_dir = report_dir.resolve()

    if mode == "apply":
        report_prefix = manifest.report_preferences.report_name_prefix or resolved_profile.report_prefix
        backup_root_pattern = str(
            (target_root / resolved_profile.backup_root_name / f"{safe_patch}_<timestamp>").resolve()
        )
    elif mode == "verify":
        report_prefix = manifest.report_preferences.report_name_prefix or f"{resolved_profile.report_prefix}_verify"
        backup_root_pattern = None
    else:
        raise ValueError(f"Unsupported plan mode: {mode!r}")

    report_path_pattern = str((report_dir / f"{report_prefix}_{safe_patch}_<timestamp>.txt").resolve())

    file_paths_to_backup = sorted(set(manifest.backup_files) | {item.path for item in manifest.files_to_write})

    return {
        "mode": mode,
        "manifest_path": str(manifest_path),
        "manifest_version": manifest.manifest_version,
        "patch_name": manifest.patch_name,
        "active_profile": resolved_profile.name,
        "workspace_root": _path_text(workspace_root),
        "wrapper_project_root": _path_text(wrapper_root),
        "target_project_root": _path_text(target_root),
        "runtime_path": _path_text(runtime_path),
        "report_dir": str(report_dir),
        "report_path_pattern": report_path_pattern,
        "backup_root_pattern": backup_root_pattern,
        "backup_files": file_paths_to_backup,
        "target_files": [str((target_root / item.path).resolve()) for item in manifest.files_to_write],
        "validation_commands": [_command_to_dict(command) for command in manifest.validation_commands],
        "smoke_commands": [_command_to_dict(command) for command in manifest.smoke_commands],
        "audit_commands": [_command_to_dict(command) for command in manifest.audit_commands],
        "cleanup_commands": [_command_to_dict(command) for command in manifest.cleanup_commands],
        "archive_commands": [_command_to_dict(command) for command in manifest.archive_commands],
        "tags": list(manifest.tags),
        "notes": manifest.notes,
    }