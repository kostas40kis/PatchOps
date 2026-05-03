# L25.8 Microsoft Edge controlled runtime archive member-byte-read first proof

L25.8 follows accepted L25.7 and performs the first controlled archive member-byte-read proof.

Allowed in L25.8:

- read back accepted L25.7 member-byte-read authorization;
- create a controlled ZIP fixture during validator setup;
- open the controlled ZIP fixture after explicit token authorization;
- read bytes from exactly one controlled non-manifest member: `bundle/run_with_patchops.ps1`;
- compute byte count and SHA-256 for that non-manifest member payload;
- keep manifest payload read, extraction, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime ZIP fixture is the only archive path used by this proof.
- Archive member-byte read is allowed only with explicit flag and token.
- The only member payload read is the synthetic non-manifest member `bundle/run_with_patchops.ps1`.
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

L25.8 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MEMBER_BYTE_READ_FIRST_CONTROLLED_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.8"`.
- `source_l25_07_summary.ok:true`.
- `source_l25_07_summary.future_member_byte_read_authorized:true`.
- default passive readback has `archive_member_bytes_read:false`.
- authorized readback has `archive_member_byte_read_allowed:true`.
- authorized readback has `archive_member_bytes_read:true`.
- authorized readback has `archive_member_payload_read:true`.
- authorized readback has `archive_member_payload_bytes_read:true`.
- authorized readback has `archive_member_payload_sha256_read:true`.
- authorized readback has `archive_member_name_read:"bundle/run_with_patchops.ps1"`.
- `archive_member_read_scope:"controlled_runtime_non_manifest_member_bytes_only_no_manifest_payload"`.
- `manifest_payload_read:false`.
- `real_archive_manifest_read:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_manifest_payload_read_added_by_l25_8:true`.

Next patch: L25.9 Microsoft Edge controlled runtime archive member-byte-read broad checkpoint.
