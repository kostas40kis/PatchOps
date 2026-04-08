PatchOps maintained example bundle
=================================

This is the maintained generic apply example bundle.

Workflow
1. `py -m patchops.cli bundle-doctor examples/bundles/generic_apply_bundle`
2. `py -m patchops.cli build-bundle examples/bundles/generic_apply_bundle --output generic_apply_bundle.zip`
3. `py -m patchops.cli run-package generic_apply_bundle.zip --wrapper-root C:\dev\patchops`
