# L24.3 Microsoft Edge real downloaded-archive candidate filesystem stat authorization gate

L24.3 follows accepted L24.2a and adds only a future authorization/readback gate for candidate filesystem stat.

It does not stat the candidate path yet.

Allowed in L24.3:

- read back accepted L24.2a string-only preflight;
- confirm the candidate path string passed string-only checks;
- expose a future candidate filesystem stat authorization token;
- keep filesystem stat execution disabled;
- keep all hash, existence, size, archive, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Candidate archive path may be carried as a string only.
- Candidate archive path is not statted.
- Candidate archive path is not hashed.
- Candidate archive suffix is not checked on the filesystem.
- Candidate archive existence is not checked.
- Candidate archive size is not read.
- No downloaded file bytes read.
- No downloaded file hash.
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
- No real downloaded archive open.
- No real downloaded archive listing.
- No archive extraction.
- No real archive manifest read.
- No click/download/real-archive-open/archive-list/archive-extract/member-byte-read/manifest-payload-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L24.3 token:

```text
PATCHOPS_L24_EDGE_REAL_ARCHIVE_CANDIDATE_FILESYSTEM_STAT_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L24.3"`.
- `source_l24_02_summary.ok:true`.
- `source_l24_02_summary.repair_patch:"L24.2a"`.
- `source_l24_02_summary.string_preflight_allowed:true`.
- `real_archive_candidate_stat_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `real_archive_candidate_path_stat_allowed:false`.
- `real_archive_candidate_path_stat_performed:false`.
- `real_archive_candidate_path_hash_performed:false`.
- `real_archive_candidate_exists:false`.
- `real_archive_candidate_size_bytes_read:false`.
- `real_archive_candidate_opened:false`.
- `real_archive_candidate_listed:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_real_archive_candidate_filesystem_execution_added_by_l24_3:true`.

Next patch: L24.4 Microsoft Edge real downloaded-archive candidate filesystem stat proof.
