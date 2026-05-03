# L24.4 Microsoft Edge real downloaded-archive candidate filesystem stat proof

L24.4 follows accepted L24.3 and performs the first controlled candidate filesystem stat proof.

Allowed in L24.4:

- read back accepted L24.3 stat authorization;
- create a controlled runtime candidate fixture during validator setup;
- stat only that controlled candidate fixture path after explicit token authorization;
- check candidate existence;
- check candidate is a file;
- read candidate size metadata;
- check `.zip` suffix using filesystem metadata proof context;
- read candidate modification-time metadata;
- keep all hash, archive open/list/extract/read, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime candidate fixture is the only path used by this proof.
- Candidate filesystem stat is allowed only with explicit flag and token.
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
- No real artifact content reading beyond filesystem metadata.
- No click/download/real-archive-open/archive-list/archive-extract/member-byte-read/manifest-payload-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L24.4 token:

```text
PATCHOPS_L24_EDGE_REAL_ARCHIVE_CANDIDATE_FILESYSTEM_STAT_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L24.4"`.
- `source_l24_03_summary.ok:true`.
- `source_l24_03_summary.future_stat_authorized:true`.
- default passive readback has `real_archive_candidate_path_stat_performed:false`.
- authorized readback has `real_archive_candidate_path_stat_allowed:true`.
- authorized readback has `real_archive_candidate_path_stat_performed:true`.
- `real_archive_candidate_exists:true`.
- `real_archive_candidate_is_file:true`.
- `real_archive_candidate_size_bytes_read:true`.
- `real_archive_candidate_size_bytes` is a positive integer.
- `real_archive_candidate_suffix_checked_on_filesystem:true`.
- `real_archive_candidate_suffix:".zip"`.
- `real_archive_candidate_mtime_read:true`.
- `candidate_stat_scope:"controlled_runtime_candidate_filesystem_metadata_only"`.
- `real_archive_candidate_path_hash_performed:false`.
- `downloaded_file_bytes_read:false`.
- `real_archive_candidate_opened:false`.
- `real_archive_candidate_listed:false`.
- `real_archive_candidate_extracted:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_hash_or_archive_open_permission_added_by_l24_4:true`.

Next patch: L24.5 Microsoft Edge real downloaded-archive candidate filesystem stat broad checkpoint.
