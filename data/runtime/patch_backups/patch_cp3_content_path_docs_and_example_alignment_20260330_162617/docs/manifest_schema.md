# Manifest schema and version policy

This document explains the maintained PatchOps manifest contract and the current manifest version policy.

## Current version posture

PatchOps currently authors and accepts manifest version `1` only.

That means:
- the current authoring target is `1`,
- the current supported manifest versions list contains only `1`,
- future versions must be added intentionally in code and docs,
- unsupported versions should fail closed with a readable `ManifestError`.

## Why this exists

Stage 2 needs manifest evolution to be easier to reason about for both humans and future LLMs.

The goal is not to add speculative migration machinery too early.
The goal is to make the current contract explicit and stable while preserving the already-proven authoring patterns.

## Current top-level fields

Required:
- `manifest_version`
- `patch_name`
- `active_profile`

Optional:
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

A `files_to_write` entry must provide exactly one of:
- `content`
- `content_path`

Do not set both at the same time.

`content_path` should be treated as a maintained authoring surface rather than a legacy edge case.
It exists so larger or cleaner payloads can live beside the manifest instead of being embedded inline.

See:
- `examples/generic_content_path_patch.json`
- `examples/content/generic_content_path_note.txt`

## Command groups

### validation_commands

This is the main pass/fail gate for the patch.

Each command entry may include:
- `name`
- `program`
- `args`
- `working_directory`
- `use_profile_runtime`
- `allowed_exit_codes`

Use `allowed_exit_codes` when a non-zero process result is expected and should be treated as acceptable evidence rather than a patch failure.

See:
- `examples/generic_allowed_exit_patch.json`

### smoke_commands

Use `smoke_commands` for lightweight secondary checks that help prove expected shape or basic operability after the main validation step.

### audit_commands

Use `audit_commands` for extra diagnostics or evidence-generation steps that should appear in the report without becoming the main gate.

### cleanup_commands

Use `cleanup_commands` for explicit cleanup steps that should be visible in the canonical report.

### archive_commands

Use `archive_commands` for explicit archival or export steps that should be visible in the canonical report.

## Command-group authoring guidance

Use the extra command groups when they improve clarity, not by default.

- Prefer `validation_commands` for the main gate.
- Add `smoke_commands` when a fast secondary proof is useful.
- Add `audit_commands` when the report should include diagnostics.
- Add `cleanup_commands` when temporary artifacts should be removed in a reported way.
- Add `archive_commands` when the patch intentionally creates preserved outputs or handoff artifacts.

Maintained command-group examples:
- `examples/generic_smoke_audit_patch.json`
- `examples/generic_cleanup_archive_patch.json`

## Report preferences

`report_preferences` may contain:
- `report_dir`
- `report_name_prefix`
- `write_to_desktop`

These settings control where the canonical single report is written and how it is named.

## Version policy rules

1. `manifest_version` is a string field.
2. Version `1` is the only supported value right now.
3. Unsupported versions must fail clearly.
4. Future versions require:
   - validator updates,
   - schema/reference updates,
   - docs updates,
   - tests that prove new behavior intentionally.

## Unsupported version behavior

Expected style:
- mention the unsupported value,
- mention the supported versions,
- mention the current authoring target,
- say that future versions require explicit migration and validator support.

## Recommended operator use

For authoring and repair work:

```powershell
py -m patchops.cli schema
py -m patchops.cli template --profile trader --mode apply --patch-name trader_stage1_template
py -m patchops.cli check <manifest>
py -m patchops.cli inspect <manifest>
py -m patchops.cli plan <manifest>
```

## Why future LLMs should care

A future LLM should not guess whether `manifest_version` is decorative.

It is part of the explicit contract.

A future LLM should also not guess whether `content_path`, `allowed_exit_codes`, or maintained example references are still part of the supported authoring surface.
They are part of the maintained manifest guidance and should remain documented until intentionally removed with matching code, docs, and tests.
