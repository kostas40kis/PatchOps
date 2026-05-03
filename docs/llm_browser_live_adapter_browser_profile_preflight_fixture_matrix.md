
# L2.3 Live adapter browser profile preflight fixture matrix

L2.3 adds a passive fixture matrix around the L2 browser-profile preflight contract.

The matrix models the profile/startup combinations that later live-browser work will need to reason about, without performing any browser or filesystem actions:

- default Edge request without acknowledgements;
- Opera request with all acknowledgements and requested browser/profile side effects;
- Edge profile-directory-only request;
- invalid browser request that is reported without side effects;
- custom profile root/name path calculation;
- optional browser dependency flag request.

## Passive contract

L2.3 remains a readback-only contract:

- no Selenium import;
- no browser start;
- no browser session creation;
- no profile directory creation;
- no filesystem writes;
- no click, download, paste, send, or package-run side effect;
- no automatic git commit or push;
- every fixture keeps `startup_allowed=false`;
- every fixture keeps `browser_started=false`;
- every fixture keeps `profile_directory_created=false`;
- every fixture keeps `side_effects_performed=[]` and `filesystem_writes_performed=[]`.

## Module readback

```powershell
py -m patchops.llm_browser.live_adapter_browser_profile_preflight_fixtures --repo-root C:\dev\patchops --json --compact
```

Text readback:

```powershell
py -m patchops.llm_browser.live_adapter_browser_profile_preflight_fixtures --repo-root C:\dev\patchops
```

The module is `patchops/llm_browser/live_adapter_browser_profile_preflight_fixtures.py` and exposes:

- `build_browser_profile_preflight_fixture_cases(...)`
- `build_browser_profile_preflight_fixture_matrix(...)`

L2.3 does not add a PatchOps CLI command yet. L2.4 is reserved for the CLI/readback surface around this fixture matrix.

Next patch: L2.4 Live adapter browser profile preflight fixture matrix CLI/readback.
