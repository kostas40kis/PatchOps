# L5.6 Live adapter browser-start supervised launch handoff fixture matrix contract gate CLI/readback

This patch adds a passive CLI/readback wrapper for the accepted L5.5 supervised-launch handoff fixture matrix contract gate.

Command:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-handoff-contract-gate --repo-root C:\dev\patchops --json --compact
```

The command is supervised-launch-handoff readback only. It forwards to `patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate` and returns the existing passive contract-gate payload.

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

- the L5.5 contract gate remains callable through the operator-facing `patchops.cli llm-browser` surface;
- the accepted L5.3 fixture matrix remains the data source;
- the accepted L5.4 fixture matrix CLI/readback remains present;
- the L5.5 contract gate still reports PASS;
- the command remains passive and side-effect blocked.

Next patch: L5.7 Live adapter browser-start supervised launch handoff L5 aggregate readiness gate.
