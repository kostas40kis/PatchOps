# Operator script emitter

## Purpose

`emit-operator-script` is the maintained repo-owned way to generate thin, operator-facing PowerShell helpers for supported PatchOps actions.

The emitted output is a **repo-owned template** generated from maintained Python code, not an ad hoc hand-authored script and not a second workflow engine.

## Why this surface exists

This surface exists so common operator helpers can be produced from one maintained source instead of being recopied and slowly drifting back into old quoting, compatibility, launcher-shape, and operator ergonomics bugs.

Treat the emitted helper as a **copy/paste-safe** operator surface generated from a maintained **compatibility shim**, not as a place to rebuild wrapper logic by hand.

## Current maintained emitted-script examples

Supported examples include thin helpers for:

- `run-package-zip`
- `maintenance-gate`

**Keep PowerShell thin.**

**Keep reusable mechanics in Python.**

The intelligence remains in Python and the generated script stays thin.

## Windows compatibility rule

Generated scripts must remain compatible with **Windows PowerShell 5.1**.

That means process-launch helpers must support older hosts where `ArgumentList` may be unavailable:
- use `ArgumentList` when the property exists,
- otherwise fall back to `Arguments`.

The doc keeps the exact `ArgumentList` and `Arguments` terms here because that compatibility rule is part of the supported contract.

## Guardrails

- Treat the emitted helper as a maintained operator shim, not as target-project logic.
- Do not let emitted scripts become a second apply engine.
- Keep operator output grounded in the maintained command surface.
- Prefer the repo-owned template over one-off pasteable rewrites when a supported emitted helper already exists.

## Maintained emitted operator surfaces

`emit-operator-script` is the maintained surface for repo-owned PowerShell helpers.

Current emitted families include:
- `run-package-zip`
- `maintenance-gate`

The emitted scripts are thin shims. They must forward JSON truth from Python rather than reinterpreting it in PowerShell.
- `maintenance-gate` remains a current emitted operator script surface.
- Keep emitted operator scripts thin and JSON-forwarding.
Emitted operator scripts remain thin shims.
They must forward JSON truthfully.
They should not become a second workflow engine.

- `patchops-entry-ps1`
