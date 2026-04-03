# Profile matrix

This document gives a fast profile-selection view for Stage 1 PatchOps usage.

## Profiles

| Profile | Use when | Default target root | Notes |
|---|---|---|---|
| `trader` | You are patching the trader repo under the shared workspace. | `C:/dev/trader` | First real target profile. Keep trader-specific assumptions inside the profile, not the core. |
| `generic_python` | The target repo is mainly Python and does not need PowerShell-native smoke commands in the starter flow. | none | Best default generic profile for simple patch, check, inspect, and verify flows. |
| `generic_python_powershell` | The target repo is still generic, but the operator expects Python patching plus occasional PowerShell smoke or helper steps. | none | Good proving ground for mixed Python + PowerShell workflows without hardcoding trader behavior. |

## Selection rules

1. Prefer `trader` only for the trader repo.
2. Prefer `generic_python` for portable Python-first repos.
3. Prefer `generic_python_powershell` when the repo still stays generic but your validation or smoke surface needs both runtimes.

## Stage 1 recommendation

Before touching trader, prove the flow in this order:

1. `generic_python` example apply
2. `generic_python` backup-proof example
3. `generic_python` verify example
4. `generic_python_powershell` example inspection
5. trader-oriented examples only after the generic flows are understood


## Generic Python + PowerShell apply proof

A dedicated apply-flow test now proves that `generic_python_powershell` can execute a PowerShell validation command plus a Python smoke command and still produce a clean PASS report.
