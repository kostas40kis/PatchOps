# L5.13 Microsoft Edge supervised launch readiness CLI/readback

L5.13 adds the dedicated CLI/readback layer for the accepted L5.12 Microsoft Edge supervised launch readiness contract.

Microsoft Edge first. Opera second.

## CLI commands

L5.12 source readiness command:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-readiness --repo-root C:\dev\patchops --json --compact
```

L5.13 readback command:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-readiness-readback --repo-root C:\dev\patchops --json --compact
```

Module readback:

```powershell
py -m patchops.llm_browser.live_adapter_edge_supervised_launch_readiness_cli_readback --repo-root C:\dev\patchops --json --compact
```

## What this proves

L5.13 proves that:

- L5.12 still reports `PASS`;
- the L5.12 Edge readiness command is still registered;
- the L5.13 Edge readiness readback command is registered;
- the Edge readiness contract still blocks live startup;
- Microsoft Edge remains the first live-browser priority;
- Opera remains second;
- dedicated profile required remains true;
- manual user login required remains true;
- silent auto-submit remains false;
- no localhost PatchOps server is required;
- no browser extension is required.

## Passive safety boundary for this patch

This patch remains readback-only. It does not perform live browser automation.

Required passive guarantees:

- no Selenium import;
- no browser start;
- no Edge process start;
- no browser session creation;
- no driver creation;
- no profile directory creation;
- no adapter filesystem writes;
- no click/download/paste/send/package-run side effect;
- no automatic git commit;
- no automatic git push.

## Next patch

If accepted, continue with:

`L5.14 Live adapter Microsoft Edge supervised launch fixture matrix`