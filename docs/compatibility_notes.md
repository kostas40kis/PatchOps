# Compatibility Notes

PatchOps is designed for Windows-friendly, PowerShell-compatible execution.

## Stage 1 compatibility posture

- prefer explicit runtime paths over PATH guessing
- avoid shell-dependent quoting tricks
- capture stdout and stderr separately
- keep PowerShell thin and move reusable logic into Python
- produce one report that stands on its own

## Practical PowerShell reality

Saved `.ps1` files can be affected by execution policy even when pasted commands still work.
PatchOps therefore keeps launcher logic minimal and places the durable behavior in Python.

<!-- PATCHOPS_SELF_HOSTED_COMPAT_NOTES:START -->
## Self-hosted manifest-authoring compatibility note

In Windows PowerShell 5.1 / PowerShell ISE, generated self-hosted PatchOps scripts should avoid relying on `ProcessStartInfo.ArgumentList`.
Use `ProcessStartInfo.Arguments` with careful argument escaping instead.

For temporary self-hosted patch manifests, prefer:
- compact JSON,
- no trailing newline,
- immediate `json.load(...)` validation before the apply step.

This reduces false starts where the wrapper never reaches the real validation target because the authoring script itself failed first.
<!-- PATCHOPS_SELF_HOSTED_COMPAT_NOTES:END -->
