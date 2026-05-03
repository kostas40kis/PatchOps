# L22.1a Microsoft Edge downloaded-archive manifest validation passive preflight repair

L22.1a repairs the L22.1 manifest-validation passive preflight by using a less brittle source readback than L22.1.

Command:

```text
browser-start-supervised-launch-edge-downloaded-archive-manifest-validation-passive-preflight-gate-repair
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-final-acceptance-marker-repair
```

Preflight authorization token:

```text
PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L22.1a.
- downloaded-archive manifest validation passive preflight repair.
- manifest validation preflight authorization is readback-only.
- L21.7a archive final marker repair remains accepted.
- L21 completion means metadata-only listing of the synthetic archive fixture.
- manifest validation execution allowed: false.
- manifest validation active: false.
- manifest validation is not performed.
- downloaded manifest is not read.
- downloaded archive is not extracted.
- archive member bytes are not read.
- downloaded archive is not opened for manifest validation.
- downloaded archive contents are not listed for manifest validation.
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
- no click/download/stat/hash/archive-open/archive-list/archive-extract/manifest-read/member-byte-read/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Repair note

The original L22.1 bundle passed package preflight, check, inspect, and plan, but failed during apply. L22.1a keeps the same safety contract but avoids brittle exact-field assertions against the L21.7a source payload.

## CLI commands

Default passive readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-manifest-validation-passive-preflight-gate-repair --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized passive readback, still no manifest validation execution:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-manifest-validation-passive-preflight-gate-repair --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-manifest-validation-preflight --authorization-token PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY --json --compact
```

## Expected compact JSON fields

- `ok:true`.
- `patch:"L22.1a"`.
- `source_l21_7a_archive_final_marker_repair_accepted:true`.
- `manifest_validation_preflight_authorized:true` for authorized readback.
- `manifest_validation_preflight_authorization_is_readback_only_in_l22_1a:true`.
- `manifest_validation_execution_allowed:false`.
- `manifest_validation_active:false`.
- `manifest_validation_performed:false`.
- `downloaded_manifest_read:false`.
- `downloaded_archive_opened_for_manifest_validation:false`.
- `downloaded_archive_contents_listed_for_manifest_validation:false`.
- `downloaded_archive_extracted:false`.
- `archive_member_bytes_read:false`.
- `downloaded_file_bytes_read:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint.
