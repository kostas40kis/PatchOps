# L5.11 Live adapter browser-start supervised launch handoff L5 broad validation checkpoint CLI/readback

L5.11 exposes the accepted L5.10 broad-validation checkpoint through the main passive `llm-browser` CLI/readback surface.

L5.11c direct-manifest repair follows the L5.11b report, where bundle preflight passed and the launcher exited 0 but the inner report still reported FAIL. This repair avoids the zip/content-path layer entirely and keeps the validation contract narrow enough to expose the real L5.11 readback state.

## Command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-handoff-l5-broad-validation --repo-root C:\dev\patchops --json --compact
```

Module readback remains available:

```powershell
py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback --repo-root C:\dev\patchops --json --compact
```

## What this proves

The readback confirms that the L5.10 broad validation checkpoint still reports `PASS` and that the L5.11 CLI/readback command is installed.

It also reads back the accepted earlier passive boundaries without importing or executing live browser logic:

- L1.17 startup-request passive stack;
- L2.12d browser-profile preflight passive stack;
- L3.12 browser-start authorization passive stack;
- L4.12 browser-start dry-run handoff passive stack.

## Browser priority

Microsoft Edge first. Opera second.

L5.11 does not start Edge yet. It only records the Edge-first priority and keeps the next patch focused on Microsoft Edge supervised-launch readiness.

## Passive safety boundary

This patch remains readback-only. It does not perform live browser automation and does not execute the broad validation command plan from adapter logic.

Required passive guarantees:

- no Selenium import;
- no browser start;
- no browser session creation;
- no driver creation;
- no profile directory creation;
- no adapter filesystem writes;
- no click/download/paste/send/package-run side effect;
- no automatic git commit;
- no automatic git push.

## Next patch

If accepted, continue with:

`L5.12 Live adapter Microsoft Edge supervised launch readiness contract`