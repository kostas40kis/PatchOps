# L2.10b path-length packaging repair: L2 broad validation checkpoint

This is a narrow packaging repair for the L2.10 passive broad-validation checkpoint.

Repair reason: the previous bundle failed before launcher execution because package extraction attempted to read a long content/docs path from the runtime package_runs directory. This repair shortens the bundle name and the content paths while preserving the passive L2.10 checkpoint semantics.

# L2.10 Live adapter browser profile preflight L2 broad validation checkpoint

L2.10 adds a passive broad-validation checkpoint for the L2 browser-profile preflight stack.

It aggregates/readbacks the already accepted L2.1 through L2.9 browser-profile preflight surfaces and proves that the L1 startup-request passive stack still remains present and green from the L2 boundary.

## Passive-only boundary

This checkpoint is intentionally passive-only:

- no Selenium import;
- no optional browser dependency import;
- no browser start;
- no browser session creation;
- no profile directory creation;
- no adapter filesystem writes;
- no click/download/paste/send/package-run side effect;
- no automatic git commit;
- no automatic git push.

The broad-validation command list is a plan/readback surface only. The checkpoint records the commands an operator may run for broad validation, but it does not execute those commands itself.

## What L2.10 checks

L2.10 checks that:

- the L2.9 documentation freeze/readiness checkpoint still reports PASS;
- the L2 aggregate readiness gate still reports PASS;
- the L1 final acceptance marker still reports PASS;
- required L2 docs/source/test paths are present;
- required L1 accepted surfaces remain present;
- the broad-validation command plan is passive and contains no browser/package-run/send side-effect command;
- no validation commands are executed by this checkpoint;
- no browser starts;
- no profile directory is created;
- no adapter filesystem writes are performed;
- no Selenium or optional browser dependency is imported or required;
- side-effect operations remain modelled-only.

## Readback

```powershell
py -m patchops.llm_browser.live_adapter_browser_profile_l2_broad_validation_checkpoint --repo-root C:\dev\patchops --json --compact
py -m patchops.llm_browser.live_adapter_browser_profile_l2_broad_validation_checkpoint --repo-root C:\dev\patchops
```

## Planned broad-validation commands

The checkpoint exposes a planned command list for the operator. These commands are readbacked as strings and are not executed by the module:

```powershell
py -m compileall patchops/llm_browser tests
py -m pytest -q tests/test_llm_browser_live_adapter_browser_profile_preflight_current.py tests/test_llm_browser_live_adapter_browser_profile_preflight_cli_readback_current.py tests/test_llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_current.py tests/test_llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_cli_readback_current.py tests/test_llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_contract_gate_current.py tests/test_llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_contract_gate_cli_readback_current.py tests/test_llm_browser_live_adapter_browser_profile_l2_aggregate_readiness_gate_current.py tests/test_llm_browser_live_adapter_browser_profile_l2_aggregate_readiness_gate_cli_readback_current.py tests/test_llm_browser_live_adapter_browser_profile_l2_documentation_freeze_checkpoint_current.py tests/test_llm_browser_live_adapter_browser_profile_l2_broad_validation_checkpoint_current.py
py -m patchops.cli llm-browser profile-preflight-l2-readiness --repo-root C:\dev\patchops --json --compact
py -m patchops.llm_browser.live_adapter_browser_profile_l2_readiness_gate --repo-root C:\dev\patchops --json --compact
py -m patchops.llm_browser.live_adapter_browser_profile_l2_documentation_checkpoint --repo-root C:\dev\patchops --json --compact
py -m patchops.llm_browser.live_adapter_startup_request_l1_final_acceptance_marker --repo-root C:\dev\patchops --json --compact
git status --short --branch
```

## Next patch

L2.11 Live adapter browser profile preflight L2 broad validation checkpoint CLI/readback
