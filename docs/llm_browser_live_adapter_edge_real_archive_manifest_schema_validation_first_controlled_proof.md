# L25.17 Microsoft Edge controlled runtime archive manifest schema validation first proof

L25.17 follows accepted L25.16 and performs the first controlled archive manifest schema-validation proof.

Allowed in L25.17:

- read back accepted L25.16 schema-validation authorization;
- create a controlled ZIP fixture during validator setup;
- open the controlled ZIP fixture after explicit token authorization;
- read bytes from exactly one controlled synthetic manifest member: `bundle/manifest.json`;
- parse that payload as JSON;
- validate the parsed object against a tiny internal schema for the synthetic fixture only;
- report required keys, validated keys, expected type names, and validation errors;
- keep PatchOps manifest validation, package execution, extraction, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime ZIP fixture is the only archive path used by this proof.
- Archive manifest schema validation is allowed only with explicit flag and token.
- The only schema-validated payload is the synthetic controlled member `bundle/manifest.json`.
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

L25.17 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_SCHEMA_VALIDATION_FIRST_CONTROLLED_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.17"`.
- `source_l25_16_summary.ok:true`.
- `source_l25_16_summary.future_schema_validation_authorized:true`.
- default passive readback has `manifest_schema_validated:false`.
- authorized readback has `archive_manifest_schema_validation_allowed:true`.
- authorized readback has `manifest_payload_read:true`.
- authorized readback has `manifest_payload_json_parsed:true`.
- authorized readback has `manifest_payload_schema_validated:true`.
- authorized readback has `manifest_schema_validated:true`.
- authorized readback has `manifest_validation_performed:true`.
- authorized readback has `manifest_member_name_read:"bundle/manifest.json"`.
- `manifest_schema_validation_scope:"controlled_runtime_manifest_tiny_internal_schema_validation_only_no_patchops_validation_no_execution"`.
- `manifest_schema_validation_summary.ok:true`.
- `patchops_manifest_validation_performed:false`.
- `package_manifest_used_for_execution:false`.
- `package_run:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `no_patchops_manifest_validation_added_by_l25_17:true`.

Next patch: L25.18 Microsoft Edge controlled runtime archive manifest schema validation broad checkpoint.
