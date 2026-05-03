# L1.13 Live adapter startup request L1 aggregate readiness gate

L1.13 adds a passive aggregate readiness gate for the L1 startup-request stack.

The gate combines readback from:

- `live_adapter_startup_request_contract_gate`
- `live_adapter_startup_request_fixtures`
- `live_adapter_startup_request_fixture_matrix_contract_gate`

The contract remains passive-only. A PASS means:

- startup is still blocked;
- no browser is started;
- no browser session is created;
- requested side effects are modelled but not executed;
- Selenium and other optional browser dependencies are not imported;
- fixture matrix invalid-browser cases are reported without side effects.

This patch does not expose a new `patchops.cli llm-browser` command. That is left for the next patch:

`L1.14 Live adapter startup request L1 aggregate readiness gate CLI/readback`
