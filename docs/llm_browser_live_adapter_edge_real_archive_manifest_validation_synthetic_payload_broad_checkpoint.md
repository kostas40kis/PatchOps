# L23.8 Microsoft Edge real downloaded-archive manifest validation synthetic payload broad checkpoint

L23.8 follows accepted L23.7 and acts as a broad checkpoint over the synthetic-only L23 ladder.

It summarizes the accepted ladder:

- L23.1 real downloaded-archive manifest authorization gate.
- L23.2/L23.2a fixed synthetic archive path preflight.
- L23.3 synthetic archive listing authorization gate.
- L23.4/L23.4b first synthetic archive metadata listing proof.
- L23.5 synthetic manifest-name proof gate.
- L23.6 synthetic manifest payload authorization gate.
- L23.7 first synthetic manifest payload proof.

Allowed in L23.8:

- read back accepted L23.7 default passive path;
- read back accepted L23.7 authorized synthetic payload proof;
- confirm only `manifest.json` from the fixed synthetic archive fixture was read;
- confirm the tiny synthetic manifest JSON was parsed and shape-validated;
- confirm non-manifest members, real archives, browser, pasteback, and package-run remain inactive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The fixed synthetic archive fixture is the only archive that may be opened by this checkpoint.
- Only `manifest.json` payload from that fixed synthetic fixture may be read.
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
- `patch:"L23.8"`.
- `broad_checkpoint:true`.
- `synthetic_payload_ladder_checkpoint:true`.
- `l23_synthetic_payload_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l23_07_default_summary.payload_read_performed:false`.
- `source_l23_07_authorized_summary.payload_read_performed:true`.
- `source_l23_07_authorized_summary.manifest_member_name:"manifest.json"`.
- `source_l23_07_authorized_summary.synthetic_manifest_json_parsed:true`.
- `source_l23_07_authorized_summary.synthetic_manifest_shape_validated:true`.
- `accepted_synthetic_payload_scope:"fixed_synthetic_archive_manifest_payload_only"`.
- `accepted_synthetic_manifest_patch_name:"l23_07_synthetic_manifest_payload_fixture"`.
- `manifest_member_payload_read:true`.
- `non_manifest_member_bytes_read:false`.
- `readme_member_payload_read:false`.
- `archive_extracted:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_real_archive_permission_added_by_l23_8:true`.

Next patch: L23.9 Microsoft Edge real downloaded-archive manifest validation final synthetic acceptance marker.
