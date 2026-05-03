# L25.3 Microsoft Edge controlled runtime archive-open broad checkpoint

L25.3 follows accepted L25.2 and acts as a broad checkpoint over the archive-open ladder.

Accepted L25 archive-open ladder so far:

- L25.1/L25.1a archive-open authorization gate.
- L25.2 first controlled empty ZIP open/close proof.

Allowed in L25.3:

- read back accepted L25.2 default passive path;
- read back accepted L25.2 authorized open/close proof;
- confirm the controlled empty ZIP fixture was opened and closed;
- confirm the accepted scope is open/close only;
- confirm archive listing, member-count read, member-name read, extraction, member-byte read, manifest payload read, browser, pasteback, and package-run remain inactive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime empty ZIP fixture is the only archive path used by this checkpoint.
- Archive open remains open/close only.
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

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.3"`.
- `broad_checkpoint:true`.
- `archive_open_ladder_checkpoint:true`.
- `l25_archive_open_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l25_02_default_summary.archive_opened:false`.
- `source_l25_02_authorized_summary.archive_opened:true`.
- `source_l25_02_authorized_summary.archive_open_closed:true`.
- `accepted_archive_open_scope:"controlled_runtime_empty_zip_open_close_only_no_listing_no_member_read"`.
- `real_archive_candidate_opened:true`.
- `archive_open_closed:true`.
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
- `no_archive_listing_or_extraction_added_by_l25_3:true`.

Next patch: L25.4 Microsoft Edge controlled runtime archive listing authorization gate.
