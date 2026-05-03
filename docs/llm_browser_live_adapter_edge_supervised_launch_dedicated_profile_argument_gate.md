# L5.26 Microsoft Edge supervised launch dedicated profile argument gate

L5.26 adds a passive Microsoft Edge supervised-launch gate for the dedicated profile argument. It reads back the accepted L5.25 authorization gate and exposes whether the operator supplied `--profile-dir`.

Microsoft Edge first. Opera second.

This is still not the live launch patch. It does not start Edge and it does not create the profile directory.

## CLI commands

Source L5.25 authorization gate:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-authorization-gate --repo-root C:\dev\patchops --allow-live-start --json --compact
```

L5.26 profile gate without a profile argument:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-profile-gate --repo-root C:\dev\patchops --allow-live-start --json --compact
```

L5.26 profile gate with a dedicated profile argument:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-profile-gate --repo-root C:\dev\patchops --allow-live-start --profile-dir C:\dev\patchops\data\runtime\browser_profiles\edge_l5_26_candidate --json --compact
```

Module readback:

```powershell
py -m patchops.llm_browser.live_adapter_edge_supervised_launch_dedicated_profile_argument_gate --repo-root C:\dev\patchops --allow-live-start --profile-dir C:\dev\patchops\data\runtime\browser_profiles\edge_l5_26_candidate --json --compact
```

## Dedicated profile gate behavior

The dedicated profile flag is:

```text
--profile-dir
```

The gate reports:

- dedicated profile argument required;
- dedicated profile argument present;
- missing profile keeps startup blocked;
- default profile forbidden;
- default profile path rejected;
- dedicated profile present is still blocked by the current passive phase.

In L5.26, `--profile-dir` is parsed and read back, but it still cannot start Edge. It only proves that the future live-start command has a clear dedicated-profile surface.

## Preserved live-start gates

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

`L5.27 Live adapter Microsoft Edge supervised launch default profile rejection gate`