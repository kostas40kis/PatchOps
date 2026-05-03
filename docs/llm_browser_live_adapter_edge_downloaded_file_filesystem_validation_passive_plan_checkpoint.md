# L20.3 Microsoft Edge downloaded-file filesystem validation passive plan checkpoint

L20.3 defines the safe future real-filesystem validation plan after the accepted L20.2 CLI/readback checkpoint.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-passive-plan-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-cli-readback-checkpoint
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L20.3.
- downloaded-file filesystem validation passive plan checkpoint.
- passive plan checkpoint.
- L20.2 CLI/readback checkpoint remains accepted.
- safe future real-filesystem validation plan.
- future filesystem validation candidate path must remain metadata-only in L20.3.
- filesystem validation plan does not check whether a file exists.
- filesystem validation plan does not stat a file.
- filesystem validation plan does not hash a file.
- filesystem validation plan does not read downloaded file bytes.
- filesystem validation plan does not open a downloaded archive.
- filesystem validation plan does not list downloaded archive contents.
- filesystem validation plan does not extract a downloaded archive.
- filesystem validation plan does not read a downloaded manifest.
- filesystem validation plan does not run a package.
- filesystem validation execution allowed: false.
- filesystem validation active: false.
- filesystem validation is not performed.
- real filesystem validation remains inactive.
- real file existence check remains inactive.
- real file stat remains inactive.
- real file hash remains inactive.
- archive validation remains inactive.
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

## Future filesystem validation candidate definition

In L20.3, a filesystem validation candidate means metadata-only path evidence for a future downloaded PatchOps zip artifact on disk.

A candidate does not mean:

- checking whether a file exists.
- stating a file.
- hashing a file.
- reading downloaded file bytes.
- opening a downloaded archive.
- listing downloaded archive contents.
- extracting a downloaded archive.
- reading a downloaded manifest.
- running a package.
- pasting into a browser.
- sending or submitting a message.

Future candidate path rules remain:

- extension must be `.zip`.
- recommended pattern is `patch_*_patchops_bundle.zip`.
- path must be metadata-only in L20.3.
- path must not be the default Microsoft Edge profile.
- reject non-zip candidates.
- reject ambiguous multiple candidates.

## Future passive plan

The safe future real-filesystem validation plan is planned but not executed in L20.3:

1. Confirm the L20.2 CLI/readback checkpoint is accepted.
2. Require an L20.4-or-later explicit filesystem validation authorization token.
3. Accept future downloaded-file path metadata only.
4. In a later phase, check file existence without reading file bytes.
5. In a later phase, stat file metadata without opening the archive.
6. Gate hash separately because hashing reads file bytes.
7. Gate archive opening/listing/extraction and manifest read separately.
8. Keep package-run, pasteback, and auto-send blocked.

Filesystem validation remains inactive in L20.3.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-passive-plan-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The readback should confirm:

- `ok:true`.
- `patch:"L20.3"`.
- `source_l20_2_cli_readback_checkpoint_accepted:true`.
- `filesystem_validation_candidate_definition_blocks_l20_3_filesystem_file_read_archive_package_run:true`.
- `future_filesystem_validation_plan_is_planned_not_executed:true`.
- `future_filesystem_validation_plan_blocks_filesystem_file_read_archive_package_run:true`.
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

## Next patch

L20.4 Microsoft Edge downloaded-file filesystem validation controlled authorization gate.
