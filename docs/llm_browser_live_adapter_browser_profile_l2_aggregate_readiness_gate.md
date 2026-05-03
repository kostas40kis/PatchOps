# L2.7 Live adapter browser profile preflight L2 aggregate readiness gate

L2.7 adds a passive aggregate readiness gate for the L2 browser-profile preflight stack.

The gate combines readback from:

- `patchops.llm_browser.live_adapter_browser_profile_preflight`
- `patchops.llm_browser.live_adapter_browser_profile_preflight_fixtures`
- `patchops.llm_browser.live_adapter_browser_profile_preflight_fixture_matrix_contract_gate`

A PASS means the L2 profile-preflight stack is still only a contract/readback layer:

- the base browser-profile preflight contract passes;
- the fixture matrix passes;
- the fixture-matrix contract gate passes;
- the required Edge, Opera, invalid-browser, custom-profile, and optional-dependency fixture rows are present;
- startup remains blocked for every surface and fixture row;
- no browser is started and no browser session is created;
- no profile directory is created;
- no adapter filesystem writes are reported;
- requested side effects are modelled as data and not executed;
- invalid-browser cases are reported without browser/profile side effects;
- profile paths are calculated as data only;
- Selenium/browser optional modules are not imported or loaded.

Manual smoke commands:

```powershell
py -m patchops.llm_browser.live_adapter_browser_profile_l2_readiness_gate --repo-root "C:\dev\patchops" --json --compact
py -m patchops.llm_browser.live_adapter_browser_profile_l2_readiness_gate --repo-root "C:\dev\patchops"
```

This patch does not expose a new `patchops.cli llm-browser` command. That readback surface is left for the next patch:

**L2.8 Live adapter browser profile preflight L2 aggregate readiness gate CLI/readback**.
