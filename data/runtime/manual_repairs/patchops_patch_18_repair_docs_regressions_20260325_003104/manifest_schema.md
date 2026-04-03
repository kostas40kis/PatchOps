# PatchOps manifest schema

Patch manifests are explicit JSON documents.

## Top-level fields

Required:
- `manifest_version`
- `patch_name`
- `active_profile`

Common optional fields:
- `target_project_root`
- `backup_files`
- `files_to_write`
- `validation_commands`
- `smoke_commands`
- `audit_commands`
- `cleanup_commands`
- `archive_commands`
- `failure_policy`
- `report_preferences`
- `tags`
- `notes`

## files_to_write entries

Each `files_to_write` entry may contain:
- `path`
- `content`
- `content_path`
- `encoding`

Use `content` when the manifest should hold the payload inline.
Use `content_path` when the manifest should point at a separate text artifact that contains the payload to be written.

## command entries

Each command entry may contain:
- `name`
- `program`
- `args`
- `working_directory`
- `use_profile_runtime`
- `allowed_exit_codes`

Use `allowed_exit_codes` when a command should be treated as acceptable even if it exits non-zero.

See:
- `examples/generic_allowed_exit_patch.json`

## Command groups

### validation_commands
The primary proof that the patch is correct enough to continue.

### smoke_commands
Secondary fast checks that help prove expected shape or basic operability after validation.

### audit_commands
Extra diagnostics or evidence-generation steps that should appear in the report but are not the primary gate.

### cleanup_commands
Post-validation steps used to remove temporary files or restore a clean working state.

### archive_commands
Post-validation steps used to create explicit handoff or archival artifacts.

## Report preferences

`report_preferences` may contain:
- `report_dir`
- `report_name_prefix`
- `write_to_desktop`

These settings control where the canonical single report is written and how it is named.
