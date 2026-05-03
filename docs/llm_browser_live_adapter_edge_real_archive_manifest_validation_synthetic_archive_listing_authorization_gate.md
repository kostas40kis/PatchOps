# L23.3 Microsoft Edge real downloaded-archive manifest validation synthetic-archive listing authorization gate

L23.3 follows accepted L23.2/L23.2a.

It adds only a future authorization/readback surface for synthetic archive listing. It does not list anything yet.

Allowed in L23.3:

- read back accepted L23.2 synthetic archive preflight;
- confirm the fixed synthetic archive path was statted by L23.2;
- expose a future listing authorization token;
- keep listing execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- No new archive listing permission is added by L23.3.
- Synthetic archive listing authorization is readback-only.
- Synthetic archive listing execution allowed remains false.
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
- No ZIP archive module loading.
- No click/download/archive-open/archive-list/archive-extract/member-byte-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L23.3 token:

```text
PATCHOPS_L23_EDGE_SYNTHETIC_ARCHIVE_LISTING_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L23.3"`.
- `source_l23_02_summary.ok:true`.
- `source_l23_02_summary.preflight_allowed:true`.
- `source_l23_02_summary.synthetic_archive_path_stat_performed:true`.
- `synthetic_archive_listing_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `synthetic_archive_listing_execution_allowed:false`.
- `downloaded_archive_opened:false`.
- `downloaded_archive_contents_listed:false`.
- `real_archive_manifest_read:false`.
- `archive_member_bytes_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_new_archive_listing_permission_added_by_l23_3:true`.

Next patch: L23.4 Microsoft Edge real downloaded-archive manifest validation first synthetic-archive listing proof.
