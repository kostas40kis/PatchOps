# L25.1 Microsoft Edge real downloaded-archive archive-open authorization gate

L25.1 starts a new separately gated post-L24 stream.

L25.1a repairs the validator for this gate: forbidden import detection now inspects Python AST import nodes instead of matching prose, so documentation text cannot cause a false failure.

L24 ended with a final metadata/hash acceptance marker. L24 accepted only controlled runtime candidate metadata/stat and SHA-256 over controlled fixture file bytes. L24 did not grant archive open/list/extract/read, manifest payload read, browser activity, pasteback, send/submit, or package-run permission.

Allowed in L25.1:

- read back accepted L24.9 final metadata/hash marker;
- expose a future archive-open authorization token;
- keep archive open execution disabled;
- keep archive listing, extraction, member-byte read, manifest payload read, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Archive-open authorization is readback-only.
- Archive-open execution is not allowed in L25.1.
- The `zipfile` module is not loaded in L25.1.
- Candidate archive is not opened as an archive.
- Candidate archive is not listed.
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
- No click/download/real-archive-open/archive-list/archive-extract/archive-member-byte-read/manifest-payload-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L25.1 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_OPEN_AUTHORIZED_READBACK_ONLY
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.1"`.
- `repair_patch:"L25.1a"`.
- `source_l24_09_summary.ok:true`.
- `source_l24_09_summary.final_metadata_hash_acceptance_marker:true`.
- `source_l24_09_summary.l24_metadata_hash_complete:true`.
- `source_l24_09_summary.archive_open_permission:false`.
- `archive_open_authorization_granted_for_future_patch:true` when flag and token are supplied.
- `archive_open_authorization_readback_only:true`.
- `real_archive_candidate_open_allowed:false`.
- `real_archive_candidate_opened:false`.
- `real_archive_candidate_listed:false`.
- `real_archive_candidate_extracted:false`.
- `archive_member_bytes_read:false`.
- `manifest_payload_read:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_archive_open_execution_added_by_l25_1:true`.

Next patch: L25.2 Microsoft Edge controlled runtime archive-open first proof.
