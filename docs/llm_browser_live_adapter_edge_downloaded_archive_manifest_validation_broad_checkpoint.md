# L22.6 Microsoft Edge downloaded-archive manifest validation broad checkpoint

L22.6 is the broad checkpoint after accepted L22.3b, L22.4/L22.4a, and L22.5.

L22.6a repairs the broad checkpoint by normalizing older accepted readback payloads. Missing optional safety fields are not treated as unsafe. Explicit `true` values for forbidden side-effect fields still fail the checkpoint.

It aggregates these accepted surfaces:

- L22.3b passive plan launcher-direct checkpoint.
- L22.4/L22.4a controlled authorization gate and validator import repair.
- L22.5 first controlled synthetic manifest fixture validation proof.

Allowed in L22.6:

- read back accepted Python safety payloads;
- invoke the accepted L22.5 synthetic manifest fixture proof;
- confirm the default L22.5 path does not read the synthetic fixture;
- confirm the authorized L22.5 path reads only the explicit synthetic fixture;
- confirm all real browser/download/archive/package-run boundaries remain closed.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- Synthetic manifest fixture validation from L22.5 remains allowed.
- Real downloaded manifest read remains false.
- Real archive manifest read remains false.
- Download workflow remains inactive.
- Real browser download remains inactive.
- No browser activity.
- No Microsoft Edge start.
- No Selenium import.
- No CDP use.
- No DOM scraping.
- No page inspection.
- No prompt text extraction.
- No conversation reading.
- No real artifact content reading.
- No archive open.
- No archive extraction.
- No archive member-byte read.
- No downloaded file stat.
- No downloaded file hash.
- No click/download/archive-extract/member-byte-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L22.6"`.
- `repair_patch:"L22.6a"`.
- `broad_checkpoint:true`.
- `failed_checks:[]`.
- `l22_03b_summary.ok:true`.
- `l22_04_authorized_summary.manifest_validation_authorization_granted_for_future_patch:true`.
- `l22_05_default_summary.downloaded_manifest_read:false`.
- `l22_05_authorized_summary.synthetic_manifest_fixture_read:true`.
- `manifest_validation_scope:"synthetic_patchops_runtime_manifest_fixture_only"`.
- `manifest_validation_result:true`.
- `real_downloaded_manifest_read:false`.
- `real_archive_manifest_read:false`.
- `archive_extracted:false`.
- `archive_member_bytes_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.

Next patch: L22.7 Microsoft Edge downloaded-archive manifest validation final acceptance marker.
