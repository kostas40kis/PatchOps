# L25.31 Microsoft Edge controlled runtime archive manifest package-run authorization gate

L25.31 follows accepted L25.30 and adds only a future authorization/readback gate for package-run over the archive manifest.

It does not run PatchOps run-package or package-run yet.

Allowed in L25.31:

- read back accepted L25.30 controlled PatchOps apply-only broad checkpoint;
- confirm the synthetic archive manifest passed the zero-write and zero-validation apply-only proof in the source checkpoint;
- confirm PatchOps run-package, package execution, extraction, browser, pasteback, and package-run remain inactive;
- expose a future package-run authorization token;
- keep PatchOps run-package execution, package execution, extraction, browser, pasteback, and package-run disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Archive manifest package-run authorization is readback-only.
- Archive manifest package-run execution is not allowed in L25.31.
- PatchOps apply-only proof may be read only by accepted L25.30 source readback; L25.31 adds no new apply or run-package execution scope.
- PatchOps run-package is not invoked against the archive manifest copy.
- The synthetic manifest is not used for package execution.
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
- No click/download/archive-extract/run-package/package-run/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L25.31 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PACKAGE_RUN_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.31"`.
- `source_l25_30_summary.ok:true`.
- `source_l25_30_summary.broad_checkpoint:true`.
- `source_l25_30_summary.apply_ladder_complete:true`.
- `source_l25_30_summary.patchops_cli_apply_invoked_for_archive_manifest:true`.
- `source_l25_30_summary.patchops_cli_apply_exit_code:0`.
- `source_l25_30_summary.patchops_cli_apply_stdout_result_pass:true`.
- `archive_manifest_package_run_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `archive_manifest_package_run_authorization_readback_only:true`.
- `archive_manifest_package_run_allowed:false`.
- `patchops_run_package_performed:false`.
- `patchops_cli_run_package_invoked_for_archive_manifest:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_patchops_run_package_execution_added_by_l25_31:true`.

Next patch: L25.32 Microsoft Edge controlled runtime archive manifest package-run first proof.
