# L25.5 Microsoft Edge controlled runtime archive listing first proof

L25.5 follows accepted L25.4 and performs the first controlled archive-listing proof.

Allowed in L25.5:

- read back accepted L25.4 archive-listing authorization;
- create a controlled ZIP fixture during validator setup;
- open the controlled ZIP fixture after explicit token authorization;
- list only member names and member count;
- keep extraction, member-byte read, manifest payload read, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime ZIP fixture is the only archive path used by this proof.
- Archive listing is allowed only with explicit flag and token.
- Candidate archive is listed only for member names and member count.
- Candidate archive member names are read.
- Candidate archive member count is read.
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
- No click/download/archive-extract/archive-member-byte-read/manifest-payload-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L25.5 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_LISTING_FIRST_CONTROLLED_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.5"`.
- `source_l25_04_summary.ok:true`.
- `source_l25_04_summary.future_listing_authorized:true`.
- default passive readback has `real_archive_candidate_listed:false`.
- authorized readback has `real_archive_candidate_listing_allowed:true`.
- authorized readback has `real_archive_candidate_listed:true`.
- authorized readback has `real_archive_candidate_member_count_read:true`.
- authorized readback has `real_archive_candidate_member_count:2`.
- authorized readback has `real_archive_candidate_member_names_read:true`.
- authorized readback has `real_archive_candidate_member_names:["bundle/manifest.json","bundle/run_with_patchops.ps1"]`.
- `archive_listing_scope:"controlled_runtime_zip_member_names_and_count_only_no_member_bytes"`.
- `real_archive_candidate_extracted:false`.
- `archive_member_bytes_read:false`.
- `manifest_payload_read:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_archive_extraction_added_by_l25_5:true`.

Next patch: L25.6 Microsoft Edge controlled runtime archive listing broad checkpoint.
