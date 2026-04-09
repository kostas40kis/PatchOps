# Bundle Contract Packet

## Purpose
This packet is the maintained bundle contract reference after the Patch 21-24 maintenance stream.
It exists so operators and future maintainers can see the real bundle workflow in one place without rediscovering it from reports.

## Canonical bundle root
The maintained bundle shape is:

```text
<bundle-root>/
  manifest.json
  bundle_meta.json
  README.txt
  run_with_patchops.ps1
  content/
    ...
```

`run_with_patchops.ps1` stays thin and operator-facing.
`bundle-entry` remains the Python-owned bridge used by the launcher.

## Maintained bundle commands
Use these commands as the normal bundle contract surface:

- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `bundle-doctor`
- `make-bundle`
- `build-bundle`
- `make-proof-bundle`
- `run-package`
- `bundle-entry`

## Maintained wrapper health and recovery commands
These are the narrow maintenance surfaces added in this stream:

- `maintenance-gate`
- `emit-operator-script`
- `bootstrap-repair`

## Classic manifest commands still preserved
The classic wrapper surfaces still matter and remain aligned with the docs:

- `check`
- `inspect`
- `plan`
- `apply`
- `verify`

## Command/doc alignment proof
The command names listed in this packet are intentionally the same names exposed by the maintained CLI parser.
Patch 24 keeps this packet under test so command/doc alignment proof remains automatic rather than aspirational.

## Operator rules
- Keep PowerShell thin.
- Keep reusable mechanics in Python.
- Keep one canonical Desktop txt report.
- Use bundle review surfaces before risky execution.
- Use `run-package` for the normal raw zip flow.
- Treat `bootstrap-repair` as a narrow recovery surface, not a second workflow engine.
