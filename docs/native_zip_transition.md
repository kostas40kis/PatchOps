# Native Zip Transition

## Purpose

This note records the exact point where the zip-first PatchOps workflow changes.

Before this patch series finished:
- you manually unzipped bundles on the Desktop,
- you opened the extracted folder,
- and you ran the bundled `run_with_patchops.ps1`.

After this patch series finished:
- you no longer manually unzip bundles,
- PatchOps accepts the `.zip`,
- PatchOps extracts it,
- PatchOps finds and calls the bundled `.ps1`,
- and PatchOps still writes one canonical Desktop txt report.

## What changed

The native zip milestone proof is green.
That means the intended default operator flow is now raw-zip-first rather than extracted-folder-first.

The maintained operator flow is:

1. receive one zip bundle,
2. do not manually extract it,
3. run one PatchOps command or one-liner against the zip, for example:
   `py -m patchops.cli run-package "<bundle.zip>" --wrapper-root "C:\dev\patchops"`
4. let PatchOps extract the zip and invoke the bundled launcher,
5. read the outer canonical report first,
6. then read the inner report when the outer report points to it.

## What did not change

The older PatchOps surfaces still remain valid and supported:
- normal manifest-based `check`,
- normal manifest-based `inspect`,
- normal manifest-based `plan`,
- normal manifest-based `apply`,
- normal manifest-based `verify`,
- profiles,
- reporting,
- packet and handoff flow.

Zip support is additive.
It is a new execution surface, not a replacement for the existing manifest-driven flow.

## Launcher posture

Bundled launchers still need to stay thin and boring.
In other words, bundled launchers still need to stay thin and boring even though the workflow is now zip-native and more Python-owned.
PatchOps should own extraction, validation, reporting, and the reusable mechanics.
PowerShell should remain an operator boundary, not a second workflow engine.

The maintained launcher path is now Python-heavier:
- generate or normalize launchers through `build_patchops_bundle_launcher(...)`,
- use launcher heuristics for review,
- keep the root launcher wrapped safely,
- avoid adding reusable workflow logic directly to `.ps1`.

## Preflight and proof guidance

Before distributing or trusting a bundle:
- prefer `preflight_bundle_zip(...)` for early zip/bundle/launcher review,
- treat launcher heuristic findings as review signals rather than as target-project failures,
- keep proof expectations concrete:
  - raw zip only,
  - no manual unzip,
  - PatchOps extraction,
  - bundled launcher invocation,
  - outer/inner report chain visible,
  - one canonical Desktop txt report.

## Practical reading

If you are using the maintained zip-first workflow now, the default assumption is:
- start from the zip,
- let PatchOps do the extraction,
- let PatchOps call the internal `run_with_patchops.ps1`,
- and use the canonical report as the source of truth.
