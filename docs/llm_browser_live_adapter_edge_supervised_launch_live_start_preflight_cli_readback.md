# L5.24 Microsoft Edge supervised launch live-start preflight CLI/readback

L5.24 exposes the accepted L5.23 Microsoft Edge live-start preflight contract through a passive CLI/readback command.

Microsoft Edge first. Opera second.

This is still not the live launch patch. It does not start Edge.

## CLI commands

Source L5.23 preflight contract:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-preflight --repo-root C:\dev\patchops --json --compact
```

L5.24 preflight CLI/readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-preflight-readback --repo-root C:\dev\patchops --json --compact
```

Module readback:

```powershell
py -m patchops.llm_browser.live_adapter_edge_supervised_launch_live_start_preflight_cli_readback --repo-root C:\dev\patchops --json --compact
```

## What L5.24 checks

L5.24 checks that:

- L5.23 still reports PASS;
- L5.23 remains passive;
- the L5.23 source command remains registered;
- the L5.24 CLI/readback command is registered;
- required Edge L5 commands are present;
- required Edge L5 source/docs/tests are present;
- required docs contain the CLI/readback boundary;
- the L5.24 command plan is readback-only;
- adapter logic executes no validation commands;
- explicit operator authorization required remains true;
- dedicated profile required remains true;
- default profile forbidden remains true;
- manual user login required remains true;
- silent auto-submit remains false;
- Microsoft Edge first remains true;
- Opera second remains true;
- no Selenium import occurs;
- no browser or adapter side effects occur.

## Preserved preflight gates

The readback keeps these future live-start gates visible:

- explicit operator authorization required;
- `--allow-live-start` authorization flag required;
- `--profile-dir` dedicated profile argument required;
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

`L5.25 Live adapter Microsoft Edge supervised launch explicit authorization argument gate`