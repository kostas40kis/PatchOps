# L1.12 Live adapter startup request fixture matrix contract gate CLI/readback

L1.12 exposes the passive L1.11 startup-request fixture matrix contract gate through the main PatchOps llm-browser CLI.

## Command

```powershell
py -m patchops.cli llm-browser startup-request-fixture-gate --json --compact
```

Text readback is also available:

```powershell
py -m patchops.cli llm-browser startup-request-fixture-gate
```

## Contract

The command is readback-only. It delegates to `patchops.llm_browser.live_adapter_startup_request_fixture_matrix_contract_gate` and must keep the same passive guarantees:

- no Selenium import;
- no browser/session creation;
- no click/download/paste/send/package-run operation;
- no commit or push;
- `startup_allowed` remains `false`;
- `side_effects_performed` remains an empty JSON array;
- the upstream startup-request contract gate still reports `PASS`.

L1.12 is still L1 passive model/readback work. It does not silently expand into live browser automation.
