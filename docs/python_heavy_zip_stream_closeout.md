# Python-Heavy Zip Stream Closeout

## Purpose

This note closes the Python-heavy zip-first stream in maintained documentation form.

It is written so a future operator or LLM can continue from repo truth without reconstructing the stream from chat history.

## Final maintained posture

PatchOps now has a real raw-zip-first execution path:

- PatchOps accepts a raw patch bundle zip directly.
- PatchOps extracts the zip into its runtime workspace.
- PatchOps validates the bundle before risky execution.
- PatchOps discovers and invokes a thin bundled launcher.
- PatchOps preserves the outer/inner report chain.
- One canonical Desktop txt report still remains required.

This is additive maintenance work.
It is not a redesign and it does not remove the classic manifest-driven surfaces.

## Operator flow

The maintained default is:

1. receive one zip bundle,
2. do not manually unzip it,
3. run:
   `py -m patchops.cli run-package "<bundle.zip>" --wrapper-root "C:\dev\patchops"`
4. read the outer run-package report first,
5. use the inner report path from the outer report when deeper evidence is needed.

## What is now more Python-owned

The shipped helper family now includes:

- `build_patchops_bundle_launcher(...)`
- launcher normalization / safe wrapping support
- `find_common_launcher_mistakes(...)`
- `preflight_bundle_zip(...)`
- `classify_bundle_run_failure(...)`
- `create_starter_bundle(...)`

These helpers move launcher generation, launcher review, preflight, classification, and starter bundle authoring further into Python while keeping PowerShell as a thin operator boundary.

## Launcher guidance

Bundled PowerShell launchers should stay thin, boring, and reviewable.

Preferred posture:
- generate or normalize launchers through Python-owned helpers,
- keep the root launcher safely wrapped,
- avoid fragile JSON handoff,
- avoid large inline Python emission,
- avoid making the launcher a second workflow engine.

Treat launcher heuristic output as a review aid, not as proof of target-project failure by itself.

## Preflight guidance

Before trusting a delivered bundle:
- review the bundle shape,
- prefer `preflight_bundle_zip(...)` for early validation and launcher audit,
- treat missing staged content or broken bundle layout as package-authoring failures,
- keep the first actually failing layer explicit in reports.

## Proof expectations

A real zip-first proof should show:
- raw zip input,
- PatchOps extraction,
- bundled launcher discovery,
- launcher invocation,
- inner report preservation,
- honest classification,
- green validation when the patch is accepted.

## Regression expectations

The zip path is additive.
Future work should continue to prove:
- classic `check`,
- classic `inspect`,
- classic `plan`,
- classic `apply`,
- classic `verify`,
- profiles,
- reporting,
- packet/handoff flow.

Do not trade away classic stability to widen the zip path.

## What this stream did not do

This stream did not redesign PatchOps.
It did not remove PowerShell.
It did not replace manifests with zip-only behavior.

PowerShell remains a thin boundary.
PatchOps remains the wrapper.
Reusable mechanics increasingly live in Python.
The maintained workflow still requires one canonical Desktop txt report as the operator-facing evidence artifact.

## Follow-on posture

The stream is closed as a maintained surface.

Normal next work should now be:
- narrow maintenance,
- evidence-first repairs,
- small additive improvements,
- or specifically queued follow-on work.

The explicitly queued follow-on idea to combine the outer run-package report and the inner apply report into one canonical artifact is still not implemented here.
