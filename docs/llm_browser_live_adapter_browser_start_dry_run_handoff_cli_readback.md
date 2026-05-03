# L4.2 Live adapter browser-start dry-run handoff CLI/readback

This patch exposes a passive `llm-browser browser-start-dry-run-handoff` CLI/readback surface for the L4.1 dry-run handoff contract.

## Boundary

This is still dry-run-only. It does not start a browser, import Selenium, create a WebDriver, create a browser profile directory, click downloads, paste into the composer, send messages, run downloaded packages from adapter logic, commit, or push.

The CLI only forwards arguments to `patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_contract` and returns that module's readback payload.

## Readback command

```powershell
py -m patchops.cli llm-browser browser-start-dry-run-handoff --repo-root C:\dev\patchops --browser edge --json --compact
```

Opera is modelled the same way:

```powershell
py -m patchops.cli llm-browser browser-start-dry-run-handoff --repo-root C:\dev\patchops --browser opera --json --compact
```

## Required passive checks

- no Selenium import
- no browser start
- no browser session creation
- no profile directory creation
- no adapter filesystem writes
- no click/download/paste/send/package-run side effect
- no commit/push

## Next patch

L4.3 Live adapter browser-start dry-run handoff fixture matrix.
