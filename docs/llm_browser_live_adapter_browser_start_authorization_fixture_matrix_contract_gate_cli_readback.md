# L3.6 Live adapter browser-start authorization fixture matrix contract gate CLI/readback

L3.6 adds a passive `llm-browser` CLI/readback command for the L3.5 browser-start authorization fixture matrix contract gate.

Command:

```powershell
py -m patchops.cli llm-browser browser-start-authorization-contract-gate --repo-root C:\dev\patchops --json --compact
```

Boundary:

- no Selenium import;
- no browser start;
- no browser session creation;
- no profile directory creation;
- no adapter filesystem writes;
- no click/download/paste/send/package-run side effect;
- no commit or push.

This patch only exposes the already-accepted passive contract gate through the operator CLI. It does not authorize or perform live browser startup.

The command forwards to:

```text
patchops.llm_browser.live_adapter_browser_start_authorization_fixture_matrix_contract_gate
```

Expected current payload:

```text
patch: L3.5
status: PASS
browser_started: false
browser_session_created: false
profile_directory_created: false
side_effects_performed: []
filesystem_writes_performed: []
```

Expected next patch: **L3.7 Live adapter browser-start authorization L3 aggregate readiness gate**.
