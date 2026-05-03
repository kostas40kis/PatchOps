# L25.25 Microsoft Edge controlled runtime archive manifest PatchOps plan authorization gate

L25.25 follows accepted L25.24 and adds only a future authorization/readback gate for PatchOps plan over the archive manifest.

It does not run PatchOps plan on the archive manifest yet.

Allowed in L25.25:

- read back accepted L25.24 controlled PatchOps inspect-only broad checkpoint;
- confirm the synthetic archive manifest passed the inspect-only proof in the source checkpoint;
- confirm PatchOps plan, apply, run-package, package execution, extraction, browser, pasteback, and package-run remain inactive;
- expose a future PatchOps-plan authorization token;
- keep PatchOps plan execution, apply, run-package, package execution, extraction, browser, pasteback, and package-run disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Archive manifest PatchOps-plan authorization is readback-only.
- Archive manifest PatchOps-plan execution is not allowed in L25.25.
- PatchOps inspect-only proof may be read only by accepted L25.24 source readback; L25.25 adds no new inspect or plan execution scope.
- PatchOps plan is not invoked against the archive manifest copy.
- PatchOps apply is not invoked against the archive manifest copy.
- PatchOps run-package is not invoked against the archive manifest copy.
- The inspected manifest is not used for package execution.
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
- No click/download/archive-extract/PatchOps-plan/PatchOps-apply/package-run/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L25.25 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PATCHOPS_PLAN_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.25"`.
- `source_l25_24_summary.ok:true`.
- `source_l25_24_summary.broad_checkpoint:true`.
- `source_l25_24_summary.inspect_ladder_complete:true`.
- `source_l25_24_summary.patchops_cli_inspect_invoked_for_archive_manifest:true`.
- `source_l25_24_summary.patchops_cli_inspect_exit_code:0`.
- `source_l25_24_summary.patchops_cli_inspect_json_object:true`.
- `archive_manifest_patchops_plan_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `archive_manifest_patchops_plan_authorization_readback_only:true`.
- `archive_manifest_patchops_plan_allowed:false`.
- `patchops_manifest_plan_performed:false`.
- `patchops_cli_plan_invoked_for_archive_manifest:false`.
- `patchops_cli_apply_invoked_for_archive_manifest:false`.
- `patchops_cli_run_package_invoked_for_archive_manifest:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_patchops_plan_execution_added_by_l25_25:true`.

Next patch: L25.26 Microsoft Edge controlled runtime archive manifest PatchOps plan first proof.
