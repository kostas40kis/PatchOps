# L25.13 Microsoft Edge controlled runtime archive manifest structure parse authorization gate

L25.13 follows accepted L25.12 and adds only a future authorization/readback gate for archive manifest structure parsing.

It does not parse the archive manifest payload yet.

Allowed in L25.13:

- read back accepted L25.12 controlled manifest payload byte-read broad checkpoint;
- confirm the synthetic manifest payload bytes were read by the source checkpoint;
- confirm manifest JSON parsing and manifest validation remain inactive;
- expose a future manifest structure parse authorization token;
- keep manifest JSON parsing execution, manifest schema validation, package execution, extraction, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Archive manifest structure parse authorization is readback-only.
- Archive manifest structure parse execution is not allowed in L25.13.
- Manifest payload bytes may be read only by accepted L25.12 source readback; L25.13 adds no new payload-read scope.
- Manifest JSON parsing is not performed.
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
- No click/download/archive-extract/manifest-parse/manifest-validation/package-run/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L25.13 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_STRUCTURE_PARSE_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.13"`.
- `source_l25_12_summary.ok:true`.
- `source_l25_12_summary.broad_checkpoint:true`.
- `source_l25_12_summary.manifest_payload_read_ladder_complete:true`.
- `source_l25_12_summary.manifest_payload_read:true`.
- `source_l25_12_summary.manifest_payload_bytes_read:true`.
- `source_l25_12_summary.manifest_member_name_read:"bundle/manifest.json"`.
- `archive_manifest_structure_parse_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `archive_manifest_structure_parse_authorization_readback_only:true`.
- `archive_manifest_structure_parse_allowed:false`.
- `manifest_payload_json_parsed:false`.
- `manifest_structure_parsed:false`.
- `manifest_payload_schema_validated:false`.
- `manifest_validation_performed:false`.
- `package_manifest_used_for_execution:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_manifest_structure_parse_execution_added_by_l25_13:true`.

Next patch: L25.14 Microsoft Edge controlled runtime archive manifest structure parse first proof.
