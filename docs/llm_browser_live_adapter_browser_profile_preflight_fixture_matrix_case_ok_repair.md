# L2.3a Browser profile preflight fixture case OK repair

L2.3a is a narrow repair for the L2.3 browser-profile preflight fixture matrix.

The failed L2.3 report showed that the patch applied and compiled, but focused pytest failed because at least one fixture row returned `case["ok"] is False` while the fixture was intentionally modelling a rejected/passive request. The fixture matrix contract is that fixture rows are successful when they are safely blocked and report the expected no-side-effect state.

This repair changes only the per-case success semantics in `patchops/llm_browser/live_adapter_browser_profile_preflight_fixtures.py`:

- `case["ok"]` now means the fixture was safely blocked and reported as expected.
- The invalid-browser fixture is allowed to report `invalid_fields == ["requested_browser"]` and still pass as a fixture case.
- All fixture cases must still prove no browser starts, no browser session is created, no profile directory is created, no filesystem writes occur, and no side effects are performed.
- Selenium and other optional browser dependencies remain outside this patch.

This patch remains passive-only and does not import Selenium, start a browser, create a profile directory, write files from the adapter, click, download, paste, send, run packages from the adapter, commit, or push.

Next patch after acceptance: **L2.4 Live adapter browser profile preflight fixture matrix CLI/readback**.
