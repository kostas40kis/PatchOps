# LLM browser live adapter passive contract gate

L1.3 adds a passive contract gate for the L-phase live adapter skeleton.

This is still **not** live browser automation. It does not start Edge, Opera,
Chrome, Firefox, Selenium, or any driver process. It does not click, download,
paste, send, submit, run PatchOps packages, commit, or push.

## Purpose

L1.1 created the no-side-effect live-adapter skeleton. L1.2 exposed passive
CLI/readback for that skeleton. L1.3 adds a dedicated gate that evaluates the
contract and fails closed if the skeleton stops being passive.

## Operator smoke

```powershell
py -m patchops.llm_browser.live_adapter_contract_gate --json --compact
```

The gate returns a JSON payload with:

- `patch: L1.3`
- `status: PASS` when the passive contract is intact
- `browser_started: false`
- `browser_session_created: false`
- `optional_browser_dependencies_required: false`
- `side_effects_performed: []`
- every live operation listed in `required_blocked_operations`

## Checks

The gate verifies:

1. the L1.2 readback payload is passive;
2. every live operation remains listed as blocked;
3. optional browser dependency imports are absent from `live_adapter.py`;
4. module-level live operations raise `LiveAdapterBlockedError`;
5. `LiveAdapterSkeleton` methods return blocked/unsupported results without side effects;
6. evaluating the gate does not load Selenium or browser optional dependency modules.

## Required blocked operations

```text
start_browser
read_page
detect_latest_assistant_reply
click_download
run_patchops_package
paste_to_composer
send_or_submit
```

## Next patch

Next patch: **L1.4 Live adapter explicit startup gate scaffold**.

<!-- PATCHOPS_L1_04_LIVE_ADAPTER_STARTUP_GATE_SCAFFOLD_START -->

## L1.4 startup gate scaffold follow-up

After the L1.3 passive contract gate, L1.4 adds
`patchops/llm_browser/live_adapter_startup_gate.py` as the explicit startup gate
scaffold. It is still passive and no-side-effect:

```powershell
py -m patchops.llm_browser.live_adapter_startup_gate --json --compact
```

The L1.4 startup gate keeps startup blocked with `startup_allowed: false` and
names the acknowledgements required by a later live-browser phase.

<!-- PATCHOPS_L1_04_LIVE_ADAPTER_STARTUP_GATE_SCAFFOLD_END -->
