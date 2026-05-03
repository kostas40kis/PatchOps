# L20.2 Microsoft Edge downloaded-file filesystem validation CLI/readback checkpoint

L20.2 adds a passive CLI/readback checkpoint over the accepted L20.1 filesystem validation passive preflight gate.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-cli-readback-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-passive-preflight-gate
```

Authorization token used by the source L20.1 readback:

```text
PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L20.2.
- downloaded-file filesystem validation CLI/readback checkpoint.
- passive CLI/readback checkpoint.
- L20.1 passive preflight gate remains accepted.
- default compact readback remains passive.
- authorized compact readback remains passive.
- filesystem validation preflight authorization remains readback-only.
- filesystem validation execution allowed: false.
- filesystem validation active: false.
- filesystem validation is not performed.
- real filesystem validation remains inactive.
- real file existence check remains inactive.
- real file stat remains inactive.
- real file hash remains inactive.
- downloaded file existence check is not performed.
- downloaded file stat is not performed.
- downloaded file hash is not performed.
- downloaded file bytes are not read.
- downloaded archive is not opened.
- downloaded archive contents are not listed.
- downloaded archive is not extracted.
- downloaded manifest is not read.
- download workflow remains inactive.
- real browser download remains inactive.
- pasteback remains inactive.
- package-run from browser remains inactive.
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
- no click/download/file-read/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Validation style

L20.2 should avoid nested CLI validation cascades.

The L20.2 readback proves both accepted L20.1 source branches through direct module readback:

1. default compact readback remains passive and has filesystem validation preflight authorization false.
2. authorized compact readback remains passive and has filesystem validation preflight authorization true.

The direct-manifest validation should run one shallow L20.2 compact CLI smoke, not a long nested CLI chain.

One shallow L20.2 compact CLI smoke is enough for this checkpoint.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-cli-readback-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The readback should confirm:

- `ok:true`.
- `patch:"L20.2"`.
- `l20_1_passive_preflight_gate_accepted:true`.
- `l20_1_default_compact_readback_ok:true`.
- `l20_1_authorized_compact_readback_ok:true`.
- `default_filesystem_validation_preflight_authorized:false`.
- `authorized_filesystem_validation_preflight_authorized:true`.
- `filesystem_validation_preflight_authorization_remains_readback_only:true`.
- `filesystem_validation_execution_allowed:false`.
- `filesystem_validation_active:false`.
- `filesystem_validation_performed:false`.
- `real_filesystem_validation_active:false`.
- `real_file_exists_check_performed:false`.
- `real_file_stat_performed:false`.
- `real_file_hash_performed:false`.
- `downloaded_file_exists_check_performed:false`.
- `downloaded_file_stat_performed:false`.
- `downloaded_file_hash_performed:false`.
- `downloaded_file_bytes_read:false`.
- `downloaded_archive_opened:false`.
- `downloaded_archive_contents_listed:false`.
- `downloaded_archive_extracted:false`.
- `downloaded_manifest_read:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.
- `avoid_nested_cli_validation_cascades:true`.
- `one_shallow_l20_2_compact_cli_smoke:true`.

## Next patch

L20.3 Microsoft Edge downloaded-file filesystem validation passive plan checkpoint.
