# L23.2 Microsoft Edge real downloaded-archive manifest validation synthetic-archive preflight gate

L23.2 advances from the accepted L23.1 authorization gate to a fixed synthetic archive preflight.

Allowed in L23.2:

- read back the accepted L23.1 authorization gate;
- record only the fixed synthetic archive fixture path;
- stat only that fixed synthetic fixture path for existence and size;
- verify the fixed fixture path has a `.zip` suffix.

The synthetic fixture is a PatchOps-created path fixture. It is not opened as an archive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Synthetic archive fixture path may be statted only when the explicit L23.2 flag and token are supplied.
- No real candidate archive path stat.
- No real candidate archive path hash.
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
- No archive open.
- No archive listing.
- No archive extraction.
- No archive member-byte read.
- No real archive manifest read.
- No `zipfile` import.
- No click/download/archive-open/archive-list/archive-extract/member-byte-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L23.2 token:

```text
PATCHOPS_L23_EDGE_SYNTHETIC_ARCHIVE_PREFLIGHT_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L23.2"`.
- `synthetic_archive_preflight_allowed:true`.
- `preflight_scope:"fixed_synthetic_archive_path_existence_and_size_only"`.
- `synthetic_archive_path_recorded:true`.
- `synthetic_archive_path_is_fixed:true`.
- `synthetic_archive_path_exists:true`.
- `synthetic_archive_path_stat_performed:true`.
- `synthetic_archive_size_bytes` is positive.
- `downloaded_file_stat_performed:false`.
- `candidate_archive_path_stat_performed:false`.
- `candidate_archive_path_hash_performed:false`.
- `downloaded_archive_opened:false`.
- `downloaded_archive_contents_listed:false`.
- `downloaded_archive_extracted:false`.
- `archive_member_bytes_read:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.

Next patch: L23.3 Microsoft Edge real downloaded-archive manifest validation synthetic-archive listing authorization gate.
