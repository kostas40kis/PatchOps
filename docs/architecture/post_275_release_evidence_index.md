# Post-275 Release Evidence Index

Patch 280 adds a canonical, review-only release evidence index for the post-275 frontier.

## Purpose

Patch 276 through Patch 279 synchronized the maintained frontier, ledger, test matrix, and repo inventory around the real current accepted frontier:

- **Patch 275** — `cautious_live_widening_pilot_final_handoff_packet.py`
- accepted commit `4d24c9ec65a8f2643a6b1ba482e82a27915fb77b`
- GitHub CI run `25049340880`
- release gate result `PASS`
- full discovery count `1774 tests OK`

Patch 280 adds the missing release-evidence index so Batch A has a single chronological release-evidence read model before the official release stop.

## Indexed batches

The index records these post-252 batches:

1. Patch 252 — accepted release gate script
2. Patch 253 — green checkpoint tag and restore guide
3. Patch 254 — release-gate repair and pilot runbook
4. Patch 255R-260 — evidence, preflight, stop, monitoring, review, and go/no-go packet
5. Patch 261-270 — operator handoff, acceptance, safety, execution-window, incident, recovery, audit, closeout, and batch checklist
6. Patch 271-275 — suite runner, documentation stop, release readiness, milestone gate, and final handoff packet

Entries whose remote SHA or GitHub CI run are not embedded in the available roadmap evidence are marked incomplete rather than falsely promoted to `PASS`.

## Fail-closed evidence rule

A release entry cannot be considered complete when either of these are missing:

- remote commit SHA
- GitHub CI run ID

If an entry claims `PASS` without those fields, the effective result becomes `BLOCKED_INCOMPLETE_EVIDENCE`.

## Safety boundary

This patch is a release-evidence read model only. It does not:

- submit orders,
- fetch quotes,
- mutate wallets,
- change live thresholds,
- start autonomous loops,
- bypass operator review,
- authorize a real-money pilot.

A complete index means release evidence is easier to review. It is not a live execution approval.

## Validation

Patch-specific validation is provided by:

`tests/test_post_275_release_evidence_index.py`

and runner:

`scripts/run_patch_280_post_275_release_evidence_index_tests.ps1`

## Release stop after this patch

Patch 280 is the end of Batch A. After this patch passes locally, the operator should run the official release gate:

```powershell
& "C:\dev\trader\scripts\test_and_upload_trader_to_github.ps1" `
  -RepoRoot "C:\dev\trader" `
  -CommitMessage "Refresh post-275 trader frontier and release evidence"
```

Only continue to Patch 281 after full discovery, commit/push, remote HEAD match, and GitHub CI success.
