from __future__ import annotations

from patchops.manifest_validator import (
    CURRENT_MANIFEST_VERSION,
    SUPPORTED_MANIFEST_VERSIONS,
    manifest_version_policy_summary,
)


def build_manifest_schema_summary() -> dict:
    version_policy = manifest_version_policy_summary()
    return {
        "manifest_version": CURRENT_MANIFEST_VERSION,
        "current_manifest_version": CURRENT_MANIFEST_VERSION,
        "supported_manifest_versions": list(SUPPORTED_MANIFEST_VERSIONS),
        "version_policy": version_policy,
        "required_top_level_fields": [
            "manifest_version",
            "patch_name",
            "active_profile",
        ],
        "optional_top_level_fields": [
            "target_project_root",
            "backup_files",
            "files_to_write",
            "validation_commands",
            "smoke_commands",
            "audit_commands",
            "cleanup_commands",
            "archive_commands",
            "failure_policy",
            "report_preferences",
            "tags",
            "notes",
        ],
        "manifest_version_field": {
            "type": "string",
            "current_value": CURRENT_MANIFEST_VERSION,
            "supported_values": list(SUPPORTED_MANIFEST_VERSIONS),
            "authoring_target": CURRENT_MANIFEST_VERSION,
            "future_compatibility_intent": version_policy["compatibility_intent"],
            "unsupported_behavior": version_policy["unsupported_version_behavior"],
        },
        "command_groups": {
            "validation_commands": "Primary proof commands that usually determine pass/fail.",
            "smoke_commands": "Lightweight confidence checks after writing files.",
            "audit_commands": "Optional information-gathering commands for context or evidence.",
            "cleanup_commands": "Optional post-run cleanup commands.",
            "archive_commands": "Optional archival steps for packaging or preserving artifacts.",
        },
        "report_preferences": {
            "report_dir": "Optional explicit report directory.",
            "report_name_prefix": "Optional prefix for deterministic report naming.",
            "write_to_desktop": "When true, write the canonical report to the Desktop.",
        },
        "files_to_write_fields": {
            "path": "Target-relative output path.",
            "content": "Inline content to write. Usually null when content_path is used.",
            "content_path": "Optional wrapper-relative path to source content.",
            "encoding": "Text encoding to use when writing.",
        },
        "command_fields": {
            "name": "Human-readable command label in reports.",
            "program": "Executable name or explicit path.",
            "args": "Argument array, already split into stable tokens.",
            "working_directory": "Working directory, usually '.' for target root.",
            "use_profile_runtime": "When true, allow the profile to resolve the runtime.",
            "allowed_exit_codes": "Exit codes that should count as success.",
        },
        "starter_notes": [
            "Prefer 'template' to generate a starting manifest instead of writing one from scratch.",
            "Run 'check' before 'inspect', 'plan', 'apply', or 'verify'.",
            "Replace placeholder paths, commands, and notes before real use.",
            "Keep target-repo business logic out of PatchOps manifests; manifests describe execution mechanics.",
            "Treat manifest_version as an explicit contract, not a casual label.",
        ],
    }