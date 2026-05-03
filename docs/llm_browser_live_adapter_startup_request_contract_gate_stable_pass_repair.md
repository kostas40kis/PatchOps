# L1.8g Startup Request Contract Gate Stable PASS Repair

L1.8g repairs the startup-request contract gate after the alias-only L1.8f repair made the gate report `ok: false` again.

The gate is still passive only. It imports no Selenium/browser automation dependency, starts no browser, clicks nothing, downloads nothing, pastes nothing, sends nothing, runs no PatchOps package from the adapter, and performs no git action.

The stable gate preserves every public check-name alias expected by the current L1.8 tests:

- `required_public_api_surface`
- `readback_payload_contract`
- `startup_request_readback_payload`
- `requested_side_effects_are_modelled_but_blocked`
- `requested_side_effects_modelled_not_executed`
- `no_optional_browser_dependency_imports`
- `gate_did_not_load_browser_optional_modules`

A blocked startup request is a PASS when no browser/session/side-effect occurs.
