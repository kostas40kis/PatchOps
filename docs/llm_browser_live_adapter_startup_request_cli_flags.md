# L1.7p Startup Request Requested-Side-Effects Repair

L1.7p keeps the startup-request CLI passive while ensuring allow flags are reflected as requested side effects in JSON readback. Startup remains blocked and no browser/session side effects occur.
## L1.8 contract gate

The L1.8 contract gate is `patchops.llm_browser.live_adapter_startup_request_contract_gate`.

It is a read-only proof surface for the startup request model. It checks the public API names, JSON payload keys, requested-side-effect modelling, callable legacy helpers, CLI aliases, and the no-optional-browser-dependency boundary.

The gate is still passive: it reports `startup_allowed: false`, `browser_started: false`, and `side_effects_performed: []`.
