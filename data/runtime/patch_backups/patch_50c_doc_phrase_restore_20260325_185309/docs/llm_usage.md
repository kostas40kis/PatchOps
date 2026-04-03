# LLM Usage Guide

PatchOps is a standalone wrapper / harness / patch-execution toolkit.

Target repo = what changes
PatchOps = how the change is applied, validated, and evidenced

Treat the repo as a maintained utility, not an early concept.

Trust these signals first:

- full pytest
- `python -m patchops.cli profiles`
- `python -m patchops.cli examples`
- `python -m patchops.cli doctor --profile trader`
- `python -m patchops.cli plan .\examples\trader_first_verify_patch.json --mode verify`