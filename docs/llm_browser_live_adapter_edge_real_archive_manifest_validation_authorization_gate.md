# L23.1 Microsoft Edge real downloaded-archive manifest validation authorization gate

L23.1 starts a new separately gated post-L22 stream.

L22 ended with a final marker proving only synthetic manifest fixture validation. L22 explicitly did not grant real browser, real downloaded artifact, real archive, pasteback, send/submit, or package-run permission.

L23.1 adds only a readback authorization gate for future real downloaded-archive manifest validation.

Authorization token name:

```text
REQUIRED_REAL_ARCHIVE_MANIFEST_AUTHORIZATION_TOKEN
```

Authorization token value:

```text
PATCHOPS_L23_EDGE_REAL_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_AUTHORIZED_READBACK_ONLY
```

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Candidate archive path may be recorded as a string only.
- Candidate archive path is not statted.
- Candidate archive path is not hashed.
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
- No real artifact content reading.
- No downloaded file bytes read.
- No archive open.
- No archive listing.
- No archive extraction.
- No archive member-byte read.
- No real archive manifest read.
- No click/download/archive-open/archive-list/archive-extract/member-byte-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L23.1"`.
- `source_l22_07_summary.l22_complete:true`.
- `real_archive_manifest_authorization_granted_for_future_patch:true` when both flag and token are supplied.
- `real_archive_manifest_validation_execution_allowed:false`.
- `real_archive_opened:false`.
- `downloaded_archive_contents_listed:false`.
- `real_archive_manifest_read:false`.
- `archive_member_bytes_read:false`.
- `candidate_archive_path_stat_performed:false`.
- `candidate_archive_path_hash_performed:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_new_execution_permission_added_by_l23_1:true`.

Next patch: L23.2 Microsoft Edge real downloaded-archive manifest validation synthetic-archive preflight gate.
