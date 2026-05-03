# L5.17 Microsoft Edge supervised launch fixture matrix contract gate CLI/readback

L5.17 adds the dedicated CLI/readback layer for the accepted L5.16 Microsoft Edge supervised launch fixture matrix contract gate.

Microsoft Edge first. Opera second.

## CLI commands

L5.16 source contract gate command:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-fixtures-contract-gate --repo-root C:\dev\patchops --json --compact
```

L5.17 readback command:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-fixtures-contract-gate-readback --repo-root C:\dev\patchops --json --compact
```

Module readback:

```powershell
py -m patchops.llm_browser.live_adapter_edge_supervised_launch_fixture_matrix_contract_gate_cli_readback --repo-root C:\dev\patchops --json --compact
```

## Relationship to L5.16

L5.16 proved that the Edge fixture matrix contract gate passes and that the six Edge fixture cases still block live side effects. L5.17 makes that gate available through its own passive CLI/readback checkpoint.

## Contract gate summary preserved from L5.16

The readback preserves these passive fixture IDs:

- `edge_future_launch_user_visible`;
- `edge_dedicated_profile_required`;
- `edge_manual_login_required`;
- `edge_no_silent_auto_submit`;
- `edge_no_extension_no_localhost`;
- `edge_no_current_side_effects`.

The readback also preserves these contract gate boundaries:

- Microsoft Edge first;
- Opera second;
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
- no adapter filesystem writes;
- no click/download/paste/send/package-run side effect;
- no automatic git commit;
- no automatic git push.

## Next patch

If accepted, continue with:

`L5.18 Live adapter Microsoft Edge supervised launch L5 aggregate readiness gate`