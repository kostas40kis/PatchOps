from __future__ import annotations

from patchops.exceptions import ManifestError


SUPPORTED_MANIFEST_VERSION = "1"


def validate_manifest_data(data: dict) -> None:
    if not isinstance(data, dict):
        raise ManifestError("Manifest must be a JSON object.")

    required = ["manifest_version", "patch_name", "active_profile"]
    missing = [key for key in required if key not in data or data[key] in (None, "")]
    if missing:
        raise ManifestError(f"Manifest is missing required field(s): {', '.join(missing)}")

    if str(data["manifest_version"]) != SUPPORTED_MANIFEST_VERSION:
        raise ManifestError(
            f"Unsupported manifest_version {data['manifest_version']!r}; expected {SUPPORTED_MANIFEST_VERSION!r}."
        )

    list_fields = [
        "backup_files",
        "files_to_write",
        "validation_commands",
        "smoke_commands",
        "audit_commands",
        "cleanup_commands",
        "archive_commands",
        "tags",
    ]
    for field_name in list_fields:
        value = data.get(field_name, [])
        if value is None:
            continue
        if not isinstance(value, list):
            raise ManifestError(f"Manifest field {field_name!r} must be a list.")

    for item in data.get("files_to_write", []):
        if not isinstance(item, dict):
            raise ManifestError("Each files_to_write entry must be an object.")
        if not item.get("path"):
            raise ManifestError("Each files_to_write entry must include 'path'.")
        has_inline = item.get("content") is not None
        has_content_path = item.get("content_path") is not None
        if has_inline and has_content_path:
            raise ManifestError(
                f"files_to_write entry for {item['path']!r} cannot include both 'content' and 'content_path'."
            )
        if not has_inline and not has_content_path:
            raise ManifestError(
                f"files_to_write entry for {item['path']!r} must include either 'content' or 'content_path'."
            )

    command_groups = [
        "validation_commands",
        "smoke_commands",
        "audit_commands",
        "cleanup_commands",
        "archive_commands",
    ]
    for group in command_groups:
        for command in data.get(group, []):
            if not isinstance(command, dict):
                raise ManifestError(f"Each entry in {group!r} must be an object.")
            if not command.get("name"):
                raise ManifestError(f"Each command in {group!r} must include 'name'.")
            if command.get("use_profile_runtime"):
                continue
            if not command.get("program"):
                raise ManifestError(
                    f"Command {command.get('name')!r} in {group!r} must include 'program' when use_profile_runtime is false."
                )
