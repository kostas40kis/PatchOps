from __future__ import annotations

from patchops.exceptions import ManifestError


CURRENT_MANIFEST_VERSION = "1"
SUPPORTED_MANIFEST_VERSIONS = (CURRENT_MANIFEST_VERSION,)


def manifest_version_policy_summary() -> dict[str, object]:
    return {
        "current_manifest_version": CURRENT_MANIFEST_VERSION,
        "supported_manifest_versions": list(SUPPORTED_MANIFEST_VERSIONS),
        "authoring_target": CURRENT_MANIFEST_VERSION,
        "compatibility_intent": (
            "Current authoring targets v1 only. "
            "Future manifest versions require explicit validator and documentation updates."
        ),
        "unsupported_version_behavior": (
            "Unsupported manifest versions fail closed with a readable ManifestError."
        ),
    }


def validate_manifest_version(value: object) -> str:
    normalized = str(value)
    if normalized not in SUPPORTED_MANIFEST_VERSIONS:
        supported = ", ".join(repr(item) for item in SUPPORTED_MANIFEST_VERSIONS)
        raise ManifestError(
            "Unsupported manifest_version "
            f"{normalized!r}; supported versions: {supported}. "
            f"Current authoring target: {CURRENT_MANIFEST_VERSION!r}. "
            "Future versions require explicit migration/validator support."
        )
    return normalized


def validate_manifest_data(data: dict) -> None:
    if not isinstance(data, dict):
        raise ManifestError("Manifest must be a JSON object.")

    required = ["manifest_version", "patch_name", "active_profile"]
    missing = [key for key in required if key not in data or data[key] in (None, "")]
    if missing:
        raise ManifestError(f"Manifest is missing required field(s): {', '.join(missing)}")

    validate_manifest_version(data["manifest_version"])

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

    for item in data.get("validation_commands", []):
        if not isinstance(item, dict):
            raise ManifestError("Each validation_commands entry must be an object.")
        if not item.get("name"):
            raise ManifestError("Each validation_commands entry must include 'name'.")
        if not item.get("program") and not item.get("use_profile_runtime"):
            raise ManifestError(
                f"Validation command {item.get('name', '<unnamed>')!r} must include "
                "'program' or set 'use_profile_runtime' to true."
            )