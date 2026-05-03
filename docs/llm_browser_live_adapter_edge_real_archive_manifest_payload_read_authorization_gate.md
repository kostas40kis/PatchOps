# L25.10 Microsoft Edge controlled runtime archive manifest payload-read authorization gate

L25.10 follows accepted L25.9 and adds only a future authorization/readback gate for archive manifest payload reads.

It does not read the archive manifest payload yet.

Allowed in L25.10:

- read back accepted L25.9 controlled non-manifest member-byte-read broad checkpoint;
- confirm only the non-manifest member `bundle/run_with_patchops.ps1` was read by the source checkpoint;
- confirm the manifest member `bundle/manifest.json` was not read by the source checkpoint;
- confirm manifest payload reads remain inactive;
- expose a future manifest payload-read authorization token;
- keep manifest payload-read execution, extraction, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Archive manifest payload-read authorization is readback-only.
- Archive manifest payload-read execution is not allowed in L25.10.
- Candidate archive non-manifest member bytes may be read only by accepted L25.9 source readback; L25.10 adds no new member-byte-read scope.
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

L25.10 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PAYLOAD_READ_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.10"`.
- `source_l25_09_summary.ok:true`.
- `source_l25_09_summary.broad_checkpoint:true`.
- `source_l25_09_summary.member_byte_read_ladder_complete:true`.
- `source_l25_09_summary.accepted_manifest_member_not_read:true`.
- `source_l25_09_summary.archive_member_name_read:"bundle/run_with_patchops.ps1"`.
- `source_l25_09_summary.manifest_payload_read:false`.
- `archive_manifest_payload_read_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `archive_manifest_payload_read_authorization_readback_only:true`.
- `archive_manifest_payload_read_allowed:false`.
- `manifest_payload_read:false`.
- `manifest_payload_bytes_read:false`.
- `real_archive_manifest_read:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_manifest_payload_read_execution_added_by_l25_10:true`.

Next patch: L25.11 Microsoft Edge controlled runtime archive manifest payload-read first proof.
