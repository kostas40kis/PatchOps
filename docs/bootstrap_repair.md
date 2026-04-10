# Bootstrap repair

## Purpose

`bootstrap-repair` is the narrow maintained recovery surface for the case where the
normal PatchOps CLI import chain is too broken to rely on ordinary repair flow.

You can reach it either as:

- `py -m patchops.bootstrap_repair`
- `py -m patchops.cli bootstrap-repair`

## Scope

This is not a second apply engine.

It is a minimal recovery tool for restoring one or a few known file paths, validating
Python syntax, and getting the repo back to the point where the normal PatchOps workflow
is usable again.

## When to use it

Use bootstrap repair only when the normal PatchOps CLI import chain is too broken, for example:

- a partially broken import chain
- a damaged helper file that stops `py -m patchops.cli ...` from booting
- a narrow known-file restoration case where the repo must become bootable first

## Recovery posture

The recovery path should stay exceptional and narrow.

- repair only the minimum files needed to restore bootability
- validate syntax before returning to normal flow
- return to the maintained PatchOps flow as soon as recovery succeeds
- treat recovery as a bridge back to the real workflow, not as a replacement for it

## After recovery

Return to the normal `check` / `inspect` / `plan` / `apply` / `verify` flow as soon as the
repo is bootable again.

The correct long-term path is still the maintained PatchOps command surface, not the
bootstrap helper itself.
