# PatchOps

PatchOps is a project-agnostic patch execution harness for Windows-first patch workflows.

It keeps target-repo business logic separate from wrapper mechanics and standardizes:

- manifest-driven patch execution
- profile-aware defaults
- deterministic backups
- explicit file writes
- process execution with stdout/stderr capture
- canonical single-report evidence
- wrapper-vs-target failure separation
- narrow reruns such as verify-only and wrapper-only repair paths

## Current status

PatchOps has completed its initial buildout circle and is now operating as a maintained reusable utility.

The initial milestone is no longer a vague concept or a partial prototype.
The core wrapper surface is present, the tests are green, the main workflows are covered, and the remaining work is maintenance-mode alignment rather than architecture discovery.

This patch refresh completes the Documentation Stop H handoff posture by making the main status and usage docs reflect the repo's real state.

## What PatchOps is

PatchOps is the wrapper layer that owns how patches are applied, validated, and evidenced.

It owns:

- manifest loading and validation
- profile-driven target-root and runtime resolution
- backup mechanics
- file-writing mechanics
- command execution
- stdout/stderr capture
- report generation
- failure classification
- verify-only reruns
- wrapper-only retry/repair support
- maintenance flows such as cleanup and archive
- future-LLM-friendly examples and docs

## What PatchOps is not

PatchOps is not:

- trader strategy logic
- trader portfolio logic
- exchange logic
- execution engine business logic
- target-repo domain logic

Target repo = what changes  
PatchOps = how the change is applied, validated, and evidenced

That boundary remains non-negotiable.

## Stable workflow contracts

The maintained core contracts are:

- explicit workspace, wrapper, and target roots
- explicit active profile
- explicit runtime/interpreter path
- manifest-driven behavior rather than hidden guessing
- explicit backup behavior
- explicit file-write behavior
- full stdout/stderr capture
- one canonical Desktop txt report per run
- wrapper-vs-target failure separation
- narrow rerun modes instead of blind full retries

## Shipped workflow classes

PatchOps now supports the main intended workflow classes:

- code patch flow
- documentation patch flow
- validation patch flow
- cleanup flow
- archive flow
- verification-only rerun flow

## Supported profiles

The currently maintained profile surface includes:

- trader
- generic_python
- generic_python_powershell

Trader is the first real target profile, not the identity of the system.

## CLI surface

The main CLI surface now includes:

- apply
- verify
- inspect
- check
- plan
- profiles
- template
- doctor
- examples
- schema

## Maintenance-mode posture

PatchOps should now be treated as a maintained wrapper utility.

That means:

- do not redesign the manifest system without evidence
- do not redesign the profile system just because future work exists
- do not blur target-repo logic into the wrapper core
- keep PowerShell thin and conservative
- preserve the one-report evidence contract
- prefer additive improvements over architecture churn

## Current near-term focus

The near-term focus is simple:

- keep the status/handoff docs aligned with the real repo state
- keep examples current
- preserve test coverage around the main contracts
- keep Git/traceability hygiene visible as an environment concern rather than a core product failure

## Optional future enhancements

These are valid future improvements, but they are not proof that the initial product is incomplete:

- richer profile ecosystem
- more ergonomic manifest authoring
- stronger dry-run introspection
- richer artifact preservation and summaries
- broader language/repo support
- stronger fixture repos for integration tests
- additional launcher conveniences

## Bottom line

PatchOps is now a real reusable wrapper with stable core architecture.

The correct posture is:

- maintain the docs
- preserve the contracts
- extend additively
- avoid drift