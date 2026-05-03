# L2.8 Live adapter browser profile preflight L2 aggregate readiness gate CLI/readback

L2.8 exposes the passive L2.7 browser-profile preflight L2 aggregate readiness gate through the main PatchOps `llm-browser` CLI.

## Command

```powershell
py -m patchops.cli llm-browser profile-preflight-l2-readiness --repo-root C:\dev\patchops --json --compact
```

Text readback is also available:

```powershell
py -m patchops.cli llm-browser profile-preflight-l2-readiness --repo-root C:\dev\patchops
```

## Contract

The command is readback-only. It delegates to `patchops.llm_browser.live_adapter_browser_profile_l2_readiness_gate` and must keep the same passive guarantees:

- no Selenium import;
- no optional browser dependency import;
- no browser/session creation;
- no profile directory creation;
- no filesystem writes from adapter logic;
- no click/download/paste/send/package-run operation;
- no commit or push;
- `startup_allowed` remains `false`;
- `profile_directory_created` remains `false`;
- `side_effects_performed` and `filesystem_writes_performed` remain empty JSON arrays.

L2.8 is still L2 passive profile-preflight contract/readback work. It does not silently expand into live browser automation.

Next patch: L2.9 Live adapter browser profile preflight L2 documentation freeze/readiness checkpoint.
