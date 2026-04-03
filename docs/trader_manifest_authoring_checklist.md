# Trader manifest authoring checklist

Use this checklist when preparing the first real trader-facing PatchOps manifest.

## Before editing the manifest
- Confirm PatchOps itself is healthy:
  - `py -m pytest -q`
  - `py -m patchops.cli doctor --profile trader`
- Review:
  - `docs/trader_first_usage.md`
  - `docs/stage1_freeze_checklist.md`
  - `docs/release_checklist.md`

## Manifest authoring
- Start from a low-risk trader starter example.
- Confirm `active_profile` is `trader`.
- Confirm `target_project_root` points at the trader repo.
- List any files that must be backed up explicitly.
- Keep the first trader-facing manifest intentionally small.
- Prefer documentation-only, validation-only, or tiny repo-safe writes first.

## Before execution
- Run:
  - `py -m patchops.cli check <manifest>`
  - `py -m patchops.cli inspect <manifest>`
  - `py -m patchops.cli plan <manifest>`
- Confirm:
  - report location is understood,
  - validation commands are explicit,
  - the patch does not move trader business logic into PatchOps.

## Success criteria
- The manifest is understandable without reading PatchOps source.
- The report is deterministic.
- Backups are explicit.
- Validation output is complete.
- Failure mode is clearly wrapper-only or trader-side.
