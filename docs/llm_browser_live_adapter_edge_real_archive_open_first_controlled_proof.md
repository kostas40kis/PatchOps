# L25.2 Microsoft Edge controlled runtime archive-open first proof

L25.2 follows accepted L25.1a and performs the first controlled archive-open proof.

Allowed in L25.2:

- read back accepted L25.1a archive-open authorization;
- create a controlled empty ZIP fixture during validator setup;
- import Python's archive-opening module only for this proof;
- open and close the controlled empty ZIP fixture after explicit token authorization;
- keep archive listing, extraction, member-name read, member-byte read, manifest payload read, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime empty ZIP fixture is the only archive path used by this proof.
- Archive open is allowed only with explicit flag and token.
- Archive open is open/close only.
- Candidate archive is opened as an archive only in L25.2 authorized proof mode.
- Candidate archive is not listed.
- Candidate archive member names are not read.
- Candidate archive member count is not read.
- Candidate archive is not extracted.
- Archive member bytes are not read.
- Real archive manifest is not read.
- Manifest payload is not read.
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
- No click/download/archive-list/archive-extract/archive-member-byte-read/manifest-payload-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L25.2 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_OPEN_FIRST_CONTROLLED_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.2"`.
- `source_l25_01_summary.ok:true`.
- `source_l25_01_summary.repair_patch:"L25.1a"`.
- `source_l25_01_summary.future_archive_open_authorized:true`.
- default passive readback has `real_archive_candidate_opened:false`.
- authorized readback has `real_archive_candidate_open_allowed:true`.
- authorized readback has `real_archive_candidate_opened:true`.
- authorized readback has `archive_open_closed:true`.
- `archive_open_scope:"controlled_runtime_empty_zip_open_close_only_no_listing_no_member_read"`.
- `real_archive_candidate_listed:false`.
- `real_archive_candidate_member_count_read:false`.
- `real_archive_candidate_member_names_read:false`.
- `real_archive_candidate_extracted:false`.
- `archive_member_bytes_read:false`.
- `manifest_payload_read:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_archive_listing_or_extraction_added_by_l25_2:true`.

Next patch: L25.3 Microsoft Edge controlled runtime archive-open broad checkpoint.
