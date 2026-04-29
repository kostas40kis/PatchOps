# Trader Frontier Detection Rules

<!-- PATCH_276_POST_275_FRONTIER_TRUTH_SYNC_START -->
## Post-275 frontier truth sync

Patch 276 updates the maintained frontier rule source for the accepted post-275 state.

Current accepted overall frontier:

- Patch: `275`
- Module: `cautious_live_widening_pilot_final_handoff_packet.py`
- Release commit: `4d24c9ec65a8f2643a6b1ba482e82a27915fb77b`
- GitHub CI run: `25049340880` (`success`)
- Release result: `PASS`
- Full tests: `1774 tests OK`

Important historical milestones that must remain visible but must not be treated as the latest overall frontier:

- Patch 125 — `cautious_live_manual_review_request.py` — production milestone frontier for the original cautious-live manual review chain.
- Patch 134 — `repo_backup_archive_cleanup.py` — cleanup/documentation stabilization milestone.
- Patch 70 — `entry_execution_coordinator.py` / `entry_execution_coordinator.md` / `run_patch_70_entry_execution_coordinator...` — historical entry-execution marker only.

Exporter and summary wording must not infer the current frontier from old file-presence markers such as:

```text
entry_execution_coordinator.md present : True
run_patch_70_entry_execution_coordinator present : True
```

Preferred wording is:

```text
Current accepted frontier detected from accepted release evidence
Patch number: 275
Patch module: cautious_live_widening_pilot_final_handoff_packet.py
Release result: PASS
GitHub CI run: 25049340880 (success)
Full tests: 1774 tests OK
```

This frontier sync is review-only. It does not authorize live trading, does not submit orders, does not touch wallets, and does not widen autonomous behavior.
<!-- PATCH_276_POST_275_FRONTIER_TRUTH_SYNC_END -->
