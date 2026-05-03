# L25.4 Microsoft Edge controlled runtime archive listing authorization gate

L25.4 follows accepted L25.3 and adds only a future authorization/readback gate for archive listing.

It does not list archive members yet.

Allowed in L25.4:

- read back accepted L25.3 controlled empty ZIP open/close broad checkpoint;
- confirm archive open/close is accepted;
- confirm archive listing and member reads remain inactive;
- expose a future archive listing authorization token;
- keep listing execution, member-count read, member-name read, extraction, member-byte read, manifest payload read, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Archive listing authorization is readback-only.
- Archive listing execution is not allowed in L25.4.
- Candidate archive may be opened only by accepted L25.3 source readback; L25.4 adds no new archive-open scope.
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

L25.4 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_LISTING_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.4"`.
- `source_l25_03_summary.ok:true`.
- `source_l25_03_summary.broad_checkpoint:true`.
- `source_l25_03_summary.archive_open_ladder_complete:true`.
- `source_l25_03_summary.archive_opened:true`.
- `source_l25_03_summary.archive_open_closed:true`.
- `source_l25_03_summary.archive_listed:false`.
- `source_l25_03_summary.archive_member_count_read:false`.
- `source_l25_03_summary.archive_member_names_read:false`.
- `archive_listing_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `archive_listing_authorization_readback_only:true`.
- `real_archive_candidate_listing_allowed:false`.
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
- `no_archive_listing_execution_added_by_l25_4:true`.

Next patch: L25.5 Microsoft Edge controlled runtime archive listing first proof.
