# L1.14 Live adapter startup request L1 aggregate readiness gate CLI/readback

L1.14 exposes the passive L1.13 startup-request L1 aggregate readiness gate through the main PatchOps llm-browser CLI.

## Command

```powershell
py -m patchops.cli llm-browser startup-request-l1-readiness --json --compact
```

Text readback is also available:

```powershell
py -m patchops.cli llm-browser startup-request-l1-readiness
```

## Contract

The command is readback-only. It delegates to `patchops.llm_browser.live_adapter_startup_request_l1_readiness_gate` and must keep the same passive guarantees:

- no Selenium import;
- no browser/session creation;
- no click/download/paste/send/package-run operation;
- no commit or push;
- `startup_allowed` remains `false`;
- `side_effects_performed` remains an empty JSON array;
- the startup-request contract gate still reports `PASS`;
- the fixture matrix still reports `PASS`;
- the fixture-matrix contract gate still reports `PASS`.

L1.14 is still L1 passive model/readback work. It does not silently expand into live browser automation.
