# L4.5 Live adapter browser-start dry-run handoff fixture matrix contract gate

This patch adds a passive contract gate for the L4 browser-start dry-run handoff fixture matrix.

The gate proves that the accepted L4.3 fixture matrix and L4.4 CLI/readback surfaces remain present and passive. It is dry-run-only and exists to validate readback data, not to start browsers.

## Boundary

- no Selenium import
- no browser start
- no browser session creation
- no driver creation
- no profile directory creation
- no adapter filesystem writes
- no click/download/paste/send/package-run side effect
- no git commit or push

## Checks

The gate verifies:

- the L4 dry-run handoff fixture matrix still reports PASS;
- Edge and Opera dry-run handoff cases are present;
- mixed-case browser normalization remains modelled-only;
- unsupported browser requests remain rejected without startup;
- the L4.4 CLI/readback command remains registered;
- source, docs, and focused tests required by L4.1 through L4.4 are present;
- the command plan is readback-only and excludes live browser operations;
- optional browser dependencies are not imported or required.

## Operator readback

```powershell
py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixture_matrix_contract_gate --repo-root C:\dev\patchops --json --compact
```

Next patch: L4.6 Live adapter browser-start dry-run handoff fixture matrix contract gate CLI/readback.
