# L24.7 Microsoft Edge real downloaded-archive candidate first controlled hash proof

L24.7 follows accepted L24.6 and performs the first controlled candidate hash proof.

Allowed in L24.7:

- read back accepted L24.6 hash authorization;
- refresh a controlled runtime candidate fixture during validator setup;
- read only that controlled fixture's file bytes for SHA-256 hashing after explicit token authorization;
- compute SHA-256 for that controlled candidate fixture;
- keep archive open/list/extract/read, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime candidate fixture is the only path used by this proof.
- Candidate hash proof is allowed only with explicit flag and token.
- File bytes are read only for SHA-256 over the controlled runtime candidate fixture.
- Candidate archive is not opened as an archive.
- Candidate archive is not listed.
- Candidate archive is not extracted.
- Real archive manifest is not read.
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
- No archive member-byte read.
- No manifest payload read.
- No click/download/real-archive-open/archive-list/archive-extract/manifest-payload-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L24.7 token:

```text
PATCHOPS_L24_EDGE_REAL_ARCHIVE_CANDIDATE_FIRST_CONTROLLED_HASH_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L24.7"`.
- `source_l24_06_summary.ok:true`.
- `source_l24_06_summary.future_hash_authorized:true`.
- default passive readback has `real_archive_candidate_path_hash_performed:false`.
- authorized readback has `real_archive_candidate_path_hash_allowed:true`.
- authorized readback has `real_archive_candidate_path_hash_performed:true`.
- `downloaded_file_bytes_read:true`.
- `downloaded_file_hash_performed:true`.
- `real_archive_candidate_sha256_read:true`.
- `real_archive_candidate_sha256` is a 64-character lowercase hex string.
- `real_archive_candidate_bytes_read_count` is a positive integer.
- `candidate_hash_scope:"controlled_runtime_candidate_sha256_file_bytes_only_no_archive_open"`.
- `real_archive_candidate_opened:false`.
- `real_archive_candidate_listed:false`.
- `real_archive_candidate_extracted:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_archive_open_permission_added_by_l24_7:true`.

Next patch: L24.8 Microsoft Edge real downloaded-archive candidate hash broad checkpoint.
