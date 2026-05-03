# L1.15 Live adapter startup request L1 documentation freeze/readiness checkpoint

L1.15 is a documentation freeze/readiness checkpoint for the L1 startup-request stack.

It does not start live browser work. It records that the L1 stack has reached a passive checkpoint after:

- the live adapter skeleton;
- passive startup-gate/readback surfaces;
- startup-request modelling;
- startup-request CLI flags;
- startup-request contract gates;
- startup-request fixture matrix;
- fixture-matrix contract gate;
- L1 aggregate readiness gate;
- PatchOps CLI readback for the L1 aggregate readiness gate.

## Passive-only boundary

This checkpoint is passive-only:

- no Selenium import;
- no browser start;
- no browser session creation;
- no click/download/paste/send/package-run side effect;
- no automatic git commit;
- no automatic git push.

The checkpoint module verifies that the aggregate readiness gate still reports PASS, startup remains blocked, browser/session creation remains false, and side effects performed remain an empty JSON array.

## Readback

```powershell
py -m patchops.llm_browser.live_adapter_startup_request_l1_documentation_checkpoint --repo-root C:\dev\patchops --json --compact
py -m patchops.llm_browser.live_adapter_startup_request_l1_documentation_checkpoint --repo-root C:\dev\patchops
```

## Next patch

L1.16 Live adapter startup request L1 broad validation checkpoint

## L1.15a runner phrase repair

L1.15a keeps the L1.15 documentation-freeze/readiness checkpoint passive-only and repairs a brittle runner-document phrase check. The checkpoint now accepts the command family:

```powershell
py -m patchops.llm_browser.live_adapter_startup_request_l1_documentation_checkpoint --json --compact
py -m patchops.llm_browser.live_adapter_startup_request_l1_documentation_checkpoint --repo-root C:\dev\patchops --json --compact
```

The repair performs no Selenium import, no browser start, no browser session creation, and no click/download/paste/send/package-run side effect.
