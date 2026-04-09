# Self-hosted bundle authoring proof

From Patch 12 onward, the standardized bundle workflow is proven against PatchOps itself.

The proof path is intentionally the same one operators and future LLM sessions are expected to use:

1. scaffold a PatchOps-targeted proof bundle from Python,
2. check it with `bundle-doctor`,
3. build the zip from Python,
4. review the resulting zip,
5. execute the bundle through `run-package`,
6. read one canonical report.

## What this proof demonstrates

- PatchOps can generate a self-hosted proof bundle without hand-authoring launcher structure.
- The generated bundle targets `C:/dev/patchops` using the canonical root layout.
- `bundle-doctor` accepts the generated bundle as a valid maintained bundle.
- `build-bundle` produces a one-root deterministic zip.
- `inspect-bundle` and `plan-bundle` succeed on the built proof zip.
- The actual patch bundle used for this proof is itself executed through `run-package`, which provides the canonical self-hosted report artifact.

## Maintained command sequence

```text
py -m patchops.cli make-proof-bundle --kind apply ...
py -m patchops.cli bundle-doctor <bundle-root>
py -m patchops.cli build-bundle <bundle-root> --output <zip>
py -m patchops.cli inspect-bundle <zip>
py -m patchops.cli plan-bundle <zip>
py -m patchops.cli run-package <zip> --wrapper-root C:\dev\patchops
```

This is now the maintained self-hosted proof path for PatchOps bundle work.
