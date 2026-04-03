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
The goal is to make the current contract explicit and stable.

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
- say that future versions require explicit migration/validator support.

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
If a new version is ever introduced, the wrapper should teach that change deliberately instead of silently accepting unknown shapes.