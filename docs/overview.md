# Overview

## Purpose

PatchOps is a standalone wrapper / harness / patch-execution toolkit.
It owns how change is reviewed, applied, verified, reported, retried, and handed off.

Simple boundary:

- **PatchOps = how change is applied and evidenced**
- **target repo = what the change actually is**

PatchOps remains project-agnostic.
It should not absorb target-project business logic.

## Current maintained posture

PatchOps is in maintenance mode after the completed zip-first and Python-heavier streams.
The repository now has a maintained raw zip workflow, repo-owned operator helper surfaces, narrow bootstrap repair support, a repo-owned GitHub publish helper, and a canonical root launcher shape contract.

Current practical rule set:

- keep PowerShell thin,
- keep reusable mechanics in Python,
- preserve one canonical Desktop txt report,
- prefer narrow repair over redesign,
- use handoff for already-running work.

## Core maintained surfaces

Classic manifest workflow remains real:

- `check`
- `inspect`
- `plan`
- `apply`
- `verify`

Bundle workflow remains additive:

- `check-bundle`
- `run-package`
- bundle-entry from the bundled root launcher
- launcher review and bundle shape review

Operator-facing maintenance helpers also now exist for:

- emitted operator scripts,
- maintenance-gate execution,
- bootstrap repair when the normal CLI import chain is too broken,
- repo-owned GitHub publish flow,
- published-state snapshot and documentation refresh packets.

## Reading order

For first-read surfaces, start with:

1. `README.md`
2. `docs/operator_quickstart.md`
3. `docs/llm_usage.md`

Then use these deep-reference documents when you need more exact detail:

- `docs/examples.md`
- `docs/profile_system.md`
- `docs/manifest_schema.md`
- `docs/compatibility_notes.md`

## Evidence discipline

A patch is green only when:

- the relevant tests pass,
- the canonical report says PASS,
- the claimed scope matches the real change,
- and the repo is healthier, not merely different.
