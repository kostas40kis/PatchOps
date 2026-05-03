# L21.6 Microsoft Edge downloaded-archive validation broad checkpoint

L21.6 is the broad checkpoint for the Microsoft Edge downloaded-archive validation stream.

Command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-broad-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-metadata-proof
```

L21.5 archive metadata proof authorization token:

```text
PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_METADATA_PROOF_AUTHORIZED
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L21.6.
- downloaded-archive validation broad checkpoint.
- broad archive validation checkpoint.
- L21.1 through L21.5 remain accepted.
- archive metadata-only validation proof remains accepted.
- default archive metadata proof readback remains passive.
- authorized archive metadata proof readback remains metadata-only.
- unsafe archive candidate remains rejected without archive access.
- only the synthetic PatchOps runtime archive metadata listing is allowed.
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

## What L21.6 proves

L21.6 consolidates:

1. L21.1 archive validation passive preflight gate.
2. L21.2 archive validation CLI/readback checkpoint.
3. L21.3 archive validation passive plan checkpoint.
4. L21.4 archive validation controlled authorization gate.
5. L21.5 first controlled archive metadata-only proof.

The successful archive operation allowed by the L21 stream so far is metadata listing for the synthetic archive fixture:

```text
data/runtime/browser_downloads/patch_l21_05_synthetic_archive_patchops_bundle.zip
```

The listing may detect entry names, including whether a `manifest.json` entry exists, but L21.6 does not permit reading manifest contents or any archive member bytes.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-validation-broad-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The readback should confirm:

- `ok:true`.
- `patch:"L21.6"`.
- `l21_1_through_l21_5_remain_accepted:true`.
- `archive_metadata_only_validation_proof_remains_accepted:true`.
- `default_archive_metadata_proof_readback_remains_passive:true`.
- `authorized_archive_metadata_proof_readback_remains_metadata_only:true`.
- `unsafe_archive_candidate_remains_rejected_without_archive_access:true`.
- `only_synthetic_patchops_runtime_archive_metadata_listing_is_allowed:true`.
- `archive_validation_scope:"metadata_listing_only_synthetic_patchops_runtime_archive_fixture"`.
- `archive_validation_performed:true`.
- `downloaded_archive_opened:true`.
- `downloaded_archive_contents_listed:true`.
- `downloaded_archive_extracted:false`.
- `downloaded_manifest_read:false`.
- `archive_member_bytes_read:false`.
- `downloaded_file_bytes_read:false`.
- `downloaded_file_stat_performed:false`.
- `downloaded_file_hash_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L21.7 Microsoft Edge downloaded-archive validation final acceptance marker.
