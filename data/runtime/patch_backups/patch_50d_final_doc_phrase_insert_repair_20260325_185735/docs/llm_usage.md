# LLM Usage Guide

PatchOps is a **standalone wrapper / harness project**.

Target repo = what changes  
PatchOps = how the change is applied, validated, and evidenced

## how to read the project

Read in this order:

1. `README.md`
2. `docs/project_status.md`
3. `docs/overview.md`
4. `docs/manifest_schema.md`
5. `docs/profile_system.md`
6. `docs/compatibility_notes.md`
7. `docs/failure_repair_guide.md`
8. `docs/examples.md`

## how to pick a profile

Use the smallest correct profile:

- `trader`
- `generic_python`
- `generic_python_powershell`

Do not move target-repo logic into PatchOps.

## how to build a manifest

Start from bundled examples and adapt them.
Use `examples/trader_first_verify_patch.json` as the safest trader-first verification starter when appropriate.

## how to decide between apply and verify-only

Use `apply` when files need to be written.
Use verify-only when files are already on disk and the goal is narrow validation or wrapper-only repair.

See also:
- `powershell/Invoke-PatchVerify.ps1`
- `docs/failure_repair_guide.md`

## how to classify failure

Treat failures as either:

- target-repo content failure
- wrapper mechanics failure

## how to avoid moving target-repo logic into PatchOps

Keep trader-specific or target-specific assumptions in the profile or target repo, not in the generic core.