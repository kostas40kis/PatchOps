# Trader Repo Inventory

<!-- PATCH_279_POST_275_REPO_INVENTORY_REFRESH_START -->

## Patch 279 — Post-275 Repo Inventory Refresh

### Current accepted frontier

The current accepted overall frontier is **Patch 275 — `cautious_live_widening_pilot_final_handoff_packet.py`**.

Patch 125 — `cautious_live_manual_review_request.py` remains the production milestone frontier, and Patch 134 — `repo_backup_archive_cleanup.py` remains the cleanup/documentation milestone. They are important historical milestones, but they are not the latest overall accepted frontier.

Accepted release evidence for the current frontier:

- commit SHA: `4d24c9ec65a8f2643a6b1ba482e82a27915fb77b`
- GitHub CI run: `25049340880`
- release result: `PASS`
- full release gate discovery: `1774 tests OK`

### Modern operator-support scripts

The post-275 repo inventory should explicitly recognize these operator-support scripts:

- `scripts\test_and_upload_trader_to_github.ps1`
- `scripts\create_trader_green_checkpoint_tag.ps1`

These scripts are operator wrappers and release/checkpoint helpers. They are not the home of canonical trading logic.

### Pilot-control architecture family

The Patch 254–275 pilot-control family is now part of the active repo shape. It is review-only and no-submit oriented.

Key surfaces include:

- `cautious_live_widening_pilot_runbook`
- `cautious_live_widening_pilot_evidence_log`
- `cautious_live_widening_pilot_preflight_check`
- `cautious_live_widening_pilot_stop_conditions`
- `cautious_live_widening_pilot_monitoring_plan`
- `cautious_live_widening_pilot_review_packet`
- `cautious_live_widening_pilot_go_no_go_summary`
- `cautious_live_widening_pilot_operator_handoff`
- `cautious_live_widening_pilot_operator_acceptance_record`
- `cautious_live_widening_pilot_safety_barrier`
- `cautious_live_widening_pilot_readiness_attestation`
- `cautious_live_widening_pilot_execution_window`
- `cautious_live_widening_pilot_incident_response_plan`
- `cautious_live_widening_pilot_recovery_drill`
- `cautious_live_widening_pilot_audit_digest`
- `cautious_live_widening_pilot_closeout_report`
- `cautious_live_widening_pilot_batch_release_checklist`
- `cautious_live_widening_pilot_suite_runner`
- `cautious_live_widening_pilot_documentation_stop`
- `cautious_live_widening_pilot_release_readiness_report`
- `cautious_live_widening_pilot_milestone_gate`
- `cautious_live_widening_pilot_final_handoff_packet`

For each pilot-control surface, the canonical pattern remains:

```text
src\trader\execution\<surface>.py
docs\architecture\<surface>.md
tests\test_<surface>.py
scripts\run_patch_<patch>_<surface>_tests.ps1
```

### Canonical implementation center

`src\trader\execution` remains the implementation center of gravity for canonical execution, review, safety, pilot-control, shadow, and future growth-control logic.

Thin PowerShell runners and manual scripts may call this layer, but they must not absorb deep canonical logic.

### Runtime and release evidence artifacts

Release evidence reports are external Desktop artifacts produced by PatchOps or the release gate; they are authoritative evidence to review, but they are not repo-tracked source files.

Runtime/report artifacts, PatchOps reports, release gate reports, Desktop txt reports, temporary logs, generated caches, and archived residue should be treated as non-canonical or caution-required. They can be evidence, but they should not be confused with maintained source, tests, or architecture notes.

### Safety boundary

Patch 275 is a review-only final handoff frontier. It does not authorize live trading, wallet mutation, order submission, or unattended autonomy.

Patch 279 does not:

- submit orders
- call wallet signing code
- alter wallet code
- bypass manual review
- authorize unattended live trading
- weaken production gates

### Inventory interpretation rule

When reading the repo after Patch 279, use this order:

1. current accepted frontier evidence through Patch 275,
2. maintained top-level docs,
3. `docs\architecture`,
4. `src\trader\execution`,
5. `tests`,
6. `scripts`,
7. runtime/external report evidence only as supporting artifacts.

Do not infer the current frontier from old Patch 70 presence markers or from Patch 125/134 milestone wording alone.

<!-- PATCH_279_POST_275_REPO_INVENTORY_REFRESH_END -->
