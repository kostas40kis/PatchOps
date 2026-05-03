# L5.12 Microsoft Edge supervised launch readiness contract

L5.12 introduces the Microsoft Edge supervised-launch readiness contract. It is still passive and model/readback-only.

Microsoft Edge first. Opera second.

The contract records the rules the future live Edge launch must obey before any actual browser startup is allowed.

## CLI/readback command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-readiness --repo-root C:\dev\patchops --json --compact
```

Module readback:

```powershell
py -m patchops.llm_browser.live_adapter_edge_supervised_launch_readiness_contract --repo-root C:\dev\patchops --json --compact
```

## Relationship to L5.11

L5.12 depends on the accepted L5.11 CLI/readback surface. L5.11 proved the L5 broad-validation checkpoint can be read through the main `llm-browser` command surface while preserving the passive boundary.

## Edge readiness rules

The future live Edge launch must preserve these operator boundaries:

- dedicated profile required;
- default browser profile is forbidden by default;
- manual user login required;
- silent auto-submit remains false;
- no localhost PatchOps server;
- no browser extension;
- no hidden background web service.

## Passive safety boundary for this patch

This patch does not perform live browser automation.

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

`L5.13 Live adapter Microsoft Edge supervised launch readiness CLI/readback`