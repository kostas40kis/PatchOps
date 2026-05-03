# L22.1b Microsoft Edge downloaded-archive manifest validation passive preflight stabilized repair

Command:

```text
browser-start-supervised-launch-edge-downloaded-archive-manifest-validation-passive-preflight-gate-stabilized
```

Authorization token:

```text
PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- manifest validation passive preflight is readback-only.
- L21.7a was already accepted by report evidence as the downloaded-archive validation final marker repair.
- L21 completion means metadata-only synthetic archive listing.
- manifest validation execution allowed: false.
- manifest validation active: false.
- manifest validation is not performed.
- downloaded manifest is not read.
- archive member bytes are not read.
- downloaded archive is not extracted.
- downloaded archive is not opened by L22.1b.
- downloaded archive contents are not listed by L22.1b.
- downloaded file bytes are not read.
- downloaded file stat is not performed.
- downloaded file hash is not performed.
- package-run from browser remains inactive.
- pasteback remains inactive.
- download workflow remains inactive.
- real browser download remains inactive.
- PatchOps remains source of truth.
- target URL allowlist remains enforced.
- ChatGPT URL may be selected but not opened.
- dedicated Microsoft Edge runtime profile remains required for future live phases.
- never use the default Microsoft Edge profile.
- no Microsoft Edge start.
- no Selenium import.
- no CDP use.
- no DOM scraping.
- no prompt text extraction.
- no conversation reading.
- no artifact content reading.
- no click/download/stat/hash/archive-open/archive-list/archive-extract/manifest/byte-read/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Stabilization reason

L22.1 and L22.1a failed during apply with a target-content failure while the report did not expose the exact inner validation command. L22.1b deliberately avoids brittle source-command and regression assumptions and proves only the new manifest-validation preflight readback surface.

## Expected readback

The default readback keeps `manifest_validation_preflight_authorized:false`.

The authorized readback keeps `manifest_validation_preflight_authorized:true` while still reporting:

- `manifest_validation_execution_allowed:false`.
- `manifest_validation_active:false`.
- `manifest_validation_performed:false`.
- `downloaded_manifest_read:false`.
- `archive_member_bytes_read:false`.
- `downloaded_archive_opened:false`.
- `downloaded_archive_extracted:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint.
