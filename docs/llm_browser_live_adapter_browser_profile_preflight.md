
# L2.1 live adapter browser profile preflight contract

This patch starts L2 with a passive browser-profile preflight contract for the LLM browser live adapter. It does not start Edge or Opera. It does not import Selenium or webdriver-manager. It does not create a browser profile directory, click, download, paste, send, run PatchOps packages from the adapter, commit, or push.

The preflight contract models the browser profile requirements that a later live-browser phase will need before any browser can be started:

- supported browsers are `edge` and `opera`;
- the profile mode is `dedicated`;
- manual login is required;
- PatchOps remains the source of truth for applying downloaded bundles;
- startup remains blocked in L2.1;
- requested side effects are recorded as data only;
- performed side effects and filesystem writes must remain empty arrays.

The Python module is `patchops/llm_browser/live_adapter_browser_profile_preflight.py`. It exposes passive readback helpers:

- `build_browser_profile_preflight_request(...)`
- `evaluate_browser_profile_preflight(...)`
- `build_default_browser_profile_preflight(...)`
- `build_fully_acknowledged_browser_profile_preflight(...)`
- `build_profile_preflight_contract(...)`

The command below is module-only and passive:

```powershell
py -m patchops.llm_browser.live_adapter_browser_profile_preflight --repo-root C:\dev\patchops --json --compact
```

A request may model permissions without executing them:

```powershell
py -m patchops.llm_browser.live_adapter_browser_profile_preflight --repo-root C:\dev\patchops --browser opera --ack-all --allow-browser-start --allow-profile-directory-creation --json --compact
```

Even with those flags, the expected L2.1 result is still `startup_allowed=false`, `browser_started=false`, `profile_directory_created=false`, `side_effects_performed=[]`, and `filesystem_writes_performed=[]`.

Next patch: L2.2 Live adapter browser profile preflight CLI/readback.
