# L1.16 Live adapter startup request L1 broad validation checkpoint

L1.16 adds a passive broad-validation checkpoint for the L1 live-adapter startup-request stack.

The checkpoint is a readback/planning surface only. It summarizes the L1 documentation-freeze checkpoint, the aggregate readiness gate, and the command plan an operator can use for broad validation. It does not run broad pytest automatically, does not run PatchOps packages from the adapter, and does not perform any browser or ChatGPT UI action.

## Passive boundary

This patch remains inside the L1 no-side-effect boundary:

- no Selenium import;
- no browser start;
- no browser session creation;
- no page read;
- no assistant-reply detection;
- no click/download;
- no PatchOps package execution from the adapter;
- no paste to composer;
- no send or submit;
- no git commit or git push.

The checkpoint reports `executed_validation_commands: []`. Its `broad_validation_commands` list is an operator readback plan, not an execution request.

## Readback command

```powershell
py -m patchops.llm_browser.live_adapter_startup_request_l1_broad_validation_checkpoint --repo-root "C:\dev\patchops" --json --compact
```

Text mode is also supported:

```powershell
py -m patchops.llm_browser.live_adapter_startup_request_l1_broad_validation_checkpoint --repo-root "C:\dev\patchops"
```

## Expected result

A passing payload has:

- `patch: L1.16`;
- `status: PASS`;
- `startup_allowed: false`;
- `browser_started: false`;
- `browser_session_created: false`;
- `side_effects_performed: []`;
- `executed_validation_commands: []`;
- a command plan that includes focused L1 pytest and full pytest as operator-run validation steps.

## Next patch

The next patch named by this checkpoint is **L1.17 Live adapter startup request L1 final acceptance marker**.
