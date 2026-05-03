# L5.18 Microsoft Edge supervised launch L5 aggregate readiness gate

L5.18 adds the Microsoft Edge supervised launch L5 aggregate readiness gate.

Microsoft Edge first. Opera second.

The gate aggregates the accepted Edge-first stream from L5.12 through L5.17 and keeps the earlier L5.11 broad validation readback in the chain.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-l5-readiness --repo-root C:\dev\patchops --json --compact
```

Module readback:

```powershell
py -m patchops.llm_browser.live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate --repo-root C:\dev\patchops --json --compact
```

## Aggregated patches

The aggregate readiness gate checks:

- L5.11 — supervised-launch L5 broad validation CLI/readback;
- L5.12 — Microsoft Edge supervised launch readiness contract;
- L5.13 — Microsoft Edge readiness CLI/readback;
- L5.14 — Microsoft Edge supervised launch fixture matrix;
- L5.15 — Microsoft Edge fixture matrix CLI/readback;
- L5.16 — Microsoft Edge fixture matrix contract gate;
- L5.17 — Microsoft Edge fixture matrix contract gate CLI/readback.

## Contract boundaries preserved

The aggregate gate preserves these Edge-first boundaries:

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

`L5.19 Live adapter Microsoft Edge supervised launch L5 aggregate readiness gate CLI/readback`

## L5.18a repair note

L5.18a repairs the aggregate gate module readback by using the accepted L5.11 builder name `build_l5_broad_validation_cli_readback`. The behavior remains passive: no Selenium import, no browser start, no Edge process start, no profile directory creation, and no click/download/paste/send/package-run side effect.

## L5.18b repair note

L5.18b repairs the aggregate passive-state compatibility check for the accepted L5.11 readback. L5.11 predates the Edge-specific `edge_process_started` field, so the L5.18 aggregate gate now treats that missing legacy field as passive false while still failing any explicit true value. The patch remains passive: no Selenium import, no browser start, no Edge process start, no profile directory creation, and no click/download/paste/send/package-run side effect.

