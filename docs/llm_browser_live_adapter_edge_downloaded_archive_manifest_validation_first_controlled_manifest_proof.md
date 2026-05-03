# L22.5 Microsoft Edge first controlled downloaded-archive manifest validation proof

L22.5 performs the first controlled manifest validation proof after accepted L22.4/L22.4a.

This patch reads only this explicit synthetic PatchOps runtime manifest fixture:

```text
data/runtime/browser_downloads/patch_l22_05_synthetic_downloaded_archive_manifest_fixture/manifest.json
```

It validates only a small manifest-shape subset:

- `manifest_version` is `"1"`.
- `patch_name` is `"l22_05_synthetic_manifest_fixture"`.
- `active_profile` is `"generic_python"`.
- `files_to_write` is a list.
- `validation_commands` is a list.
- the fixture declares `synthetic_fixture:true` and `read_only_fixture:true`.
- the fixture declares `package_run_allowed:false`.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- L22.4/L22.4a authorization remains accepted.
- L22.5 requires a separate proof token.
- Default readback is passive and does not read the synthetic manifest fixture.
- Authorized readback reads only the explicit synthetic manifest fixture.
- Manifest validation execution is limited to this synthetic fixture proof only.
- Manifest validation active is true only during the authorized synthetic fixture proof.
- Download workflow remains inactive.
- Real browser download remains inactive.
- No browser activity.
- ChatGPT URL may be selected but not opened.
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

L22.5 proof token:

```text
PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_SYNTHETIC_MANIFEST_VALIDATION_PROOF_AUTHORIZED
```

Expected authorized compact JSON fields:

- `ok:true`.
- `patch:"L22.5"`.
- `manifest_validation_execution_allowed:true`.
- `manifest_validation_performed:true`.
- `downloaded_manifest_read:true`.
- `synthetic_manifest_fixture_read:true`.
- `manifest_validation_scope:"synthetic_patchops_runtime_manifest_fixture_only"`.
- `manifest_validation_result:true`.
- `archive_extracted:false`.
- `archive_member_bytes_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.

Next patch: L22.6 Microsoft Edge downloaded-archive manifest validation broad checkpoint.
