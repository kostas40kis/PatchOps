# L2.4 Live adapter browser profile preflight fixture matrix CLI/readback

L2.4 exposes the passive L2.3 browser-profile preflight fixture matrix through the main PatchOps `llm-browser` CLI.

## Command

```powershell
py -m patchops.cli llm-browser profile-preflight-fixtures --repo-root C:\dev\patchops --json --compact
```

Text readback is also available:

```powershell
py -m patchops.cli llm-browser profile-preflight-fixtures --repo-root C:\dev\patchops
```

## Contract

The command is readback-only. It delegates to `patchops.llm_browser.live_adapter_browser_profile_preflight_fixtures` and must keep the same passive guarantees:

- no Selenium import;
- no browser/session creation;
- no profile directory creation;
- no filesystem writes from adapter logic;
- no click/download/paste/send/package-run operation;
- no commit or push;
- `startup_allowed` remains `false`;
- `profile_directory_created` remains `false`;
- `side_effects_performed` and `filesystem_writes_performed` remain empty JSON arrays.

L2.4 is still L2 passive profile preflight model/readback work. It does not silently expand into live browser automation.
