# L23.7 Microsoft Edge real downloaded-archive manifest validation first synthetic manifest payload proof

L23.7 follows accepted L23.6 and performs the first synthetic manifest payload proof.

Allowed in L23.7:

- read back accepted L23.6 payload authorization;
- refresh only the fixed synthetic archive fixture during validator setup;
- open only the fixed synthetic archive fixture;
- read only the `manifest.json` member payload from that synthetic fixture;
- parse the tiny synthetic manifest JSON;
- validate its minimal shape.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The fixed synthetic archive fixture is the only archive that may be opened.
- Only `manifest.json` payload may be read.
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

L23.7 token:

```text
PATCHOPS_L23_EDGE_FIRST_SYNTHETIC_MANIFEST_PAYLOAD_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L23.7"`.
- `source_l23_06_summary.ok:true`.
- `source_l23_06_summary.future_payload_authorized:true`.
- `synthetic_manifest_payload_read_execution_allowed:true`.
- `synthetic_manifest_payload_read_performed:true`.
- `synthetic_manifest_member_name:"manifest.json"`.
- `synthetic_manifest_json_parsed:true`.
- `synthetic_manifest_shape_validated:true`.
- `synthetic_manifest_patch_name:"l23_07_synthetic_manifest_payload_fixture"`.
- `synthetic_manifest_scope:"fixed_synthetic_archive_manifest_payload_only"`.
- `manifest_member_bytes_read:true`.
- `manifest_member_payload_read:true`.
- `non_manifest_member_bytes_read:false`.
- `readme_member_payload_read:false`.
- `archive_extracted:false`.
- `real_archive_manifest_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_real_archive_permission_added_by_l23_7:true`.

Next patch: L23.8 Microsoft Edge real downloaded-archive manifest validation synthetic payload broad checkpoint.
