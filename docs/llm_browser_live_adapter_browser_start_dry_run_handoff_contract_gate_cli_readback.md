# L4.6 Live adapter browser-start dry-run handoff fixture matrix contract gate CLI/readback

This patch adds a passive CLI/readback wrapper for the accepted L4.5 dry-run handoff fixture matrix contract gate.

Command:

```powershell
py -m patchops.cli llm-browser browser-start-dry-run-handoff-contract-gate --repo-root C:\dev\patchops --json --compact
```

The command is dry-run-only. It forwards to `patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixture_matrix_contract_gate` and returns the existing passive contract-gate payload.

## Boundary

- no Selenium import
- no browser start
- no browser session creation
- no driver creation
- no profile directory creation
- no adapter filesystem writes
- no click/download/paste/send/package-run side effect
- no git commit or push

## Readback scope

The CLI/readback proves that:

- the L4.5 contract gate remains callable through the operator-facing `patchops.cli llm-browser` surface;
- the accepted L4.3 fixture matrix remains the data source;
- the accepted L4.4 fixture matrix CLI/readback remains present;
- the L4.5 contract gate still reports PASS;
- the command remains passive and side-effect blocked.

Next patch: L4.7 Live adapter browser-start dry-run handoff L4 aggregate readiness gate.
