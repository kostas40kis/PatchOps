# LLM Browser Future Live-adapter Development Plan

This document defines the next development stream after the dry-mode closeout.

The dry-mode browser-runner stream is closed for operator validation. A future live adapter must be developed as a separate stream. It must not silently expand dry-mode code into unattended browser automation.

## Goal

Build a future operator-controlled live adapter that can eventually perform a narrow browser loop only after explicit gates are implemented, tested, documented, and accepted one-by-one.

The goal is not to create an unattended bot.

## Non-goals

The future live-adapter stream must not add:

- automatic send;
- automatic composer submission;
- unattended background work;
- localhost service;
- browser extension;
- hidden browser automation;
- automatic git commit;
- automatic git push;
- live PatchOps package execution without an explicit gate;
- download click without an explicit gate;
- composer paste without an explicit gate.

## Required gate model

Every live side-effect must have its own explicit gate.

Required gates:

1. live browser startup gate;
2. page readiness gate;
3. latest assistant reply detection gate;
4. artifact candidate detection gate;
5. download click gate;
6. download stabilization gate;
7. PatchOps package execution gate;
8. canonical report detection gate;
9. pasteback summary construction gate;
10. composer paste gate;
11. final send/submit gate.

The final send/submit gate remains unsupported until a separate explicit safety design exists.

## Safety invariants

These invariants must remain true across the future stream:

- dry-run mode remains available;
- dry-run mode performs no side effects;
- auto-send remains unsupported;
- live side effects are disabled by default;
- every live side effect is opt-in;
- every live side effect is auditable;
- every live side effect has tests;
- every live side effect has operator docs;
- every report writes to a predictable local report path;
- every broad validation path has a timeout;
- failure is fail-closed;
- ambiguous state is fail-closed.

## Patch sequence

### L1 live adapter skeleton

Add a live adapter interface with no side effects.

Acceptance:

- imports without Selenium if optional deps are absent;
- no browser starts;
- tests prove side-effect methods are not called;
- docs say this is a skeleton only.

### L2 browser startup gate

Add an explicit gate for starting Edge or Opera in a controlled automation profile.

Acceptance:

- gate defaults to disabled;
- `--live-start-browser` or equivalent explicit opt-in is required;
- no download, paste, or send is possible;
- browser path/profile errors are reported cleanly;
- tests can mock the browser factory.

### L3 page readiness live read gate

Read the live page state after browser startup.

Acceptance:

- no clicking;
- no download;
- no paste;
- no send;
- timeout and failure reason are reported;
- saved HTML snapshot path remains available for reproduction.

### L4 latest assistant reply live detection

Detect the latest assistant reply in the live page.

Acceptance:

- no side effects;
- no clicking;
- no package execution;
- no paste/send;
- audit event records the detected state.

### L5 download click gate

Add explicit opt-in for clicking a PatchOps zip artifact candidate.

Acceptance:

- only `.zip` PatchOps bundle candidates are eligible;
- already processed artifacts are skipped;
- click action requires explicit gate;
- download directory is controlled;
- download stabilization must pass before continuing;
- audit log records candidate filename and hash when available.

### L6 PatchOps execution gate

Add explicit opt-in for invoking `py -m patchops.cli run-package`.

Acceptance:

- command is rendered before execution;
- wrapper root is explicit;
- timeout exists;
- stdout/stderr are captured;
- JSON payload is parsed;
- `ok=false` is fail-closed even when process exit code is zero.

### L7 canonical report gate

Find and parse the canonical report from the PatchOps run.

Acceptance:

- missing report is fail-closed;
- stale report is rejected;
- result/exit code/failure category are captured;
- report path is written into audit log.

### L8 pasteback construction gate

Construct the response text from canonical report evidence.

Acceptance:

- no composer paste;
- no send;
- generated text includes result, patch name, report path, and next action;
- tests cover PASS, FAIL, and ambiguous states.

### L9 composer paste gate

Add explicit opt-in for pasting into the composer.

Acceptance:

- paste is disabled by default;
- paste target readiness is verified;
- paste result is audited;
- no send/submit is possible.

### L10 send/submit safety design only

Do not implement sending.

Acceptance:

- docs describe why send/submit remains unsupported;
- CLI has no `--auto-send` or `--allow-send`;
- tests assert send flags are absent.

## Validation strategy

Each live-adapter patch must run:

- focused unit tests for the new gate;
- regression tests for all previous dry-mode gates;
- release-gate smoke;
- checkpoint smoke;
- broad-report parser smoke;
- relevant docs-contract tests.

Before any live side effect is accepted, the operator must be able to run:

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_broad_validation.ps1 -RepoRoot C:\dev\patchops
```

The final closeout checkpoint remains:

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_closeout_validation_push_checkpoint.ps1 -RepoRoot C:\dev\patchops
```

## Report-location rule

Future live-adapter reports must use the same operator report convention:

```text
%USERPROFILE%\Desktop\patchops_reports\
%USERPROFILE%\Desktop\patchops_latest_llm_browser_broad_validation_report.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_closeout_checkpoint.txt
```

Any new live-adapter report must either use this folder or create a Desktop pointer file to the actual report path.

## Audit-log rule

Every future live-adapter gate must append a compact audit event when audit logging is enabled.

The event must include:

- event type;
- timestamp;
- source;
- state;
- planned actions;
- side effects performed;
- artifact filename when applicable;
- artifact hash when applicable;
- report path when applicable;
- failure reason when applicable.

## Commit and push rule

Future patch scripts must not run git commit or git push automatically.

Operator scripts may print manual commands, but actual commit/push remains operator-controlled.

## Closeout rule

The live-adapter stream is not complete until:

- broad validation passes;
- closeout checkpoint passes;
- docs name what is shipped and what is not shipped;
- the final report path is easy to find from Desktop;
- the operator explicitly commits and pushes.
