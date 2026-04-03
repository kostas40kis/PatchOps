# LLM Usage Guide

This document is the core usage manual for future coding LLMs working inside PatchOps.

The main goal is simple:

help a future model become useful quickly **without rediscovering the architecture, mixing target-repo logic into PatchOps, or widening safe rerun paths into blind retries**.

---

## 1. How to read the project

Do not start by guessing from file names alone.

Read in this order:

1. `README.md`
2. `docs/project_status.md`
3. `docs/overview.md`
4. `docs/manifest_schema.md`
5. `docs/profile_system.md`
6. `docs/compatibility_notes.md`
7. `docs/failure_repair_guide.md`
8. `docs/examples.md`

After that, use the CLI discovery/help surfaces:

- `python -m patchops.cli profiles`
- `python -m patchops.cli examples`
- `python -m patchops.cli schema`
- `python -m patchops.cli doctor --profile trader`

## 2. What you are looking at

PatchOps is a standalone wrapper / harness / patch-execution toolkit.

It is not the trader engine.
It is not strategy logic.
It is not target-repo domain logic.

Its job is to standardize:

- manifest-driven patch execution
- profile-driven target-root and runtime resolution
- backup and write mechanics
- validation command execution
- stdout/stderr capture
- canonical report generation
- failure classification
- verify-only reruns
- wrapper-only repair guidance

Target repo = what changes  
PatchOps = how the change is applied, validated, and evidenced

Do not violate that boundary.

## 3. Current project posture

Treat the current repo as a maintained utility, not an early concept.

The initial buildout circle is complete enough that the correct next behavior is maintenance-mode discipline:

- keep the docs aligned
- keep examples current
- keep tests green
- avoid architecture drift
- prefer additive improvements over redesign

## 4. How to choose a profile

Use the smallest correct profile for the target repo.

Current supported profiles include:

- `trader`
- `generic_python`
- `generic_python_powershell`

Rules:

- use `trader` only when the target repo is the trader repo or trader-aligned workflow
- use `generic_python` for general Python targets
- use `generic_python_powershell` for mixed Python/PowerShell targets
- do not hardcode trader assumptions into the generic core

## 5. How to choose between apply and verify-only

Use `apply` when:
- the patch needs to write or rewrite files
- backups must be created
- the run is a real content-changing patch pass

Use `verify` when:
- the files are already written
- the main need is validation and a clean canonical report
- the original content likely succeeded but the wrapper/report side needs a narrow rerun

Do not widen a narrow rerun into a blind full retry without evidence.

## 6. What to trust first

When taking over the repo, trust these signals first:

- full pytest
- `python -m patchops.cli profiles`
- `python -m patchops.cli examples`
- `python -m patchops.cli doctor --profile trader`
- `python -m patchops.cli plan .\examples\trader_first_verify_patch.json --mode verify`

If those are green, the core wrapper is probably healthy and the remaining work is likely maintenance or environment-specific rather than architectural.

## 7. What not to change casually

Do not casually redesign:

- the manifest system
- the profile system
- the one-report evidence model
- the wrapper-vs-target boundary
- verify-only semantics
- thin PowerShell launcher posture

These are part of the product identity.

## 8. How to think about docs and examples

Docs and examples are not optional decoration.

They are part of the handoff surface that makes PatchOps usable by future LLMs without tribal knowledge.

That means:

- keep README and project status current
- keep examples synchronized with the real workflow surface
- keep schema/profile docs accurate
- keep failure-repair guidance explicit
- keep shipped behavior clearly separated from optional future enhancements

## 9. How to think about Git warnings

If Git metadata is unavailable in a given environment, treat that as a traceability/hygiene concern unless there is evidence that the wrapper itself depends on Git for a core workflow.

Do not widen a missing-Git warning into a false architecture crisis.

## 10. Bottom line

The correct ongoing use of PatchOps is:

- read the docs first
- choose the right profile
- generate or adapt a manifest
- run apply or verify-only intentionally
- trust the canonical report
- preserve the boundaries
- extend the system additively