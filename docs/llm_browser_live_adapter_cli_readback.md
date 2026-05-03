# LLM browser live adapter CLI/readback skeleton

L1.2 exposes the first passive readback surface for the future live browser adapter.

This is still **not** live browser automation. It is a contract/readback patch only.

## Operator command

```powershell
py -m patchops.cli llm-browser live-adapter --json
```

Equivalent module-level smoke:

```powershell
py -m patchops.llm_browser.live_adapter --json
```

## Required JSON contract

The readback payload must include:

- `patch: L1.2`
- `status: PASSIVE_READBACK_ONLY`
- `browser_started: false`
- `browser_session_created: false`
- `optional_browser_dependencies_required: false`
- `side_effects_performed: []`
- every live operation listed under `blocked_operations`

## Blocked operations

L1.2 keeps these operations blocked:

- `start_browser`
- `read_page`
- `detect_latest_assistant_reply`
- `click_download`
- `run_patchops_package`
- `paste_to_composer`
- `send_or_submit`

Calling any of those Python functions raises `LiveAdapterBlockedError` and records no side effects.

## Explicit non-goals

L1.2 must not:

- import Selenium or optional browser packages;
- start Edge, Opera, Chrome, Firefox, or any driver process;
- click, download, paste, send, submit, or run a package;
- commit or push git changes.

Next patch: **L1.3 Live adapter passive contract gate**.

<!-- PATCHOPS_L1_03_LIVE_ADAPTER_PASSIVE_CONTRACT_GATE_START -->

## L1.3 passive contract gate

The maintained L1.3 gate is:

```powershell
py -m patchops.llm_browser.live_adapter_contract_gate --json --compact
```

It verifies the L1.2 readback payload, blocked operation list, optional dependency
boundary, module-level blocked functions, and `LiveAdapterSkeleton` blocked method
results without starting a browser or performing side effects.

Next patch: **L1.4 Live adapter explicit startup gate scaffold**.

<!-- PATCHOPS_L1_03_LIVE_ADAPTER_PASSIVE_CONTRACT_GATE_END -->
