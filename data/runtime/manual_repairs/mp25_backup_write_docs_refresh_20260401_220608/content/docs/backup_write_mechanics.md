# Backup and write mechanics

This note explains the current PatchOps file-mechanics posture after the Pythonization Phase C work landed.

## What changed

Backup and write mechanics are now **Python-owned reusable surfaces** rather than patch-body boilerplate.

That means a maintenance patch should not keep re-implementing the same backup-copy rules, mkdir rules, content loading rules, or write-report formatting in each individual patch body.

Instead, the shared helper path now owns those mechanics.

## The helper-owned path

The maintained helper path is:

- backup planning and backup execution stay in the Python file-mechanics layer,
- write intent is normalized before execution,
- single-file writes go through one deterministic helper,
- batch writes go through one shared orchestration path,
- canonical report lines come from the same helper-owned truth as the actual backup and write behavior.

## What contributors should do

When a new patch needs to touch files:

1. prefer the existing Python backup/write helpers,
2. keep PowerShell thin and operator-facing,
3. avoid rebuilding file choreography inside each patch body,
4. keep report evidence aligned with actual helper behavior,
5. preserve current manifest semantics and the maintained content-path contract.

## What this does not mean

This docs refresh does **not** introduce a new product surface and does **not** redesign PatchOps.

It only clarifies that the repetitive file mechanics now belong to reusable Python helpers instead of one-off patch boilerplate.

## Current maintained contract

The current maintained contract for this area is:

- helper-owned backup and write mechanics,
- one canonical report path,
- wrapper project root first for the maintained content-path rule,
- manifest-local compatibility fallback where that legacy path still matters,
- narrow proof patches preferred over broad rewrites.

## Contributor guidance

If you are writing a new maintenance patch, start by asking:

- is there already a helper for this backup/write step?
- can I prove the behavior with a narrow test or proof patch instead of widening the design?
- am I keeping PowerShell boring and the real mechanics in Python?

If the answer is yes, stay on the helper-owned path.
