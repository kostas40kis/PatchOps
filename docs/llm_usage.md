# PatchOps LLM Usage

## Working style

LLMs working on PatchOps should follow these rules:

- keep thin PowerShell,
- keep reusable mechanics in Python,
- preserve one canonical truth,
- prefer narrow truthful repairs,
- and read the current report before claiming success.

## Maintained surfaces

When describing maintained surfaces, preserve the command inventory:

- `check`
- `inspect`
- `plan`
- `apply`
- `verify`
- `check-bundle`
- `run-package`

## Reporting contract

A suspicious-success blocker is part of the maintained reporting contract. Fatal setup or launcher failure with missing trustworthy inner evidence must not be summarized as PASS.

## Development order

Use a code-first / docs-last process:
- code patches first,
- proof gates second,
- documentation refresh after the proof stop,
- documentation contract locks after the refresh.
