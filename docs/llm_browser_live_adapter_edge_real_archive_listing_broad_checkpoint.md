# L25.6 Microsoft Edge controlled runtime archive listing broad checkpoint

L25.6 follows accepted L25.5 and acts as a broad checkpoint over the archive-listing ladder.

Accepted L25 archive-listing ladder so far:

- L25.4 archive listing authorization gate.
- L25.5 first controlled member-name/member-count listing proof.

Allowed in L25.6:

- read back accepted L25.5 default passive path;
- read back accepted L25.5 authorized member-name/member-count listing proof;
- confirm the controlled ZIP fixture member names are exactly `bundle/manifest.json` and `bundle/run_with_patchops.ps1`;
- confirm the accepted scope is member names/count only;
- confirm extraction, member-byte read, member payload read, manifest payload read, browser, pasteback, and package-run remain inactive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime ZIP fixture is the only archive path used by this checkpoint.
- Archive listing remains member names/count only.
- Candidate archive member names are read.
- Candidate archive member count is read.
- Candidate archive is not extracted.
- Archive member bytes are not read.
- Archive member payload is not read.
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

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.6"`.
- `broad_checkpoint:true`.
- `archive_listing_ladder_checkpoint:true`.
- `l25_archive_listing_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l25_05_default_summary.archive_listed:false`.
- `source_l25_05_authorized_summary.archive_listed:true`.
- `source_l25_05_authorized_summary.archive_member_count_read:true`.
- `source_l25_05_authorized_summary.archive_member_count:2`.
- `source_l25_05_authorized_summary.archive_member_names_read:true`.
- `source_l25_05_authorized_summary.archive_member_names:["bundle/manifest.json","bundle/run_with_patchops.ps1"]`.
- `accepted_archive_listing_scope:"controlled_runtime_zip_member_names_and_count_only_no_member_bytes"`.
- `real_archive_candidate_listed:true`.
- `real_archive_candidate_member_count_read:true`.
- `real_archive_candidate_member_names_read:true`.
- `real_archive_candidate_extracted:false`.
- `archive_member_bytes_read:false`.
- `archive_member_payload_read:false`.
- `manifest_payload_read:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_archive_member_or_manifest_payload_read_added_by_l25_6:true`.

Next patch: L25.7 Microsoft Edge controlled runtime archive member-byte-read authorization gate.
