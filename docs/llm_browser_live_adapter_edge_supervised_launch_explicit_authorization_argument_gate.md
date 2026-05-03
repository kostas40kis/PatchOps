# L5.25 Microsoft Edge supervised launch explicit authorization argument gate

L5.25 adds a passive Microsoft Edge supervised-launch argument gate for explicit operator authorization. It reads back the accepted L5.24 preflight CLI/readback and exposes whether the operator supplied `--allow-live-start`.

Microsoft Edge first. Opera second.

This is still not the live launch patch. It does not start Edge.

## CLI commands

Source L5.24 preflight CLI/readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-preflight-readback --repo-root C:\dev\patchops --json --compact
```

L5.25 authorization gate without explicit authorization:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-authorization-gate --repo-root C:\dev\patchops --json --compact
```

L5.25 authorization gate with explicit authorization:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-authorization-gate --repo-root C:\dev\patchops --allow-live-start --json --compact
```

Module readback:

```powershell
py -m patchops.llm_browser.live_adapter_edge_supervised_launch_explicit_authorization_argument_gate --repo-root C:\dev\patchops --json --compact
```

## Authorization gate behavior

The explicit authorization flag is:

```text
--allow-live-start
```

The gate reports:

- explicit operator authorization required;
- explicit operator authorization present;
- authorization missing keeps startup blocked;
- authorization present is still blocked by the current passive phase.

In L5.25, `--allow-live-start` is parsed and read back, but it still cannot start Edge. It only proves that the future live-start command has a clear authorization surface.

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

`L5.26 Live adapter Microsoft Edge supervised launch dedicated profile argument gate`