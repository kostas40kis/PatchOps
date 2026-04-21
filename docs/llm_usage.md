# PatchOps LLM Usage

This file is the orientation page for future coding LLMs.

## Bundle-first command order

Continue patch by patch from evidence.
Use this exact bundle command order when working in the current bundle flow:

1. `make-bundle`
2. `check-bundle`
3. `inspect-bundle`
4. `plan-bundle`
5. `bundle-doctor`
6. `build-bundle`
7. `run-package`

## Contract reminders

- thin PowerShell
- reusable mechanics in Python
- `run_with_patchops.ps1` is the maintained saved launcher name
- `bundle_mode` lives in metadata
- do not manually unzip during the normal operator path
