# L3.4 Live adapter browser-start authorization fixture matrix CLI/readback

This patch adds a passive CLI/readback wrapper for the L3.3 browser-start authorization fixture matrix.

Command:

```powershell
py -m patchops.cli llm-browser browser-start-authorization-fixtures --repo-root C:\dev\patchops --json --compact
```

Contract:

- no Selenium import
- no browser start
- no profile directory creation
- no browser session creation
- no adapter filesystem writes
- no click/download/paste/send/package-run side effect
- no commit or push
- fixture matrix output remains data-only/readback-only

The command forwards to `patchops.llm_browser.live_adapter_browser_start_authorization_fixtures` and does not add a live-start path.

Next patch: L3.5 Live adapter browser-start authorization fixture matrix contract gate.
