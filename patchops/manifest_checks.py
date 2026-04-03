from __future__ import annotations

from pathlib import Path
from typing import Any

from patchops.manifest_loader import load_manifest


PLACEHOLDER_PATH = "relative/path/to/file.ext"
PLACEHOLDER_COMMAND_NAME = "validation_command"
PLACEHOLDER_NOTE_SNIPPET = "replace placeholder"


def _normalize(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).replace("\\", "/").strip().lower()


def _is_placeholder_path(value: str | None) -> bool:
    return _normalize(value) == PLACEHOLDER_PATH


def _add_issue(issues: list[str], message: str) -> None:
    issues.append(message)


def check_manifest_path(manifest_path: str | Path) -> dict[str, Any]:
    manifest_file = Path(manifest_path)
    manifest = load_manifest(manifest_file)
    issues: list[str] = []

    if manifest.target_project_root is None:
        _add_issue(issues, "target_project_root is not set.")

    for index, backup_path in enumerate(manifest.backup_files):
        if _is_placeholder_path(backup_path):
            _add_issue(issues, f"backup_files[{index}] still uses placeholder path: {backup_path}")

    for index, file_spec in enumerate(manifest.files_to_write):
        if _is_placeholder_path(file_spec.path):
            _add_issue(issues, f"files_to_write[{index}].path still uses placeholder path: {file_spec.path}")
        if file_spec.content is None and file_spec.content_path is None:
            _add_issue(issues, f"files_to_write[{index}] has neither inline content nor content_path.")

    for index, command in enumerate(manifest.validation_commands):
        if command.name == PLACEHOLDER_COMMAND_NAME:
            _add_issue(issues, f"validation_commands[{index}].name still uses starter value: {command.name}")
        if not str(command.program).strip():
            _add_issue(issues, f"validation_commands[{index}].program is empty.")

    notes_text = manifest.notes or ""
    if PLACEHOLDER_NOTE_SNIPPET in notes_text.lower():
        _add_issue(issues, "notes still contain placeholder instructions.")

    return {
        "manifest_path": str(manifest_file.resolve()),
        "patch_name": manifest.patch_name,
        "active_profile": manifest.active_profile,
        "ok": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
    }