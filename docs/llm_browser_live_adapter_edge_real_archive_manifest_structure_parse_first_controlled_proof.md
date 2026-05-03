# L25.14 Microsoft Edge controlled runtime archive manifest structure parse first proof

L25.14 follows accepted L25.13 and performs the first controlled archive manifest structure parse proof.

Allowed in L25.14:

- read back accepted L25.13 manifest structure parse authorization;
- create a controlled ZIP fixture during validator setup;
- open the controlled ZIP fixture after explicit token authorization;
- read bytes from exactly one controlled synthetic manifest member: `bundle/manifest.json`;
- parse that payload as JSON;
- report non-sensitive structural metadata only: top-level type, top-level keys, scalar value-type names, and nested-key names;
- keep manifest schema validation, PatchOps manifest validation, package execution, extraction, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime ZIP fixture is the only archive path used by this proof.
- Archive manifest structure parse is allowed only with explicit flag and token.
- The only parsed payload is the synthetic controlled member `bundle/manifest.json`.
- Manifest payload JSON parsing is performed.
- Manifest structure parsing is performed.
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

L25.14 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_STRUCTURE_PARSE_FIRST_CONTROLLED_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.14"`.
- `source_l25_13_summary.ok:true`.
- `source_l25_13_summary.future_manifest_structure_parse_authorized:true`.
- default passive readback has `manifest_payload_json_parsed:false`.
- authorized readback has `archive_manifest_structure_parse_allowed:true`.
- authorized readback has `manifest_payload_read:true`.
- authorized readback has `manifest_payload_bytes_read:true`.
- authorized readback has `manifest_payload_json_parsed:true`.
- authorized readback has `manifest_structure_parsed:true`.
- authorized readback has `manifest_member_name_read:"bundle/manifest.json"`.
- `manifest_structure_parse_scope:"controlled_runtime_manifest_json_structure_parse_only_no_schema_validation_no_execution"`.
- `manifest_structure_summary.top_level_type:"object"`.
- `manifest_payload_schema_validated:false`.
- `manifest_validation_performed:false`.
- `patchops_manifest_validation_performed:false`.
- `package_manifest_used_for_execution:false`.
- `package_run:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `no_manifest_schema_validation_added_by_l25_14:true`.

Next patch: L25.15 Microsoft Edge controlled runtime archive manifest structure parse broad checkpoint.
