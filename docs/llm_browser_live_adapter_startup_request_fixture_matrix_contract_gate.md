# L1.11 Live adapter startup request fixture matrix contract gate

L1.11 adds a passive contract gate around the L1.9/L1.10 startup-request fixture matrix.

The gate is readback-only. It does not import Selenium, start a browser, click, download, paste, send, run PatchOps packages from the adapter, commit, or push.

## Contract

The contract gate verifies that:

- the fixture matrix readback remains JSON-safe;
- all core cases are present;
- every fixture decision keeps `startup_allowed: false`;
- no fixture creates a browser session;
- requested side effects are modelled but not executed;
- the invalid-browser fixture reports invalid input without side effects;
- the upstream startup-request contract gate still passes;
- optional browser dependency roots remain unloaded.

## Operator commands

```powershell
py -m patchops.llm_browser.live_adapter_startup_request_fixture_matrix_contract_gate --json --compact
py -m patchops.llm_browser.live_adapter_startup_request_fixture_matrix_contract_gate
```

Expected status is `PASS`, while startup remains blocked.

Next patch: L1.12 Live adapter startup request fixture matrix contract gate CLI/readback.
