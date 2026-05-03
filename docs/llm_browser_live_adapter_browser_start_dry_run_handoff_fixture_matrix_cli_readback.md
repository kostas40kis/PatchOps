# L4.4 Live adapter browser-start dry-run handoff fixture matrix CLI/readback

L4.4 exposes the accepted L4.3 dry-run handoff fixture matrix through a passive `llm-browser` CLI/readback command.

Command:

```powershell
py -m patchops.cli llm-browser browser-start-dry-run-handoff-fixtures --repo-root C:\dev\patchops --json --compact
```

The command forwards only to `patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixtures`. It returns the same passive fixture matrix payload and does not authorize or perform live browser startup.

## Required passive boundary

- no Selenium import
- no browser start
- no browser session creation
- no driver creation
- no profile directory creation
- no adapter filesystem writes
- no click/download/paste/send/package-run side effect
- no commit/push

## Expected readback

The CLI readback must keep reporting:

- `patch: L4.3` for the underlying fixture matrix;
- `status: PASS` when L4.1, L4.2, and L4.3 artifacts are present;
- `next_patch: L4.4 Live adapter browser-start dry-run handoff fixture matrix CLI/readback` inside the fixture matrix payload;
- Edge and Opera modelled only as dry-run handoff targets;
- unsupported browser fixture rejected without startup;
- all side-effect lists empty.

## Next patch

If accepted, continue with:

`L4.5 Live adapter browser-start dry-run handoff fixture matrix contract gate`
