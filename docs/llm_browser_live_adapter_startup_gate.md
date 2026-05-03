# L1.4 Live adapter explicit startup gate scaffold

L1.4 adds a passive startup gate scaffold for the future live-adapter stream.
It is still **not** live browser automation.

The module is:

```text
patchops/llm_browser/live_adapter_startup_gate.py
```

The passive readback command is:

```powershell
py -m patchops.llm_browser.live_adapter_startup_gate --json --compact
```

Required contract:

```text
startup_allowed: false
browser_started: false
browser_session_created: false
side_effects_performed: []
optional_browser_dependencies_required: false
```

## Safety boundary

L1.4 keeps the same D-to-L boundary:

- no Selenium import;
- no browser starts;
- no browser session is created;
- no click/download/paste/send/package-run side effects occur;
- no commit or push is performed;
- manual login only remains the future browser posture;
- no auto-send remains the future safety default;
- visible artifact only remains the future artifact rule;
- PatchOps remains the source of truth for package execution and reports.

## Explicit acknowledgements reserved for later phases

The startup request model names the acknowledgements a later live startup phase
must require:

```text
operator_confirms_dedicated_browser_profile
operator_confirms_manual_login_only
operator_confirms_no_auto_send
operator_confirms_visible_artifact_only
operator_confirms_patchops_remains_source_of_truth
```

Even when all acknowledgements and permissive flags are true, L1.4 returns
`startup_allowed: false`. The scaffold is blocked by:

```text
l1_4_scaffold_does_not_start_browsers
live_browser_startup_requires_a_later_explicit_phase
selenium_dependency_boundary_is_not_enabled_here
```

## Next patch

Next patch: **L1.5 Live adapter startup gate CLI/readback**.

<!-- PATCHOPS_L1_04C_STARTUP_GATE_JSON_CLI_REPAIR_START -->

## L1.4c JSON CLI repair

L1.4c repairs the passive startup gate module command so:

```powershell
py -m patchops.llm_browser.live_adapter_startup_gate --json --compact
```

reads the real command-line arguments and emits compact JSON instead of text readback.
The repair does not import Selenium, start a browser, click, download, paste, send,
run PatchOps packages from the adapter, commit, or push.

<!-- PATCHOPS_L1_04C_STARTUP_GATE_JSON_CLI_REPAIR_END -->

## L1.5 CLI/readback surface

The startup gate can now be read through the main PatchOps CLI without enabling live automation:

```powershell
py -m patchops.cli llm-browser startup-gate --json --compact
```

This command must remain equivalent to the module readback and must keep startup blocked until a later explicit live-browser phase.
## L1.6 request-model boundary

The startup gate now has a neighboring passive request model in `patchops.llm_browser.live_adapter_startup_request`. The model records future startup intent and evaluates it without importing Selenium or starting a browser. It does not replace the existing startup gate; it prepares a stable request/decision payload for later CLI flag wiring.
