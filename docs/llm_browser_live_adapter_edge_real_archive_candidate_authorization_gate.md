# L24.1 Microsoft Edge real downloaded-archive candidate authorization gate

L24.1 starts a new separately gated post-L23 stream.

L23 ended with a final synthetic acceptance marker. L23 accepted only the fixed synthetic archive fixture and only the synthetic `manifest.json` payload proof. L23 did not grant real downloaded-archive validation, browser activity, pasteback, send/submit, or package-run permission.

Allowed in L24.1:

- read back accepted L23.9 final synthetic marker;
- record a candidate archive path as a string only;
- expose a future real downloaded-archive candidate authorization token;
- keep all filesystem, archive, browser, pasteback, and package-run execution disabled.

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

L24.1 token:

```text
PATCHOPS_L24_EDGE_REAL_DOWNLOADED_ARCHIVE_CANDIDATE_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L24.1"`.
- `source_l23_09_summary.final_synthetic_acceptance_marker:true`.
- `source_l23_09_summary.l23_synthetic_complete:true`.
- `source_l23_09_summary.real_downloaded_archive_permission_granted:false`.
- `real_archive_candidate_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `candidate_archive_path_recorded_as_string_only:true` when a candidate string is supplied.
- `real_archive_candidate_path_stat_performed:false`.
- `real_archive_candidate_path_hash_performed:false`.
- `real_archive_opened:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_real_archive_candidate_filesystem_permission_added_by_l24_1:true`.

Next patch: L24.2 Microsoft Edge real downloaded-archive candidate path string preflight gate.
