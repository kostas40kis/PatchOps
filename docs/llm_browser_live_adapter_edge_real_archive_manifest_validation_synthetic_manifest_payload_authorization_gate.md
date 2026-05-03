# L23.6 Microsoft Edge real downloaded-archive manifest validation synthetic manifest payload authorization gate

L23.6 follows accepted L23.5 and adds only a future authorization/readback gate for synthetic manifest payload reading.

It does not read manifest contents yet.

Allowed in L23.6:

- read back accepted L23.5 manifest-name proof;
- confirm `manifest.json` was selected by metadata name only;
- expose a future synthetic manifest payload authorization token;
- keep payload read execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Payload authorization is readback-only.
- Synthetic manifest payload read execution allowed remains false.
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

L23.6 token:

```text
PATCHOPS_L23_EDGE_SYNTHETIC_MANIFEST_PAYLOAD_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L23.6"`.
- `source_l23_05_summary.ok:true`.
- `source_l23_05_summary.selected_name:"manifest.json"`.
- `synthetic_manifest_payload_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `synthetic_manifest_payload_read_execution_allowed:false`.
- `synthetic_manifest_payload_read_performed:false`.
- `synthetic_manifest_json_parsed:false`.
- `manifest_member_payload_read:false`.
- `archive_member_bytes_read:false`.
- `archive_member_payload_read:false`.
- `archive_extracted:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_new_payload_read_permission_added_by_l23_6:true`.

Next patch: L23.7 Microsoft Edge real downloaded-archive manifest validation first synthetic manifest payload proof.
