# PatchOps bundle contract packet

This is the maintained LLM-facing packet for authoring a correct PatchOps bundle after the published post-maintenance refresh wave.

## Canonical bundle shape

Every normal bundle should use this exact root shape:

```text
<bundle-root>/
  manifest.json
  bundle_meta.json
  README.txt
  run_with_patchops.ps1
  content/
    ...
```

Required root entries:
- `manifest.json`
- `bundle_meta.json`
- `README.txt`
- `run_with_patchops.ps1`
- `content/`

## Maintained execution path

The maintained bundle workflow is:
- `make-bundle`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `bundle-doctor`
- `build-bundle`
- `make-proof-bundle`
- `run-package`
- `bundle-entry`

## Guardrails

- Keep PowerShell thin.
- Keep reusable mechanics in Python.
- Keep one canonical Desktop txt report.
- Command/doc alignment proof remains required.
- Do not claim success without the canonical Desktop txt report.
- Use `bundle-doctor` when diagnosing authoring problems.

## Launcher rule

The bundle root launcher remains `run_with_patchops.ps1`, and it should stay a thin compatibility shim that delegates into the maintained `bundle-entry` path rather than becoming a second workflow engine.

Guard against stray leading `/` or `\` characters before `param(...)` in `run_with_patchops.ps1`; treat that shape drift as a bundle authoring failure, not as a wrapper-runtime problem.

## Notes for maintainers and LLMs

- Prefer the published repo docs over scattered historical reports.
- Treat malformed bundle shape as an authoring failure, not as a reason to widen wrapper logic.
- When continuing work, repair only the first failing layer.
