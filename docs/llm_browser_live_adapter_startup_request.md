# LLM browser live adapter startup request

L1.7 keeps the startup request model passive. The module exposes both the
original L1.6 helper names and the L1.7 CLI/readback names so existing tests and
operator surfaces stay compatible.

The model may describe requested browser startup permissions, requested
side-effect operations, and operator acknowledgements. It must still report
`startup_allowed: false`, `browser_started: false`,
`browser_session_created: false`, and `side_effects_performed: []`.

This phase does not import Selenium, start a browser, click, download, paste,
send, run PatchOps packages from the adapter, commit, or push.
## L1.8 contract gate

The L1.8 contract gate is `patchops.llm_browser.live_adapter_startup_request_contract_gate`.

It is a read-only proof surface for the startup request model. It checks the public API names, JSON payload keys, requested-side-effect modelling, callable legacy helpers, CLI aliases, and the no-optional-browser-dependency boundary.

The gate is still passive: it reports `startup_allowed: false`, `browser_started: false`, and `side_effects_performed: []`.
