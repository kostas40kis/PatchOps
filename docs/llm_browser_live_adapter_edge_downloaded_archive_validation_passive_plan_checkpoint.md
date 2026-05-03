# L21.3 Microsoft Edge downloaded-archive validation passive plan checkpoint

L21.3 defines the safe future archive validation plan after the accepted L21.2 CLI/readback checkpoint.

Command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-passive-plan-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-cli-readback-checkpoint
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L21.3.
- downloaded-archive validation passive plan checkpoint.
- safe future archive validation plan.
- L21.2 CLI/readback checkpoint remains accepted.
- archive candidate path remains metadata-only in L21.3.
- archive validation plan does not open a downloaded archive.
- archive validation plan does not list downloaded archive contents.
- archive validation plan does not extract a downloaded archive.
- archive validation plan does not read a downloaded manifest.
- archive validation plan does not read downloaded file bytes.
- archive validation plan does not stat a downloaded file.
- archive validation plan does not hash a downloaded file.
- archive validation plan does not run a package.
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
- no click/download/stat/hash/archive-open/archive-list/archive-extract/manifest/byte-read/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Future archive validation plan

The plan is metadata-only in L21.3:

1. Confirm the L21.2 CLI/readback checkpoint remains accepted.
2. Require a future L21.4 archive validation authorization token.
3. Accept future archive candidate paths as metadata only.
4. In a later phase only, open the archive without extracting.
5. In a later phase only, list archive names without reading payload bytes.
6. In separate future streams only, read manifests or file bytes.
7. Keep package-run, pasteback, and auto-send blocked.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-validation-passive-plan-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

- `ok:true`.
- `patch:"L21.3"`.
- `source_l21_2_cli_readback_checkpoint_accepted:true`.
- `l21_2_complete:true`.
- `l21_1_passive_preflight_gate_accepted:true`.
- `archive_candidate_definition_blocks_l21_3_archive_execution:true`.
- `future_archive_validation_plan_is_planned_not_executed:true`.
- `future_archive_validation_plan_blocks_archive_execution:true`.
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

## Next patch

L21.4 Microsoft Edge downloaded-archive validation controlled authorization gate.
