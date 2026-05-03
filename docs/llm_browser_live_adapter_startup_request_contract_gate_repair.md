# L1.8e Startup Request Contract Gate Check-Name Repair

This repair preserves the L1 passive safety boundary while restoring the public
contract expected by the startup-request contract-gate tests.

It keeps browser startup blocked and performs no Selenium import, browser start,
click, download, paste, send, package-run, commit, or push side effect.

The gate exposes both expected operator heading variants:

- `PatchOps LLM browser live adapter startup request contract gate`
- `PatchOps LLM browser startup request contract gate`

It also preserves the expected check names:

- `required_public_api_surface`
- `readback_payload_contract`
- `startup_request_readback_payload`
- `requested_side_effects_modelled_not_executed`
