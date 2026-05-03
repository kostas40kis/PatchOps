# L3.1 Live adapter explicit browser-start authorization contract

L3.1 starts the next live-adapter stream after the accepted L2 browser-profile preflight final acceptance marker.

This patch is still passive. It does not start Edge or Opera. It does not import Selenium or webdriver-manager. It does not create a browser profile directory, open a driver session, read a page, click a download, paste into a composer, send or submit a message, run a PatchOps package from adapter logic, commit, or push.

## Purpose

L3.1 introduces an explicit browser-start authorization contract as data. Later patches can use this contract before any live browser startup is allowed. The contract records:

- the requested browser, currently `edge` or `opera`;
- the requirement for a dedicated profile;
- the acknowledgement that manual login is required;
- the acknowledgement that PatchOps remains the source of truth;
- the fact that download, paste, send, and package-run operations are still separate future gates;
- the requested live side effects as modelled data only.

## Readback

```powershell
py -m patchops.llm_browser.live_adapter_browser_start_authorization --repo-root C:\dev\patchops --json --compact
py -m patchops.llm_browser.live_adapter_browser_start_authorization --repo-root C:\dev\patchops
```

Even when all acknowledgement flags are modelled as present, L3.1 still reports:

```text
startup_authorized: false
browser_started: false
browser_session_created: false
profile_directory_created: false
side_effects_performed: []
filesystem_writes_performed: []
optional_browser_dependencies_required: false
```

## Boundary

L3.1 does not expose a new main `patchops.cli llm-browser` command yet. That is reserved for the next patch.

Next patch: **L3.2 Live adapter explicit browser-start authorization CLI/readback**.
