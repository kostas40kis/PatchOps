# L2.5 Live adapter browser profile preflight fixture matrix contract gate

L2.5 adds a passive contract gate for the L2 browser-profile preflight fixture matrix.

The gate proves that the fixture matrix remains a readback/data contract only:

- the required Edge, Opera, invalid-browser, custom-profile, and optional-dependency fixture rows are present;
- every fixture row blocks startup;
- no fixture row starts a browser or creates a browser session;
- no fixture row creates a profile directory or records filesystem writes from adapter logic;
- requested side effects are modelled as data and not executed;
- the invalid-browser fixture is reported without browser/profile side effects;
- profile paths are calculated as data only;
- payloads remain JSON-safe;
- Selenium/browser optional modules are not imported or loaded.

## Manual smoke commands

```powershell
py -m patchops.llm_browser.live_adapter_browser_profile_preflight_fixture_matrix_contract_gate --repo-root "C:\dev\patchops" --json --compact
py -m patchops.llm_browser.live_adapter_browser_profile_preflight_fixture_matrix_contract_gate --repo-root "C:\dev\patchops"
```

## Boundary

This patch is still passive L2 scaffolding. It does not import Selenium, start a browser, create a browser profile directory, write files from adapter logic, click, download, paste, send, run PatchOps packages from adapter logic, commit, or push.

Next patch: **L2.6 Live adapter browser profile preflight fixture matrix contract gate CLI/readback**.
