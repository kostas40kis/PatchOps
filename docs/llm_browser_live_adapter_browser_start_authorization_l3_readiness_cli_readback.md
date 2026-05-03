# L3.8 Live adapter browser-start authorization L3 aggregate readiness gate CLI/readback

This patch adds the passive CLI/readback wrapper for the accepted L3 aggregate readiness gate.

## Command

```powershell
py -m patchops.cli llm-browser browser-start-authorization-l3-readiness --repo-root C:\dev\patchops --json --compact
```

## Boundary

L3.8 remains passive. It forwards to `patchops.llm_browser.live_adapter_browser_start_authorization_l3_aggregate_readiness_gate` and does not authorize or perform live startup work.

Required invariants:

- no Selenium import;
- no browser start;
- no browser session creation;
- no profile directory creation;
- no adapter filesystem writes;
- no click/download/paste/send/package-run side effect from adapter logic;
- no commit or push.

## Next patch

If accepted, continue with `L3.9 Live adapter browser-start authorization L3 documentation freeze/readiness checkpoint`.
