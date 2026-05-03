# L24.2 Microsoft Edge real downloaded-archive candidate path string preflight gate

L24.2 follows accepted L24.1 and performs only string-level preflight of a future real downloaded-archive candidate path.

L24.2a repairs the default/passive readback: no-token mode is expected to be `ok:true` while preflight remains not allowed and no candidate path analysis is performed.

Allowed in L24.2:

- read back accepted L24.1 real candidate authorization;
- record a candidate archive path as a string;
- when explicitly authorized, check the string is non-empty;
- when explicitly authorized, check the string looks like an absolute Windows path;
- when explicitly authorized, check the string ends with `.zip`;
- when explicitly authorized, check the string has no wildcard characters;
- when explicitly authorized, check the string has no `..` traversal segment;
- keep all filesystem, archive, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Candidate archive path may be analyzed as a string only.
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

L24.2 token:

```text
PATCHOPS_L24_EDGE_REAL_ARCHIVE_CANDIDATE_PATH_STRING_PREFLIGHT_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L24.2"`.
- `repair_patch:"L24.2a"`.
- default passive readback has `candidate_path_string_preflight_allowed:false` and `candidate_path_string_preflight_scope:"default_readback_only_no_candidate_path_analysis"`.
- authorized readback has `source_l24_01_summary.future_candidate_authorized:true`.
- authorized readback has `candidate_path_string_preflight_allowed:true`.
- authorized readback has `candidate_path_string_preflight_scope:"string_only_no_filesystem_touch"`.
- `candidate_path_string_checks.candidate_path_string_nonempty:true`.
- `candidate_path_string_checks.candidate_path_string_absolute_windows:true`.
- `candidate_path_string_checks.candidate_path_string_zip_suffix:true`.
- `candidate_path_string_checks.candidate_path_string_has_no_wildcards:true`.
- `candidate_path_string_checks.candidate_path_string_has_no_traversal_segments:true`.
- `real_archive_candidate_path_stat_performed:false`.
- `real_archive_candidate_path_hash_performed:false`.
- `real_archive_candidate_exists:false`.
- `real_archive_candidate_opened:false`.
- `real_archive_candidate_listed:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_real_archive_candidate_filesystem_permission_added_by_l24_2:true`.

Next patch: L24.3 Microsoft Edge real downloaded-archive candidate filesystem stat authorization gate.
