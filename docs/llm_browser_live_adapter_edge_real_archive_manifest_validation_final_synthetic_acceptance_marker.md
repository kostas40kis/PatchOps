# L23.9 Microsoft Edge real downloaded-archive manifest validation final synthetic acceptance marker

L23.9 follows accepted L23.8 and finalizes the synthetic-only L23 manifest-validation ladder.

Accepted L23 synthetic ladder:

- L23.1 real downloaded-archive manifest authorization gate.
- L23.2/L23.2a fixed synthetic archive path preflight.
- L23.3 synthetic archive listing authorization gate.
- L23.4/L23.4b first synthetic archive metadata listing proof.
- L23.5 synthetic manifest-name proof gate.
- L23.6 synthetic manifest payload authorization gate.
- L23.7 first synthetic manifest payload proof.
- L23.8 synthetic payload broad checkpoint.

Accepted L23 scope:

- synthetic-only archive preflight;
- synthetic-only archive metadata listing;
- synthetic-only manifest member-name selection;
- synthetic-only `manifest.json` payload read;
- synthetic-only JSON parse and minimal shape validation.

L23.9 does not grant real downloaded archive validation permission.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The fixed synthetic archive fixture remains the only archive that may be used by this stream.
- The only accepted payload read is `manifest.json` from the fixed synthetic archive fixture.
- Non-manifest member payload bytes are not read.
- `README.txt` payload is not read.
- No archive extraction.
- No real candidate archive path stat.
- No real candidate archive path hash.
- No downloaded file bytes read.
- No downloaded file hash.
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
- No real artifact content reading.
- No real downloaded archive open.
- No real downloaded archive listing.
- No real archive manifest read.
- No click/download/real-archive-open/archive-extract/non-manifest-member-byte-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L23.9"`.
- `final_synthetic_acceptance_marker:true`.
- `l23_synthetic_manifest_validation_stream_complete:true`.
- `l23_real_downloaded_archive_permission_granted:false`.
- `failed_checks:[]`.
- `source_l23_08_summary.ok:true`.
- `source_l23_08_summary.ladder_complete:true`.
- `source_l23_08_summary.authorized_payload_read_performed:true`.
- `accepted_synthetic_payload_scope:"fixed_synthetic_archive_manifest_payload_only"`.
- `accepted_manifest_member_name:"manifest.json"`.
- `accepted_synthetic_manifest_patch_name:"l23_07_synthetic_manifest_payload_fixture"`.
- `manifest_member_payload_read:true`.
- `synthetic_manifest_json_parsed:true`.
- `synthetic_manifest_shape_validated:true`.
- `non_manifest_member_bytes_read:false`.
- `readme_member_payload_read:false`.
- `archive_extracted:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_real_archive_permission_added_by_l23_9:true`.

Post-L23 next step must be a separately gated stream. L23 itself adds no permission for real downloaded-archive validation, browser start, pasteback, send/submit, or package-run.
