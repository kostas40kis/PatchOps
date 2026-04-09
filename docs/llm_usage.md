# LLM usage

When authoring PatchOps bundles, follow the maintained default workflow exactly.

## Required sequence
- use `make-bundle` to scaffold,
- edit `manifest.json`, `bundle_meta.json`, and `content/`,
- diagnose with `check-bundle`, `inspect-bundle`, `plan-bundle`, and `bundle-doctor`,
- build with `build-bundle`,
- execute with `run-package`,
- continue patch by patch from evidence in the canonical Desktop txt report.

## What not to do
- Do not invent extra launcher variants.
- Do not manually improvise zip structure.
- Do not skip the bundle-doctor review step when diagnosing authoring problems.
- Do not claim success without a report.
