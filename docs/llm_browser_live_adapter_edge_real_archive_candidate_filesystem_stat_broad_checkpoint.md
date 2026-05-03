# L24.5 Microsoft Edge real downloaded-archive candidate filesystem stat broad checkpoint

L24.5 follows accepted L24.4 and acts as a broad checkpoint over the controlled candidate filesystem-stat ladder.

Accepted L24 stat ladder:

- L24.1 real downloaded-archive candidate authorization gate.
- L24.2/L24.2a candidate path string-only preflight gate.
- L24.3 candidate filesystem stat authorization gate.
- L24.4 controlled runtime candidate filesystem stat proof.

Allowed in L24.5:

- read back accepted L24.4 default passive path;
- read back accepted L24.4 authorized controlled candidate stat proof;
- confirm candidate exists and is a file;
- confirm candidate size, suffix, and modification-time metadata were read;
- confirm the accepted scope is controlled runtime candidate filesystem metadata only;
- confirm hash, file-byte read, archive open/list/extract/read, browser, pasteback, and package-run remain inactive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime candidate fixture is the only path used by this checkpoint.
- Candidate filesystem stat is metadata-only.
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

Expected compact JSON signals:

- `ok:true`.
- `patch:"L24.5"`.
- `broad_checkpoint:true`.
- `filesystem_stat_ladder_checkpoint:true`.
- `l24_candidate_stat_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l24_04_default_summary.stat_performed:false`.
- `source_l24_04_authorized_summary.stat_performed:true`.
- `source_l24_04_authorized_summary.candidate_exists:true`.
- `source_l24_04_authorized_summary.candidate_is_file:true`.
- `source_l24_04_authorized_summary.candidate_size_read:true`.
- `source_l24_04_authorized_summary.candidate_suffix:".zip"`.
- `source_l24_04_authorized_summary.candidate_mtime_read:true`.
- `accepted_stat_scope:"controlled_runtime_candidate_filesystem_metadata_only"`.
- `real_archive_candidate_path_stat_performed:true`.
- `real_archive_candidate_path_hash_performed:false`.
- `downloaded_file_bytes_read:false`.
- `real_archive_candidate_opened:false`.
- `real_archive_candidate_listed:false`.
- `real_archive_candidate_extracted:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_hash_or_archive_open_permission_added_by_l24_5:true`.

Next patch: L24.6 Microsoft Edge real downloaded-archive candidate hash authorization gate.
