# L24.8 Microsoft Edge real downloaded-archive candidate hash broad checkpoint

L24.8 follows accepted L24.7 and acts as a broad checkpoint over the controlled hash ladder.

Accepted L24 hash ladder:

- L24.6 candidate hash authorization gate.
- L24.7 first controlled SHA-256 proof over controlled runtime fixture bytes.

Allowed in L24.8:

- read back accepted L24.7 default passive path;
- read back accepted L24.7 authorized controlled hash proof;
- confirm SHA-256 was computed only over the controlled runtime candidate fixture bytes;
- confirm the digest is a 64-character lowercase hex string;
- confirm archive open/list/extract/read, browser, pasteback, and package-run remain inactive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime candidate fixture is the only path used by this checkpoint.
- File bytes are read only for accepted SHA-256 readback over the controlled runtime candidate fixture.
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

Expected compact JSON signals:

- `ok:true`.
- `patch:"L24.8"`.
- `broad_checkpoint:true`.
- `hash_ladder_checkpoint:true`.
- `l24_candidate_hash_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l24_07_default_summary.hash_performed:false`.
- `source_l24_07_authorized_summary.hash_performed:true`.
- `source_l24_07_authorized_summary.downloaded_file_bytes_read:true`.
- `source_l24_07_authorized_summary.downloaded_file_hash_performed:true`.
- `source_l24_07_authorized_summary.sha256_read:true`.
- `source_l24_07_authorized_summary.bytes_read_count` is a positive integer.
- `accepted_hash_scope:"controlled_runtime_candidate_sha256_file_bytes_only_no_archive_open"`.
- `accepted_sha256_is_lower_hex:true`.
- `real_archive_candidate_path_hash_performed:true`.
- `downloaded_file_bytes_read:true`.
- `downloaded_file_hash_performed:true`.
- `real_archive_candidate_opened:false`.
- `real_archive_candidate_listed:false`.
- `real_archive_candidate_extracted:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_archive_open_permission_added_by_l24_8:true`.

Next patch: L24.9 Microsoft Edge real downloaded-archive candidate metadata/hash final acceptance marker.
