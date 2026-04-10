# Root launcher shape contract

## Purpose
This note records the canonical shape for the root-level `run_with_patchops.ps1` launcher used in maintained PatchOps bundles.

## Contract
- The file must begin with `param(` on the **first line**.
- There must be **no stray leading character** before `param(...)`.
- A leading backslash such as `\` is invalid, even if a later command still manages to run.
- The launcher stays thin and only validates paths, locates `bundle_meta.json`, and delegates to `py -m patchops.cli bundle-entry`.

## Why this exists
A later passing bundle still surfaced launcher stderr because a stray leading `\` was emitted before `param(...)`.
That kind of artifact is small, but it violates the boring-launcher rule and should be locked out by a maintained contract.
