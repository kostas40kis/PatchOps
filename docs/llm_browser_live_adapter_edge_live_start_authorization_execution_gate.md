# L15.1 Microsoft Edge live-start authorization/execution gate

L15.1 starts the next stream after the accepted L14.9 dedicated-profile lifecycle final marker.

This patch is **not** the first real Edge start. L15.1 is passive. It defines the explicit authorization and token gate that a future live-start proof must pass before actual process launch can be considered.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-authorization-execution-gate --repo-root C:\dev\patchops --json --compact
```

Authorized readback example:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-authorization-execution-gate --repo-root C:\dev\patchops --allow-live-start --authorization-token PATCHOPS_L15_EDGE_LIVE_START_AUTHORIZED --json --compact
```

## Source command

L15.1 is explicitly layered on the accepted L14.9 source command:

```text
browser-start-supervised-launch-edge-dedicated-profile-lifecycle-final-acceptance-marker
```

The new passive L15.1 command remains:

```text
browser-start-supervised-launch-edge-live-start-authorization-execution-gate
```

## Contract

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L15.1.
- explicit live-start authorization flag required.
- explicit live-start authorization token required.
- dedicated profile candidate inherited from L14.9.
- default Microsoft Edge profile rejected.
- launch execution allowed: false.
- L15.1 is passive.
- operator review is required before any future live start.
- auto-send remains false by default.

## Safety boundary

L15.1 performs:

- no Selenium import.
- no browser start.
- no Edge process start.
- no browser session creation.
- no driver creation.
- no profile directory creation.
- no profile directory mutation.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

Supplying both `--allow-live-start` and `--authorization-token PATCHOPS_L15_EDGE_LIVE_START_AUTHORIZED` only proves the authorization surface. It still does not allow launch execution in L15.1.

## Readback fields

The compact JSON readback reports:

- `source_l14_09_final_marker_accepted`.
- `explicit_live_start_authorization_flag_present`.
- `explicit_live_start_authorization_token_present`.
- `live_start_operator_authorization_complete`.
- `dedicated_profile_candidate_inherited_from_l14_9`.
- `default_edge_profile_rejected`.
- `live_start_execution_gate_enforced`.
- `live_start_execution_gate_passive`.
- `launch_execution_allowed`.
- `browser_started`.
- `edge_process_started`.
- `profile_directory_created`.

## Next patch

L15.2 Microsoft Edge live-start authorization/execution gate CLI readback.
