# PatchOps

PatchOps is a standalone, project-agnostic patch execution harness.

It is **not** the trader engine, target-repo business logic, strategy logic, or portfolio logic. It exists to standardize the repetitive mechanics around patch application and evidence generation across repositories.

Core intent:

- keep **what a patch changes** separate from **how a patch is executed and evidenced**
- use an explicit **manifest** as the central contract
- resolve repo-specific behavior through **profiles**
- keep **PowerShell thin** and place reusable logic in Python
- produce **one canonical report** per run with explicit runtime, roots, backups, commands, stdout/stderr, and final summary

Stage 1 ships a usable first version with:

- manifest loading and validation
- profile resolution
- trader and generic Python profiles
- deterministic backups and file writing
- process execution with stdout/stderr capture
- human-readable report rendering
- apply and verify-only flows
- thin PowerShell launchers
- examples and harness tests

## First local proving flow

Use this order before touching a real target repo:

1. `py -m pytest`
2. `py -m patchops.cli inspect .\examples\generic_python_patch.json`
3. point the generic example at a throwaway target such as `C:\dev\some_other_project`
4. `py -m patchops.cli apply .\examples\generic_python_patch.json`
5. `py -m patchops.cli inspect .\examples\generic_backup_patch.json`
6. `py -m patchops.cli apply .\examples\generic_backup_patch.json`
7. `py -m patchops.cli verify .\examples\generic_verify_patch.json`
8. inspect the single Desktop txt reports
9. only then move on to trader-profile runs

This keeps proving focused on wrapper mechanics first:

- initial write flow,
- backup behavior when a file already exists,
- verify-only reruns,
- one-report evidence discipline.

The CLI also prints a short labeled run summary after `apply` and `verify`, but the Desktop txt report remains the canonical evidence artifact.

See `docs/` for architecture and usage details.