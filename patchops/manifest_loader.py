from __future__ import annotations

import json
from pathlib import Path

from patchops.exceptions import ManifestError
from patchops.manifest_validator import validate_manifest_data
from patchops.models import CommandSpec, FileWriteSpec, Manifest, ReportPreferences


def _list_from_first(data: dict, *keys: str) -> list:
    for key in keys:
        if key in data and data[key] is not None:
            value = data[key]
            if isinstance(value, list):
                return list(value)
            return [value]
    return []


def _command_args_from_dict(data: dict) -> list[str]:
    # `args` is the canonical key. `arguments` is accepted for older
    # generated/bundled manifests so legacy bundles do not accidentally launch
    # only the runtime executable and hang in an interactive Python REPL.
    values = _list_from_first(data, "args", "arguments")
    return [str(value) for value in values]


def _command_from_dict(data: dict) -> CommandSpec:
    return CommandSpec(
        name=data["name"],
        program=data.get("program"),
        args=_command_args_from_dict(data),
        working_directory=data.get("working_directory"),
        use_profile_runtime=bool(data.get("use_profile_runtime", False)),
        allowed_exit_codes=[int(value) for value in _list_from_first(data, "allowed_exit_codes") or [0]],
    )


def _file_write_from_dict(data: dict) -> FileWriteSpec:
    return FileWriteSpec(
        path=data["path"],
        content=data.get("content"),
        content_path=data.get("content_path"),
        encoding=data.get("encoding", "utf-8"),
    )


def load_manifest(path: str | Path) -> Manifest:
    manifest_path = Path(path)
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestError(f"Manifest file not found: {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"Manifest is not valid JSON: {exc}") from exc

    validate_manifest_data(raw)

    report_preferences = ReportPreferences(**raw.get("report_preferences", {}))
    return Manifest(
        manifest_version=str(raw["manifest_version"]),
        patch_name=raw["patch_name"],
        active_profile=raw["active_profile"],
        target_project_root=raw.get("target_project_root"),
        backup_files=[str(value) for value in _list_from_first(raw, "backup_files", "files_to_backup", "backup_paths")],
        files_to_write=[_file_write_from_dict(item) for item in _list_from_first(raw, "files_to_write", "file_writes", "writes")],
        validation_commands=[_command_from_dict(item) for item in raw.get("validation_commands", [])],
        smoke_commands=[_command_from_dict(item) for item in raw.get("smoke_commands", [])],
        audit_commands=[_command_from_dict(item) for item in raw.get("audit_commands", [])],
        cleanup_commands=[_command_from_dict(item) for item in raw.get("cleanup_commands", [])],
        archive_commands=[_command_from_dict(item) for item in raw.get("archive_commands", [])],
        failure_policy=dict(raw.get("failure_policy", {})),
        report_preferences=report_preferences,
        tags=list(raw.get("tags", [])),
        notes=raw.get("notes"),
    )
