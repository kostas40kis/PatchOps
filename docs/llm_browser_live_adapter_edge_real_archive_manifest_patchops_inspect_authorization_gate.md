# L25.22 Microsoft Edge controlled runtime archive manifest PatchOps inspect authorization gate

L25.22 follows accepted L25.21 and adds only a future authorization/readback gate for PatchOps inspect over the archive manifest.

It does not run PatchOps inspect on the archive manifest yet.

Allowed in L25.22:

- read back accepted L25.21 controlled PatchOps check-only preflight broad checkpoint;
- confirm the synthetic archive manifest passed the check-only preflight in the source checkpoint;
- confirm PatchOps inspect, plan, apply, run-package, package execution, extraction, browser, pasteback, and package-run remain inactive;
- expose a future PatchOps-inspect authorization token;
- keep PatchOps inspect execution, plan, apply, run-package, package execution, extraction, browser, pasteback, and package-run disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Archive manifest PatchOps-inspect authorization is readback-only.
- Archive manifest PatchOps-inspect execution is not allowed in L25.22.
- PatchOps check-only preflight may be read only by accepted L25.21 source readback; L25.22 adds no new preflight execution scope.
- PatchOps inspect is not invoked against the archive manifest copy.
- PatchOps plan is not invoked against the archive manifest copy.
- PatchOps apply is not invoked against the archive manifest copy.
- PatchOps run-package is not invoked against the archive manifest copy.
- The checked manifest is not used for package execution.
- Candidate archive is not extracted.
- No browser activity.
- No Microsoft Edge start.
- No Selenium import.
- No CDP use.
- No DOM scraping.
- No page inspection.
- No prompt text extraction.
- No conversation reading.
- No real download workflow.
- No real browser download.
- No click/download/archive-extract/PatchOps-inspect/PatchOps-plan/PatchOps-apply/package-run/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L25.22 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PATCHOPS_INSPECT_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.22"`.
- `source_l25_21_summary.ok:true`.
- `source_l25_21_summary.broad_checkpoint:true`.
- `source_l25_21_summary.preflight_ladder_complete:true`.
- `source_l25_21_summary.patchops_cli_check_invoked_for_archive_manifest:true`.
- `source_l25_21_summary.patchops_cli_check_exit_code:0`.
- `source_l25_21_summary.patchops_cli_check_ok:true`.
- `source_l25_21_summary.patchops_cli_check_issue_count:0`.
- `archive_manifest_patchops_inspect_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `archive_manifest_patchops_inspect_authorization_readback_only:true`.
- `archive_manifest_patchops_inspect_allowed:false`.
- `patchops_manifest_inspect_performed:false`.
- `patchops_cli_inspect_invoked_for_archive_manifest:false`.
- `patchops_cli_plan_invoked_for_archive_manifest:false`.
- `patchops_cli_apply_invoked_for_archive_manifest:false`.
- `patchops_cli_run_package_invoked_for_archive_manifest:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_patchops_inspect_execution_added_by_l25_22:true`.

Next patch: L25.23 Microsoft Edge controlled runtime archive manifest PatchOps inspect first proof.
