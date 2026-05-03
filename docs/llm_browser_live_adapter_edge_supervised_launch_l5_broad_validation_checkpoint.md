# L5.21 Microsoft Edge supervised launch L5 broad validation checkpoint

L5.21 is the passive Microsoft Edge supervised-launch L5 broad validation checkpoint. It reads back the accepted L5.20 documentation checkpoint, verifies the Edge L5 command/source/doc/test surface, and exposes a planned broad-validation command list for the operator.

Microsoft Edge first. Opera second.

## CLI commands

Source L5.20 documentation checkpoint:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-l5-documentation-checkpoint --repo-root C:\dev\patchops --json --compact
```

L5.21 broad validation checkpoint:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-l5-broad-validation --repo-root C:\dev\patchops --json --compact
```

Module readback:

```powershell
py -m patchops.llm_browser.live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint --repo-root C:\dev\patchops --json --compact
```

## What L5.21 checks

L5.21 checks that:

- L5.20 still reports PASS;
- L5.20 remains passive;
- the L5.20 source command remains registered;
- the L5.21 broad-validation command is registered;
- required Edge L5 commands are present;
- required Edge L5 source/docs/tests are present;
- required docs still contain the safety boundary;
- the planned broad-validation command list is readback-only;
- adapter logic executes no validation commands;
- Microsoft Edge first remains the browser priority;
- Opera second remains the browser priority;
- Selenium is not imported by readback;
- no browser or adapter side effects occur.

## Planned broad-validation command list

The planned broad-validation command list is for the operator and for PatchOps validation. Adapter logic executes no validation commands by itself.

```powershell
python -m compileall patchops/llm_browser tests
python -m pytest -q tests/test_l5_12_edge_supervised_launch_readiness_contract_current.py tests/test_l5_13_edge_supervised_launch_readiness_cli_readback_current.py tests/test_l5_14_edge_supervised_launch_fixture_matrix_current.py tests/test_l5_15_edge_supervised_launch_fixture_matrix_cli_readback_current.py tests/test_l5_16_edge_supervised_launch_fixture_matrix_contract_gate_current.py tests/test_l5_17_edge_supervised_launch_fixture_matrix_contract_gate_cli_readback_current.py tests/test_l5_18_edge_supervised_launch_l5_aggregate_readiness_gate_current.py tests/test_l5_19_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback_current.py tests/test_l5_20_edge_supervised_launch_l5_documentation_checkpoint_current.py tests/test_l5_21_edge_supervised_launch_l5_broad_validation_checkpoint_current.py
python -m patchops.llm_browser.live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint --repo-root C:\dev\patchops --json --compact
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-l5-broad-validation --repo-root C:\dev\patchops --json --compact
git status --short --branch
```

## Contract boundaries preserved

The broad validation checkpoint keeps these boundaries explicit:

- Microsoft Edge first;
- Opera second;
- dedicated profile required;
- default profile forbidden;
- manual user login required;
- silent auto-submit remains false;
- no localhost PatchOps server;
- no browser extension.

## Passive safety boundary for this patch

This patch remains readback-only. It does not perform live browser automation.

Required passive guarantees:

- no Selenium import;
- no browser start;
- no Edge process start;
- no browser session creation;
- no driver creation;
- no profile directory creation;
- no adapter filesystem writes except intended PatchOps source/docs/tests written by PatchOps;
- no click/download/paste/send/package-run side effect;
- no automatic git commit;
- no automatic git push.

## Next patch

If accepted, continue with:

`L5.22 Live adapter Microsoft Edge supervised launch L5 broad validation checkpoint CLI/readback`