# L25.15 Microsoft Edge controlled runtime archive manifest structure parse broad checkpoint

L25.15 follows accepted L25.14 and acts as a broad checkpoint over the archive manifest structure-parse ladder.

Accepted L25 manifest structure-parse ladder so far:

- L25.13 archive manifest structure parse authorization gate.
- L25.14 first controlled synthetic manifest JSON structure parse proof.

Allowed in L25.15:

- read back accepted L25.14 default passive path;
- read back accepted L25.14 authorized synthetic manifest JSON structure parse proof;
- confirm the only parsed payload is `bundle/manifest.json`;
- confirm the structure summary records top-level object type, top-level keys, scalar value-type names, and nested-key names;
- confirm the accepted scope is JSON structure parsing only, without schema validation, PatchOps manifest validation, or package execution;
- confirm extraction, browser, pasteback, and package-run remain inactive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime ZIP fixture is the only archive path used by this checkpoint.
- Archive manifest structure parsing remains limited to the synthetic controlled member `bundle/manifest.json`.
- Manifest payload JSON parsing is accepted only as structure parsing.
- Manifest schema validation is not performed.
- PatchOps manifest validation is not performed.
- The parsed manifest is not used for package execution.
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
- No click/download/archive-extract/manifest-validation/package-run/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.15"`.
- `broad_checkpoint:true`.
- `archive_manifest_structure_parse_ladder_checkpoint:true`.
- `l25_archive_manifest_structure_parse_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l25_14_default_summary.manifest_payload_json_parsed:false`.
- `source_l25_14_default_summary.manifest_structure_parsed:false`.
- `source_l25_14_authorized_summary.manifest_payload_json_parsed:true`.
- `source_l25_14_authorized_summary.manifest_structure_parsed:true`.
- `source_l25_14_authorized_summary.manifest_member_name_read:"bundle/manifest.json"`.
- `accepted_manifest_structure_parse_scope:"controlled_runtime_manifest_json_structure_parse_only_no_schema_validation_no_execution"`.
- `accepted_manifest_top_level_type:"object"`.
- `manifest_payload_schema_validated:false`.
- `manifest_validation_performed:false`.
- `patchops_manifest_validation_performed:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_manifest_schema_validation_added_by_l25_15:true`.

Next patch: L25.16 Microsoft Edge controlled runtime archive manifest schema validation authorization gate.
