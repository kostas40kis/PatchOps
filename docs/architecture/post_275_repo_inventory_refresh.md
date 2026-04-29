# Post-275 Repo Inventory Refresh

Patch 279 refreshes the maintained repo inventory for the post-275 project shape.

## Purpose

The project has moved beyond the old Patch 125 and Patch 134 maintained-doc baseline. Patch 275 is now the current accepted overall frontier, while Patch 125 remains the production milestone and Patch 134 remains the cleanup/documentation milestone.

This patch keeps that distinction visible inside `trader_repo_inventory.md` so future work does not reason from stale Patch 70, Patch 125, or Patch 134-only language.

## What this patch adds

Patch 279 adds a canonical helper and validator that render and check the post-275 inventory section.

The refreshed inventory must mention:

- `scripts\test_and_upload_trader_to_github.ps1`,
- `scripts\create_trader_green_checkpoint_tag.ps1`,
- the Patch 254–275 pilot-control architecture family,
- the pilot-control modules, docs, tests, and runners,
- release evidence reports as external Desktop artifacts, not repo-tracked source files,
- `src\trader\execution` as the canonical implementation center of gravity.

## Safety posture

This patch is documentation/reference-only.

It does not:

- submit orders,
- call wallet signing code,
- alter wallet code,
- bypass manual review,
- authorize unattended live trading,
- weaken production gates.

## Operator interpretation

A passing Patch 279 test means the repo inventory now describes the post-275 repo shape coherently. It does not mean that a pilot is approved, that live behavior has widened, or that autonomous trading is allowed.
