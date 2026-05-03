# L25.7 Microsoft Edge controlled runtime archive member-byte-read authorization gate

L25.7 follows accepted L25.6 and adds only a future authorization/readback gate for archive member-byte reads.

It does not read archive member bytes yet.

Allowed in L25.7:

- read back accepted L25.6 controlled archive-listing broad checkpoint;
- confirm member names/count listing is accepted;
- confirm member-byte reads and manifest payload reads remain inactive;
- expose a future archive member-byte-read authorization token;
- keep member-byte read execution, member payload read, manifest payload read, extraction, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Archive member-byte-read authorization is readback-only.
- Archive member-byte-read execution is not allowed in L25.7.
- Candidate archive may be listed only by accepted L25.6 source readback; L25.7 adds no new listing scope.
- Candidate archive member names/count may be read only by accepted L25.6 source readback.
- Candidate archive member bytes are not read.
- Candidate archive member payload is not read.
- Candidate archive is not extracted.
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
- No click/download/archive-extract/archive-member-byte-read/member-payload-read/manifest-payload-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L25.7 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MEMBER_BYTE_READ_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.7"`.
- `source_l25_06_summary.ok:true`.
- `source_l25_06_summary.broad_checkpoint:true`.
- `source_l25_06_summary.archive_listing_ladder_complete:true`.
- `source_l25_06_summary.archive_listed:true`.
- `source_l25_06_summary.archive_member_count_read:true`.
- `source_l25_06_summary.archive_member_names_read:true`.
- `source_l25_06_summary.archive_member_bytes_read:false`.
- `archive_member_byte_read_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `archive_member_byte_read_authorization_readback_only:true`.
- `archive_member_byte_read_allowed:false`.
- `archive_member_bytes_read:false`.
- `archive_member_payload_read:false`.
- `manifest_payload_read:false`.
- `real_archive_manifest_read:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_archive_member_byte_read_execution_added_by_l25_7:true`.

Next patch: L25.8 Microsoft Edge controlled runtime archive member-byte-read first proof.
