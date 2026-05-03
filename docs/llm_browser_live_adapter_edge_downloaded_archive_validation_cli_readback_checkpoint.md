# L21.2 Microsoft Edge downloaded-archive validation CLI/readback checkpoint

L21.2 adds a passive CLI/readback checkpoint over the accepted L21.1 downloaded-archive validation passive preflight gate.

Command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-cli-readback-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-passive-preflight-gate
```

L21.1 preflight authorization token:

```text
PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L21.2.
- downloaded-archive validation CLI/readback checkpoint.
- passive CLI/readback checkpoint.
- L21.1 passive preflight gate remains accepted.
- default archive preflight readback remains passive.
- authorized archive preflight readback remains passive.
- archive validation preflight authorization remains readback-only.
- archive validation execution allowed: false.
- archive validation active: false.
- archive validation is not performed.
- downloaded archive is not opened.
- downloaded archive contents are not listed.
- downloaded archive is not extracted.
- downloaded manifest is not read.
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

## Validation style

L21.2 should avoid nested CLI validation cascades.

The L21.2 readback proves both accepted L21.1 source branches through direct module readback:

1. default archive preflight readback remains passive and has archive preflight authorization false.
2. authorized archive preflight readback remains passive and has archive preflight authorization true.

The direct-manifest validation should run one shallow L21.2 compact CLI smoke, not a long nested CLI chain.

One shallow L21.2 compact CLI smoke is enough for this checkpoint.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-validation-cli-readback-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The readback should confirm:

- `ok:true`.
- `patch:"L21.2"`.
- `l21_1_passive_preflight_gate_accepted:true`.
- `l21_1_default_archive_preflight_readback_ok:true`.
- `l21_1_authorized_archive_preflight_readback_ok:true`.
- `default_archive_validation_preflight_authorized:false`.
- `authorized_archive_validation_preflight_authorized:true`.
- `archive_validation_preflight_authorization_remains_readback_only:true`.
- `archive_validation_execution_allowed:false`.
- `archive_validation_active:false`.
- `archive_validation_performed:false`.
- `downloaded_archive_opened:false`.
- `downloaded_archive_contents_listed:false`.
- `downloaded_archive_extracted:false`.
- `downloaded_manifest_read:false`.
- `downloaded_file_bytes_read:false`.
- `downloaded_file_stat_performed:false`.
- `downloaded_file_hash_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.
- `avoid_nested_cli_validation_cascades:true`.
- `one_shallow_l21_2_compact_cli_smoke:true`.

## Next patch

L21.3 Microsoft Edge downloaded-archive validation passive plan checkpoint.
