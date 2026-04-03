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

See `docs/` for architecture and usage details.
