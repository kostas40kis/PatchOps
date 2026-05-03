# L21.6a Microsoft Edge downloaded-archive validation broad checkpoint repair

Command: `browser-start-supervised-launch-edge-downloaded-archive-validation-broad-checkpoint-repair`

Source command: `browser-start-supervised-launch-edge-downloaded-archive-validation-metadata-proof`

Token: `PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_METADATA_PROOF_AUTHORIZED`

## Boundary

- Microsoft Edge first.
- Opera second.
- downloaded-archive validation broad checkpoint repair.
- L21.5 metadata-only archive proof remains accepted.
- default archive metadata proof readback remains passive.
- authorized archive metadata proof readback remains metadata-only.
- archive validation remains limited to metadata-only listing of the synthetic fixture.
- downloaded archive may be opened only for metadata listing of the synthetic fixture.
- downloaded archive contents may be listed as metadata only.
- downloaded archive is not extracted.
- downloaded manifest is not read.
- archive member bytes are not read.
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
- no click/download/stat/hash/archive-extract/manifest-read/member-byte-read/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.
- no package-run from browser.

The accepted scope remains metadata-only listing of the synthetic fixture `data/runtime/browser_downloads/patch_l21_05_synthetic_archive_patchops_bundle.zip`. L21.7 Microsoft Edge downloaded-archive validation final acceptance marker is next.
