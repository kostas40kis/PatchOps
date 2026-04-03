# Release checklist

This checklist is for a lightweight internal release of PatchOps after Stage 1 hardening.

## Before release
- [ ] Run `py -m pytest -q`
- [ ] Run `py -m patchops.cli profiles`
- [ ] Run `py -m patchops.cli doctor --profile trader`
- [ ] Run `py -m patchops.cli examples`
- [ ] Run `py -m patchops.cli schema`
- [ ] Run `py -m patchops.cli template --profile trader --mode apply --patch-name trader_stage1_template`
- [ ] Run `py -m patchops.cli check <manifest>`
- [ ] Run `py -m patchops.cli inspect <manifest>`
- [ ] Run `py -m patchops.cli plan <manifest>`

## Docs review
- [ ] `README.md` reflects the real command surface.
- [ ] `docs/project_status.md` reflects the real stage.
- [ ] `docs/patch_ledger.md` is current.
- [ ] `docs/operator_quickstart.md` still matches the recommended flow.
- [ ] `docs/repair_rerun_matrix.md` still matches actual rerun behavior.

## Operational readiness
- [ ] The team agrees on the first real trader-facing PatchOps usage.
- [ ] The manifest for that run is reviewed before apply.
- [ ] A clear rollback/backout approach exists for the target repo.
- [ ] The report location and naming expectations are understood.

## After release
- [ ] Treat Stage 1 as a baseline, not a moving target.
- [ ] Start Stage 2 intentionally instead of mixing it into Stage 1 cleanup.
