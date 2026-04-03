# Trader Profile

The `trader` profile is the first real PatchOps profile.

## Defaults

- target root: `C:\dev\trader`
- runtime path: `C:\dev\trader\.venv\Scripts\python.exe`
- backup root: `data/runtime/patch_backups`
- report prefix: `trader_patch`

## Boundary reminder

Trader-specific assumptions belong in this profile and in trader manifests.
They do not belong in the generic PatchOps core.
