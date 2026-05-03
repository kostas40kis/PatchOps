# L3.11 Live adapter browser-start authorization L3 broad validation checkpoint CLI/readback

This patch adds the passive CLI/readback wrapper for the accepted L3.10 broad validation checkpoint.

## Command

```powershell
py -m patchops.cli llm-browser browser-start-authorization-l3-broad-validation --repo-root C:\dev\patchops --json --compact
```

## Boundary

L3.11 remains passive. It forwards to `patchops.llm_browser.live_adapter_browser_start_authorization_l3_broad_validation_checkpoint` and does not authorize or perform live startup work.

Required invariants:

- no Selenium import;
- no browser start;
- no browser session creation;
- no profile directory creation;
- no adapter filesystem writes;
- no click/download/paste/send/package-run side effect from adapter logic;
- no commit or push.

## Expected readback

The command returns the L3.10 broad-validation payload. It must keep:

- `patch = L3.10`
- `status = PASS`
- `browser_started = false`
- `browser_session_created = false`
- `profile_directory_created = false`
- `optional_browser_dependencies_required = false`
- `selenium_imported = false`

## Next patch

If accepted, continue with `L3.12 Live adapter browser-start authorization L3 final acceptance marker`.
