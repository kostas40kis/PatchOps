# L25.28 Microsoft Edge controlled runtime archive manifest PatchOps apply authorization gate

L25.28 follows accepted L25.27 and adds only a future authorization/readback gate for PatchOps apply over the archive manifest.

It does not run PatchOps apply on the archive manifest yet.

Allowed in L25.28:

- read back accepted L25.27 controlled PatchOps plan-only broad checkpoint;
- confirm the synthetic archive manifest passed the plan-only proof in the source checkpoint;
- confirm PatchOps apply, run-package, package execution, extraction, browser, pasteback, and package-run remain inactive;
- expose a future PatchOps-apply authorization token;
- keep PatchOps apply execution, run-package, package execution, extraction, browser, pasteback, and package-run disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Archive manifest PatchOps-apply authorization is readback-only.
- Archive manifest PatchOps-apply execution is not allowed in L25.28.
- PatchOps plan-only proof may be read only by accepted L25.27 source readback; L25.28 adds no new plan or apply execution scope.
- PatchOps apply is not invoked against the archive manifest copy.
- PatchOps run-package is not invoked against the archive manifest copy.
- The planned manifest is not used for package execution.
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
- No click/download/archive-extract/PatchOps-apply/package-run/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L25.28 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PATCHOPS_APPLY_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.28"`.
- `source_l25_27_summary.ok:true`.
- `source_l25_27_summary.broad_checkpoint:true`.
- `source_l25_27_summary.plan_ladder_complete:true`.
- `source_l25_27_summary.patchops_cli_plan_invoked_for_archive_manifest:true`.
- `source_l25_27_summary.patchops_cli_plan_exit_code:0`.
- `source_l25_27_summary.patchops_cli_plan_json_object:true`.
- `archive_manifest_patchops_apply_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `archive_manifest_patchops_apply_authorization_readback_only:true`.
- `archive_manifest_patchops_apply_allowed:false`.
- `patchops_manifest_apply_performed:false`.
- `patchops_cli_apply_invoked_for_archive_manifest:false`.
- `patchops_cli_run_package_invoked_for_archive_manifest:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_patchops_apply_execution_added_by_l25_28:true`.

Next patch: L25.29 Microsoft Edge controlled runtime archive manifest PatchOps apply first proof.
