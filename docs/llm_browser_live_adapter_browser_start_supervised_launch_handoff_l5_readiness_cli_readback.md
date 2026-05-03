# L5.8 Live adapter browser-start supervised launch handoff L5 aggregate readiness gate CLI/readback

This patch adds the passive CLI/readback wrapper for the accepted L5.7 aggregate readiness gate.

## Command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-handoff-l5-readiness --repo-root C:\dev\patchops --json --compact
```

## Boundary

This command forwards to `patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate` and remains model/readback-only:

- no Selenium import
- no browser start
- no browser session creation
- no driver creation
- no profile directory creation
- no adapter filesystem writes
- no click/download/paste/send/package-run side effect
- no git commit or push

## Acceptance meaning

L5.8 passes only when the CLI command is registered, the CLI JSON/text readback matches the accepted L5.7 module payload, and the readback remains passive. It does not authorize or perform a real browser launch.

Next patch: L5.9 Live adapter browser-start supervised launch handoff L5 documentation freeze/readiness checkpoint.
