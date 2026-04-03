# PatchOps

PatchOps is a standalone, project-agnostic patch execution harness.

It is **not** the trader engine, target-repo business logic, strategy logic, or portfolio logic. It exists to standardize the repetitive mechanics around patch application and evidence generation across repositories.

Core intent:

- keep **what a patch changes** separate from **how a patch is executed and evidenced**
- use an explicit **manifest** as the central contract
- resolve repo-specific behavior through **profiles**
- keep **PowerShell thin** and place reusable logic in Python
- produce **one canonical report** per run with explicit runtime, roots, backups, commands, stdout/stderr, and final summary

## Stage 1 status

Stage 1 is already proving the core workflow:

- manifests load and validate
- profiles resolve
- files can be written deterministically
- backups can be proven before writes
- validation commands run with stdout/stderr capture
- verify-only reruns work
- one canonical report is produced
- the CLI now supports both `inspect` and `plan` before any real apply run

## CLI commands

- `patchops inspect <manifest>`
  - print the normalized manifest JSON
- `patchops plan <manifest>`
  - print the resolved execution preview without writing files or running commands
- `patchops apply <manifest>`
  - execute a manifest-driven patch run
- `patchops verify <manifest>`
  - run a verify-only rerun flow

## Recommended proving order before touching trader

1. `inspect` the generic example manifest
2. `plan` the generic example manifest
3. `apply` the generic example manifest against a throwaway repo
4. `plan` the generic backup-proof example
5. `apply` the generic backup-proof example to prove backup behavior
6. `verify` the generic verify-only example
7. move to trader-profile manifests only after the generic proving path is clean

See `docs/` for architecture and usage details.