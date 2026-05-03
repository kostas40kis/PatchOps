# L25.9 Microsoft Edge controlled runtime archive member-byte-read broad checkpoint

L25.9 follows accepted L25.8 and acts as a broad checkpoint over the archive member-byte-read ladder.

Accepted L25 member-byte-read ladder so far:

- L25.7 archive member-byte-read authorization gate.
- L25.8 first controlled non-manifest member-byte-read proof.

Allowed in L25.9:

- read back accepted L25.8 default passive path;
- read back accepted L25.8 authorized non-manifest member-byte-read proof;
- confirm the only accepted member payload read is `bundle/run_with_patchops.ps1`;
- confirm byte count and SHA-256 were recorded for that non-manifest member payload;
- confirm the accepted scope is non-manifest member bytes only;
- confirm manifest payload read, extraction, browser, pasteback, and package-run remain inactive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime ZIP fixture is the only archive path used by this checkpoint.
- Archive member-byte read remains limited to the synthetic non-manifest member `bundle/run_with_patchops.ps1`.
- The manifest member `bundle/manifest.json` is not read.
- Manifest payload is not read.
- Real archive manifest is not read.
- Candidate archive is not extracted.
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
- No click/download/archive-extract/manifest-payload-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.9"`.
- `broad_checkpoint:true`.
- `archive_member_byte_read_ladder_checkpoint:true`.
- `l25_archive_member_byte_read_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l25_08_default_summary.archive_member_bytes_read:false`.
- `source_l25_08_authorized_summary.archive_member_bytes_read:true`.
- `source_l25_08_authorized_summary.archive_member_payload_read:true`.
- `source_l25_08_authorized_summary.archive_member_payload_bytes_read:true`.
- `source_l25_08_authorized_summary.archive_member_payload_sha256_read:true`.
- `source_l25_08_authorized_summary.archive_member_name_read:"bundle/run_with_patchops.ps1"`.
- `accepted_member_read_scope:"controlled_runtime_non_manifest_member_bytes_only_no_manifest_payload"`.
- `accepted_manifest_member_not_read:true`.
- `manifest_payload_read:false`.
- `real_archive_manifest_read:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_manifest_payload_read_added_by_l25_9:true`.

Next patch: L25.10 Microsoft Edge controlled runtime archive manifest payload-read authorization gate.
