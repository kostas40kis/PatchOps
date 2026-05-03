# L5.15 Microsoft Edge supervised launch fixture matrix CLI/readback

L5.15 adds the dedicated CLI/readback layer for the accepted L5.14 Microsoft Edge supervised launch fixture matrix.

Microsoft Edge first. Opera second.

## CLI commands

L5.14 source fixture command:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-fixtures --repo-root C:\dev\patchops --json --compact
```

L5.15 readback command:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-fixtures-readback --repo-root C:\dev\patchops --json --compact
```

Module readback:

```powershell
py -m patchops.llm_browser.live_adapter_edge_supervised_launch_fixture_matrix_cli_readback --repo-root C:\dev\patchops --json --compact
```

## What this proves

L5.15 proves that:

- L5.14 still reports `PASS`;
- the L5.14 Edge fixture command is still registered;
- the L5.15 Edge fixture readback command is registered;
- the six Edge fixture cases are still present;
- Microsoft Edge remains first;
- Opera remains second;
- dedicated profile required remains true;
- manual user login required remains true;
- silent auto-submit remains false;
- no localhost PatchOps server is required;
- no browser extension is required.

## Fixture cases preserved from L5.14

The readback preserves these passive fixture IDs:

- `edge_future_launch_user_visible`;
- `edge_dedicated_profile_required`;
- `edge_manual_login_required`;
- `edge_no_silent_auto_submit`;
- `edge_no_extension_no_localhost`;
- `edge_no_current_side_effects`.

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

`L5.16 Live adapter Microsoft Edge supervised launch fixture matrix contract gate`