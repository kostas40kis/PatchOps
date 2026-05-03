# L25.11 Microsoft Edge controlled runtime archive manifest payload-read first proof

L25.11 follows accepted L25.10 and performs the first controlled archive manifest payload-read proof.

L25.11a repairs the validator only: forbidden validation behavior is now detected through Python AST call/import inspection instead of raw text matching. This prevents safe marker names such as `manifest_payload_schema_validated` from being mistaken for schema validation execution.

Allowed in L25.11:

- read back accepted L25.10 manifest payload-read authorization;
- create a controlled ZIP fixture during validator setup;
- open the controlled ZIP fixture after explicit token authorization;
- read bytes from exactly one controlled synthetic manifest member: `bundle/manifest.json`;
- compute byte count and SHA-256 for that manifest member payload;
- keep manifest validation, package execution, extraction, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime ZIP fixture is the only archive path used by this proof.
- Archive manifest payload read is allowed only with explicit flag and token.
- The only manifest payload read is the synthetic controlled member `bundle/manifest.json`.
- Manifest payload bytes are read, but manifest validation is not performed.
- Manifest JSON parsing is not performed.
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

L25.11 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PAYLOAD_READ_FIRST_CONTROLLED_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.11"`.
- `repair_patch:"L25.11a"` from the validator output.
- `source_l25_10_summary.ok:true`.
- `source_l25_10_summary.future_manifest_payload_read_authorized:true`.
- default passive readback has `manifest_payload_read:false`.
- authorized readback has `archive_manifest_payload_read_allowed:true`.
- authorized readback has `manifest_payload_read:true`.
- authorized readback has `manifest_payload_bytes_read:true`.
- authorized readback has `manifest_payload_sha256_read:true`.
- authorized readback has `manifest_member_name_read:"bundle/manifest.json"`.
- `manifest_payload_read_scope:"controlled_runtime_manifest_payload_bytes_only_no_validation_no_execution"`.
- `manifest_payload_json_parsed:false`.
- `manifest_payload_schema_validated:false`.
- `manifest_validation_performed:false`.
- `package_manifest_used_for_execution:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_manifest_validation_added_by_l25_11:true`.

Next patch: L25.12 Microsoft Edge controlled runtime archive manifest payload-read broad checkpoint.
