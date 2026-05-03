# L4.7 Live adapter browser-start dry-run handoff L4 aggregate readiness gate

L4.7 adds a passive aggregate readiness gate for the L4 browser-start dry-run handoff stack.

This is still **dry-run-only**. It does not authorize live browser automation and does not silently expand into browser startup.

## What this gate aggregates

The gate checks that the accepted L4 surfaces remain intact:

- L4.1 dry-run handoff contract;
- L4.2 dry-run handoff CLI/readback;
- L4.3 dry-run handoff fixture matrix;
- L4.4 fixture matrix CLI/readback;
- L4.5 fixture matrix contract gate;
- L4.6 contract gate CLI/readback.

It verifies that the required source, docs, and focused tests are present, that the expected CLI commands remain registered, and that Edge/Opera browser-start requests remain modelled as readback data only.

## Operator readback commands

```powershell
py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate --repo-root "C:\dev\patchops" --json --compact
py -m patchops.cli llm-browser browser-start-dry-run-handoff --repo-root "C:\dev\patchops" --browser edge --json --compact
py -m patchops.cli llm-browser browser-start-dry-run-handoff --repo-root "C:\dev\patchops" --browser opera --json --compact
py -m patchops.cli llm-browser browser-start-dry-run-handoff-fixtures --repo-root "C:\dev\patchops" --json --compact
py -m patchops.cli llm-browser browser-start-dry-run-handoff-contract-gate --repo-root "C:\dev\patchops" --json --compact
git status --short --branch
```

The command plan is readback-only. It must not include `run-package`, `git commit`, or `git push` as automatic adapter actions.

## Boundary

This patch performs no Selenium import, no browser start, no browser session creation, no driver creation, no profile directory creation, no adapter filesystem writes, no click/download/paste/send/package-run side effect, and no commit or push.

It also keeps optional browser dependencies optional: Selenium, webdriver-manager, pyperclip, psutil, Playwright, and Pyppeteer are not imported or required by this gate.

## Next patch

If accepted, continue with:

`L4.8 Live adapter browser-start dry-run handoff L4 aggregate readiness gate CLI/readback`
