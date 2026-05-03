# L23.4 Microsoft Edge real downloaded-archive manifest validation first synthetic-archive listing proof

L23.4 follows accepted L23.3 and performs the first synthetic archive listing proof.

L23.4a repaired the ZIP local-header fixture builder used by the direct patch script. L23.4b repairs the synthetic fixture generation path again by refreshing the fixed synthetic archive fixture with Python's ZIP writer during validator setup before the metadata-only listing proof. The safety scope is unchanged.

Allowed in L23.4:

- read back accepted L23.3 listing authorization;
- refresh only the fixed synthetic archive fixture during validator setup;
- open only the fixed synthetic archive fixture;
- list central-directory member names only;
- confirm `manifest.json` is present by name only.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The fixed synthetic archive fixture is the only archive that may be opened.
- Listing is metadata-only.
- Member names may be read.
- Member payload bytes are not read.
- `manifest.json` may be observed as a name only.
- `manifest.json` contents are not read.
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
- No click/download/real-archive-open/archive-extract/member-byte-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L23.4 token:

```text
PATCHOPS_L23_EDGE_FIRST_SYNTHETIC_ARCHIVE_LISTING_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L23.4"`.
- `repair_patch:"L23.4a"`.
- validator readback includes `repair_patch:"L23.4b"`.
- `source_l23_03_summary.future_listing_authorized:true`.
- `synthetic_archive_listing_execution_allowed:true`.
- `synthetic_archive_opened:true`.
- `synthetic_archive_contents_listed:true`.
- `synthetic_archive_member_names:["manifest.json","README.txt"]`.
- `manifest_member_name_seen:true`.
- `downloaded_archive_opened:false`.
- `downloaded_archive_contents_listed:false`.
- `archive_member_bytes_read:false`.
- `archive_member_payload_read:false`.
- `manifest_member_payload_read:false`.
- `archive_extracted:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.

Next patch: L23.5 Microsoft Edge real downloaded-archive manifest validation synthetic manifest-name proof gate.
