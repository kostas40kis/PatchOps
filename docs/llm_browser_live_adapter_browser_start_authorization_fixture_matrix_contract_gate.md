# L3.5 Live adapter browser-start authorization fixture matrix contract gate

L3.5 adds a passive contract gate for the browser-start authorization fixture matrix.

The gate validates that the accepted L3 authorization stack is still passive:

- L3.1 browser-start authorization contract is present;
- L3.2 CLI/readback command is present;
- L3.3 fixture matrix still passes;
- L3.4 fixture matrix CLI/readback remains available;
- fixture cases cover Edge, Opera, unsupported browser rejection, shared/default profile rejection, and explicit side-effect requests;
- no Selenium import;
- no optional browser dependency import or requirement;
- no browser start;
- no browser session creation;
- no profile directory creation;
- no adapter filesystem writes;
- no click/download/paste/send/package-run side effect;
- no commit or push.

The contract-gate module is:

```text
patchops/llm_browser/live_adapter_browser_start_authorization_fixture_matrix_contract_gate.py
```

Passive smoke command:

```powershell
py -m patchops.llm_browser.live_adapter_browser_start_authorization_fixture_matrix_contract_gate --repo-root C:\dev\patchops --json --compact
```

Expected next patch: **L3.6 Live adapter browser-start authorization fixture matrix contract gate CLI/readback**.
