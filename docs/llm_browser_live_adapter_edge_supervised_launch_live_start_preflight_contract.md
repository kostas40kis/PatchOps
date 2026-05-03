# L5.23 Microsoft Edge supervised launch live-start preflight contract

L5.23 defines the passive preflight contract for a future real, user-visible Microsoft Edge supervised launch.

Microsoft Edge first. Opera second.

This is still not the live launch patch. It does not start Edge.

## CLI commands

Source L5.22 broad validation CLI/readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-l5-broad-validation-readback --repo-root C:\dev\patchops --json --compact
```

L5.23 live-start preflight contract:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-preflight --repo-root C:\dev\patchops --json --compact
```

Module readback:

```powershell
py -m patchops.llm_browser.live_adapter_edge_supervised_launch_live_start_preflight_contract --repo-root C:\dev\patchops --json --compact
```

## What L5.23 checks

L5.23 checks that:

- L5.22 still reports PASS;
- L5.22 remains passive;
- the L5.22 source command remains registered;
- the L5.23 live-start preflight command is registered;
- required Edge L5 commands are present;
- required Edge L5 source/docs/tests are present;
- required docs contain the preflight boundary;
- the live-start preflight contract is explicit;
- explicit operator authorization required remains true;
- dedicated profile required remains true;
- default profile forbidden remains true;
- manual user login required remains true;
- silent auto-submit remains false;
- no localhost PatchOps server is required;
- no browser extension is required;
- Selenium is not imported by readback;
- no browser or adapter side effects occur.

## Live-start preflight contract

The future live-start path must not happen unless all of these are true:

- explicit operator authorization required;
- `--allow-live-start` style authorization flag required;
- `--profile-dir` style dedicated profile argument required;
- dedicated profile required;
- default profile forbidden;
- manual user login required;
- silent auto-submit remains false;
- Microsoft Edge first;
- Opera second;
- no localhost PatchOps server;
- no browser extension.

The future Edge executable candidates are documented but not probed as a hard requirement in this patch:

- `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
- `C:\Program Files\Microsoft\Edge\Application\msedge.exe`

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

`L5.24 Live adapter Microsoft Edge supervised launch live-start preflight CLI/readback`