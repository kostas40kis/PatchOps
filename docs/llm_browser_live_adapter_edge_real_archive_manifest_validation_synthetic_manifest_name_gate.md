# L23.5 Microsoft Edge real downloaded-archive manifest validation synthetic manifest-name proof gate

L23.5 follows accepted L23.4/L23.4b and selects the synthetic manifest entry by name only.

Allowed in L23.5:

- read back accepted L23.4 metadata-only synthetic archive listing;
- confirm the listed member names are exactly `manifest.json` and `README.txt`;
- select `manifest.json` as a metadata name only;
- expose the next gate for synthetic manifest payload authorization.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- `manifest.json` may be selected as a name only.
- `manifest.json` contents are not read.
- Member payload bytes are not read.
- No archive extraction.
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
- No real downloaded archive open.
- No real downloaded archive listing.
- No real archive manifest read.
- No click/download/real-archive-open/archive-extract/member-byte-read/manifest-payload-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L23.5 token:

```text
PATCHOPS_L23_EDGE_SYNTHETIC_MANIFEST_NAME_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L23.5"`.
- `source_l23_04_summary.ok:true`.
- `source_l23_04_summary.synthetic_archive_member_names:["manifest.json","README.txt"]`.
- `synthetic_manifest_name_selected:true`.
- `synthetic_manifest_selected_name:"manifest.json"`.
- `synthetic_manifest_name_selection_scope:"metadata_member_name_only_no_payload_read"`.
- `manifest_name_only:true`.
- `archive_member_bytes_read:false`.
- `archive_member_payload_read:false`.
- `manifest_member_payload_read:false`.
- `archive_extracted:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_new_payload_read_permission_added_by_l23_5:true`.

Next patch: L23.6 Microsoft Edge real downloaded-archive manifest validation synthetic manifest payload authorization gate.
