# L15.2 Microsoft Edge live-start authorization/execution gate CLI readback

L15.2 proves the accepted L15.1 live-start authorization/execution gate through compact JSON readback.

It is still not the first real Edge start. L15.2 is passive and performs no launch-side effects.

## Source commands

L15.2 reads back the L15.1 source command:

```text
browser-start-supervised-launch-edge-live-start-authorization-execution-gate
```

That L15.1 command is layered on the accepted L14.9 source command:

```text
browser-start-supervised-launch-edge-dedicated-profile-lifecycle-final-acceptance-marker
```

The new L15.2 command is:

```text
browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback
```

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback --repo-root C:\dev\patchops --json --compact
```

## Contract

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L15.2.
- compact JSON readback is required.
- no-authorization readback must keep execution blocked.
- explicitly-authorized readback must prove authorization without allowing launch execution.
- authorization is readback-only in L15.2.
- launch execution allowed: false.
- L15.2 is passive.
- operator review is required before any future live start.
- auto-send remains false by default.

## Safety boundary

L15.2 performs:

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

## Required readback outcomes

The L15.2 readback must confirm both L15.1 modes:

- no-authorization readback: `live_start_operator_authorization_complete:false` and `launch_execution_allowed:false`.
- explicitly-authorized readback: `live_start_operator_authorization_complete:true` and `launch_execution_allowed:false`.

Both readbacks must preserve:

- `browser_started:false`.
- `edge_process_started:false`.
- `selenium_imported_by_readback:false`.
- `profile_directory_created:false`.
- `auto_send_allowed:false`.

## Next patch

L15.3 first controlled Microsoft Edge open proof using dedicated profile only.
