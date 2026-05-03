# L5.16 Microsoft Edge supervised launch fixture matrix contract gate

L5.16 adds the contract gate for the accepted L5.15 Microsoft Edge supervised launch fixture matrix CLI/readback.

Microsoft Edge first. Opera second.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-fixtures-contract-gate --repo-root C:\dev\patchops --json --compact
```

Source readback command from L5.15:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-fixtures-readback --repo-root C:\dev\patchops --json --compact
```

Module readback:

```powershell
py -m patchops.llm_browser.live_adapter_edge_supervised_launch_fixture_matrix_contract_gate --repo-root C:\dev\patchops --json --compact
```

## Relationship to L5.15

L5.15 proved that the Edge fixture matrix can be read through a dedicated passive CLI/readback command. L5.16 turns those fixture expectations into a contract gate.

## Contract gate requirements

The gate requires the six Edge fixture cases to remain present:

- `edge_future_launch_user_visible`;
- `edge_dedicated_profile_required`;
- `edge_manual_login_required`;
- `edge_no_silent_auto_submit`;
- `edge_no_extension_no_localhost`;
- `edge_no_current_side_effects`.

The gate also requires these boundaries to remain true:

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

`L5.17 Live adapter Microsoft Edge supervised launch fixture matrix contract gate CLI/readback`