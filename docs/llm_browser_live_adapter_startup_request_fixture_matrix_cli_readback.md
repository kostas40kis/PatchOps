# L1.10 Live adapter startup request fixture matrix CLI/readback

L1.10 exposes the passive L1.9 startup-request fixture matrix through the main PatchOps llm-browser CLI.

## Command

```powershell
py -m patchops.cli llm-browser startup-request-fixtures --json --compact
```

Text readback is also available:

```powershell
py -m patchops.cli llm-browser startup-request-fixtures
```

## Contract

The command is readback-only. It delegates to `patchops.llm_browser.live_adapter_startup_request_fixtures` and must keep the same passive guarantees:

- no Selenium import;
- no browser/session creation;
- no click/download/paste/send/package-run operation;
- no commit or push;
- `startup_allowed` remains `false`;
- `side_effects_performed` remains an empty JSON array.

L1.10 is still L1 passive model/readback work. It does not silently expand into live browser automation.
