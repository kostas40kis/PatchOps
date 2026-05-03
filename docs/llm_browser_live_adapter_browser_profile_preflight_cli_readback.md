# L2.2 Live adapter browser profile preflight CLI/readback

L2.2 exposes the passive L2.1 browser-profile preflight contract through the main PatchOps `llm-browser` CLI.

## Commands

JSON readback:

```powershell
py -m patchops.cli llm-browser profile-preflight --repo-root C:\dev\patchops --json --compact
```

Operator text readback:

```powershell
py -m patchops.cli llm-browser profile-preflight --repo-root C:\dev\patchops
```

Requested side effects can be modelled without execution:

```powershell
py -m patchops.cli llm-browser profile-preflight --repo-root C:\dev\patchops --browser opera --ack-all --allow-browser-start --allow-profile-directory-creation --json --compact
```

## Contract

This is a readback-only CLI surface. It delegates to `patchops.llm_browser.live_adapter_browser_profile_preflight` and preserves the L2.1 boundary:

- no Selenium import;
- no browser start;
- no browser session creation;
- no profile directory creation;
- no filesystem writes;
- no click, download, paste, send, or package-run side effect;
- no automatic git commit or push;
- `startup_allowed` remains `false`;
- `profile_directory_created` remains `false`;
- `side_effects_performed` remains an empty JSON array;
- `filesystem_writes_performed` remains an empty JSON array.

L2.2 is still passive profile preflight/readback work. It does not silently expand into live browser automation.
