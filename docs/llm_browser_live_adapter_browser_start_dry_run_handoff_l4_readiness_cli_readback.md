# L4.8 Live adapter browser-start dry-run handoff L4 aggregate readiness gate CLI/readback

This patch adds the passive CLI/readback wrapper for the accepted L4 aggregate readiness gate.

Command added:

```text
py -m patchops.cli llm-browser browser-start-dry-run-handoff-l4-readiness --repo-root . --json --compact
```

The command only forwards to `patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate`.
It does not perform live browser automation.

Required passive guarantees:

- dry-run-only readback;
- no Selenium import;
- no browser start;
- no browser session creation;
- no profile directory creation;
- no adapter filesystem writes;
- no click/download/paste/send/package-run side effect;
- no commit or push.

Accepted source stack checked by this readback:

- L4.1 dry-run handoff contract;
- L4.3 dry-run handoff fixture matrix;
- L4.5 dry-run handoff contract gate;
- L4.7 dry-run handoff L4 aggregate readiness gate.

Next patch: L4.9 Live adapter browser-start dry-run handoff L4 documentation freeze/readiness checkpoint.
