# L4.11 Live adapter browser-start dry-run handoff L4 broad validation checkpoint CLI/readback

This patch adds the passive CLI/readback wrapper for the accepted L4 broad validation checkpoint.

Command added:

```text
py -m patchops.cli llm-browser browser-start-dry-run-handoff-l4-broad-validation --repo-root . --json --compact
```

The command only forwards to `patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_broad_validation_checkpoint`.
It does not perform live browser automation and does not execute the checkpoint command plan.

Required passive guarantees:

- broad-validation readback only;
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
- L4.7 aggregate readiness gate;
- L4.8 aggregate readiness gate CLI/readback;
- L4.9 documentation freeze/readiness checkpoint;
- L4.10 broad validation checkpoint.

Next patch: L4.12 Live adapter browser-start dry-run handoff L4 final acceptance marker.
