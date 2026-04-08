# PatchOps LLM usage notes

For the standardized bundle workflow, future sessions should not improvise launcher structure or zip nesting.

## Use this flow

1. scaffold with `py -m patchops.cli make-bundle ...`
2. edit `manifest.json`, `bundle_meta.json`, and `content/`
3. diagnose with `py -m patchops.cli bundle-doctor <bundle-root>`
4. build with `py -m patchops.cli build-bundle <bundle-root> --output <zip>`
5. execute with `py -m patchops.cli run-package <zip> --wrapper-root C:\dev\patchops`
6. continue patch by patch from the canonical Desktop txt report

## Maintained examples

Treat these as the maintained example bundles:

- `examples/bundles/generic_apply_bundle`
- `examples/bundles/generic_verify_bundle`

They show the canonical one-launcher, metadata-driven mode workflow.
