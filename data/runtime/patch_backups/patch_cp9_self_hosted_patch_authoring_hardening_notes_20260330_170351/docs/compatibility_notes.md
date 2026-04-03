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
