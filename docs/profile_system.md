# Profile system

## Purpose

Profiles let PatchOps adapt execution behavior to a target repository without moving target-side business logic into the wrapper core.

The profile system stays narrow:

- profile choice is execution configuration,
- docs and packets remain the human-facing contract,
- target repos still own target behavior.

## Current maintained profile posture

For PatchOps acting as its own current target, the selected profile remains `generic_python`.

That is still the correct self-hosted maintenance choice because:

- PatchOps is still a normal Python repository from the wrapper's point of view,
- self-hosted work should exercise the generic wrapper surfaces,
- PowerShell should remain thin,
- reusable logic should remain Python-owned.

## Practical profile rule

Start with the smallest correct profile and widen only when the target actually needs it.

That means:

- prefer `generic_python` when a normal Python repo is enough,
- use a more specific profile only when the target really requires it,
- keep the wrapper project-agnostic even when PatchOps patches itself.

## Operator expectations

Before a risky run:

- choose the smallest correct profile,
- run `check`, `inspect`, and `plan`,
- read the canonical report instead of guessing from terminal output.

## What profiles should not do

Profiles should not become a place to hide:

- target-side strategy,
- target-side operational policy,
- broad PowerShell workflow logic,
- redesign work that belongs in the target repo.
