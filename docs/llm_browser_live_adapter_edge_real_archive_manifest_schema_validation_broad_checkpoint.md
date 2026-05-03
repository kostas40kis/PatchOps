# L25.18 Microsoft Edge controlled runtime archive manifest schema validation broad checkpoint

L25.18 follows accepted L25.17 and acts as a broad checkpoint over the archive manifest schema-validation ladder.

Accepted L25 schema-validation ladder so far:

- L25.16 archive manifest schema validation authorization gate.
- L25.17 first controlled synthetic manifest tiny internal schema validation proof.

Allowed in L25.18:

- read back accepted L25.17 default passive path;
- read back accepted L25.17 authorized tiny internal schema-validation proof;
- confirm the only schema-validated payload is `bundle/manifest.json`;
- confirm schema validation is limited to the tiny internal synthetic-fixture schema;
- confirm required keys and validated keys match the internal synthetic schema;
- confirm PatchOps manifest validation, package execution, extraction, browser, pasteback, and package-run remain inactive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime ZIP fixture is the only archive path used by this checkpoint.
- Archive manifest schema validation remains limited to the synthetic controlled member `bundle/manifest.json`.
- Schema validation is a tiny internal synthetic-fixture check only.
- PatchOps manifest validation is not performed.
- The validated manifest is not used for package execution.
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
- No click/download/archive-extract/PatchOps-manifest-validation/package-run/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.18"`.
- `broad_checkpoint:true`.
- `archive_manifest_schema_validation_ladder_checkpoint:true`.
- `l25_archive_manifest_schema_validation_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l25_17_default_summary.manifest_schema_validated:false`.
- `source_l25_17_authorized_summary.schema_validation_allowed:true`.
- `source_l25_17_authorized_summary.manifest_payload_json_parsed:true`.
- `source_l25_17_authorized_summary.manifest_payload_schema_validated:true`.
- `source_l25_17_authorized_summary.manifest_schema_validated:true`.
- `source_l25_17_authorized_summary.manifest_validation_performed:true`.
- `source_l25_17_authorized_summary.manifest_member_name_read:"bundle/manifest.json"`.
- `accepted_schema_validation_scope:"controlled_runtime_manifest_tiny_internal_schema_validation_only_no_patchops_validation_no_execution"`.
- `accepted_schema_summary_ok:true`.
- `accepted_schema_errors:[]`.
- `patchops_manifest_validation_performed:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_patchops_manifest_validation_added_by_l25_18:true`.

Next patch: L25.19 Microsoft Edge controlled runtime archive manifest validation-to-PatchOps-preflight authorization gate.
