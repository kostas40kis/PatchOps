# L5.14 Microsoft Edge supervised launch fixture matrix

L5.14 adds the first Microsoft Edge supervised-launch fixture matrix.

Microsoft Edge first. Opera second.

The fixture matrix is still passive/model-only. It describes expected future Edge launch behavior without importing Selenium, starting Edge, creating profile directories, clicking downloads, pasting, sending, or running packages.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-fixtures --repo-root C:\dev\patchops --json --compact
```

Source readback command from L5.13:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-readiness-readback --repo-root C:\dev\patchops --json --compact
```

Module readback:

```powershell
py -m patchops.llm_browser.live_adapter_edge_supervised_launch_fixture_matrix --repo-root C:\dev\patchops --json --compact
```

## Relationship to L5.13

L5.14 depends on L5.13. L5.13 proved that the Microsoft Edge readiness readback command is registered and that the L5.12 Edge readiness contract remains passive and PASS.

## Fixture cases

The matrix contains these passive Edge cases:

- `edge_future_launch_user_visible` — future Edge launch is supervised and user-visible;
- `edge_dedicated_profile_required` — dedicated profile required and default browser profile forbidden;
- `edge_manual_login_required` — manual user login required and no credential handling by the adapter;
- `edge_no_silent_auto_submit` — silent auto-submit remains false;
- `edge_no_extension_no_localhost` — no localhost PatchOps server and no browser extension;
- `edge_no_current_side_effects` — current L5.14 performs no browser, profile, click/download, paste/send, package-run, commit, or push side effects.

## Passive safety boundary for this patch

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

`L5.15 Live adapter Microsoft Edge supervised launch fixture matrix CLI/readback`