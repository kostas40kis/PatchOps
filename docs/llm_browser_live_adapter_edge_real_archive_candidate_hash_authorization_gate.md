# L24.6 Microsoft Edge real downloaded-archive candidate hash authorization gate

L24.6 follows accepted L24.5 and adds only a future authorization/readback gate for a candidate hash proof.

It does not hash the candidate file yet.

Allowed in L24.6:

- read back accepted L24.5 controlled candidate filesystem-stat broad checkpoint;
- confirm metadata-only stat proof is complete;
- confirm hash execution and file-byte reads remain inactive;
- expose a future candidate hash authorization token;
- keep all hash, file-byte read, archive, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Candidate hash authorization is readback-only.
- Candidate hash execution is not allowed in L24.6.
- Candidate path hash is not performed.
- Downloaded file bytes are not read.
- Candidate archive is not opened.
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
- No real artifact content reading beyond accepted filesystem metadata readback.
- No click/download/real-archive-open/archive-list/archive-extract/member-byte-read/manifest-payload-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L24.6 token:

```text
PATCHOPS_L24_EDGE_REAL_ARCHIVE_CANDIDATE_HASH_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L24.6"`.
- `source_l24_05_summary.ok:true`.
- `source_l24_05_summary.broad_checkpoint:true`.
- `source_l24_05_summary.ladder_complete:true`.
- `source_l24_05_summary.accepted_stat_scope:"controlled_runtime_candidate_filesystem_metadata_only"`.
- `source_l24_05_summary.stat_performed:true`.
- `source_l24_05_summary.hash_performed:false`.
- `source_l24_05_summary.downloaded_file_bytes_read:false`.
- `real_archive_candidate_hash_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `real_archive_candidate_path_hash_allowed:false`.
- `real_archive_candidate_path_hash_performed:false`.
- `downloaded_file_bytes_read:false`.
- `downloaded_file_hash_performed:false`.
- `real_archive_candidate_opened:false`.
- `real_archive_candidate_listed:false`.
- `real_archive_candidate_extracted:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_real_archive_candidate_hash_execution_added_by_l24_6:true`.

Next patch: L24.7 Microsoft Edge real downloaded-archive candidate first controlled hash proof.
