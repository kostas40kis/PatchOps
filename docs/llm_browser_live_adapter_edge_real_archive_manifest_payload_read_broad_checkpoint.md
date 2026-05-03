# L25.12 Microsoft Edge controlled runtime archive manifest payload-read broad checkpoint

L25.12 follows accepted L25.11 and L25.11a and acts as a broad checkpoint over the archive manifest payload-read ladder.

Accepted L25 manifest payload-read ladder so far:

- L25.10 archive manifest payload-read authorization gate.
- L25.11 first controlled synthetic manifest payload-read proof.
- L25.11a validator AST scan repair.

Allowed in L25.12:

- read back accepted L25.11 default passive path;
- read back accepted L25.11 authorized synthetic manifest payload byte-read proof;
- confirm the only accepted manifest payload read is `bundle/manifest.json`;
- confirm byte count and SHA-256 were recorded for that synthetic manifest payload;
- confirm the accepted scope is manifest payload bytes only, without JSON parsing, schema validation, or package execution;
- confirm extraction, browser, pasteback, and package-run remain inactive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime ZIP fixture is the only archive path used by this checkpoint.
- Archive manifest payload read remains limited to the synthetic controlled member `bundle/manifest.json`.
- Manifest payload bytes are read, but manifest JSON parsing is not performed.
- Manifest schema validation is not performed.
- Manifest validation is not performed.
- The manifest is not used for package execution.
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
- `patch:"L25.12"`.
- `broad_checkpoint:true`.
- `archive_manifest_payload_read_ladder_checkpoint:true`.
- `l25_archive_manifest_payload_read_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l25_11_default_summary.manifest_payload_read:false`.
- `source_l25_11_authorized_summary.manifest_payload_read:true`.
- `source_l25_11_authorized_summary.manifest_payload_bytes_read:true`.
- `source_l25_11_authorized_summary.manifest_payload_sha256_read:true`.
- `source_l25_11_authorized_summary.manifest_member_name_read:"bundle/manifest.json"`.
- `accepted_manifest_payload_read_scope:"controlled_runtime_manifest_payload_bytes_only_no_validation_no_execution"`.
- `manifest_payload_json_parsed:false`.
- `manifest_payload_schema_validated:false`.
- `manifest_validation_performed:false`.
- `package_manifest_used_for_execution:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_manifest_json_parse_or_validation_added_by_l25_12:true`.

Next patch: L25.13 Microsoft Edge controlled runtime archive manifest structure parse authorization gate.
