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

See:
- `examples/generic_content_path_patch.json`
- `examples/content/generic_content_path_note.txt`

Additional command-group examples:
- `examples/generic_smoke_audit_patch.json`
- `examples/generic_cleanup_archive_patch.json`

## Command groups

### validation_commands
The primary proof that the patch is correct enough to continue.

Each command entry may include:
- `name`
- `program`
- `args`
- `working_directory`
- `use_profile_runtime`
- `allowed_exit_codes`

Use `allowed_exit_codes` when a non-zero process result is expected and should be treated as acceptable evidence instead of a failure.

See:
- `examples/generic_allowed_exit_patch.json`

### smoke_commands
Secondary fast checks that help prove expected shape or basic operability after validation.

### audit_commands
Extra diagnostics or evidence-generation steps that should appear in the report but are not the primary gate.

### cleanup_commands
Post-validation steps used to remove temporary files or restore a clean working state.

### archive_commands
Post-validation steps used to create explicit handoff or archival artifacts.

## Command-group authoring guidance

Use the additional command groups only when they improve clarity.

- Prefer `validation_commands` for the main pass/fail gate.
- Add `smoke_commands` when you want lightweight extra confirmation.
- Add `audit_commands` when you want extra diagnostics in the report.
- Add `cleanup_commands` when temporary artifacts should be removed in a reported way.
- Add `archive_commands` when the patch intentionally produces preserved artifacts or export outputs.

See:
- `examples/generic_smoke_audit_patch.json`
- `examples/generic_cleanup_archive_patch.json`

## Report preferences

`report_preferences` may contain:
- `report_dir`
- `report_name_prefix`
- `write_to_desktop`

These settings control where the canonical single report is written and how it is named.

Report-preference behavior is also covered by an apply-flow test, proving that a manifest can direct its canonical report into a custom directory with a custom prefix.
