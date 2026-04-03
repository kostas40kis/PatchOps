# Release readiness evidence

This document explains the stable evidence path for PatchOps release-readiness output.

## Goal

Preserve release-gate evidence in a deterministic text artifact instead of relying only on transient console output.

## Recommended commands

CLI:

```powershell
py -m patchops.cli release-readiness --profile trader --core-tests-green --report-path C:\Users\Public\patchops_release_readiness.txt
```

PowerShell launcher:

```powershell
.\powershell\Invoke-PatchReadiness.ps1 -Profile trader -CoreTestsGreen -ReportPath C:\Users\Public\patchops_release_readiness.txt
```

## Stable output conventions

The generated text artifact is intentionally plain and deterministic.

It includes:
- `PATCHOPS RELEASE READINESS`
- wrapper project path
- focused profile
- status
- core test state
- docs/examples/workflows/launchers/profiles status
- missing surface sections
- issues
- recommended commands
- notes

## Why this exists

Stage 2 needs release discipline to be easier to preserve and hand off.
A deterministic text artifact is easier to archive, compare, and pass to future LLMs than ad hoc console snippets.