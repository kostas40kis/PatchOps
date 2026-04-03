# PatchOps project status

## Stage 1 status

PatchOps now has a completed Stage 1 harness.

It is no longer just a working concept or a partial wrapper.
The core initial-buildout circle is complete in technical terms, and the repo should now be treated as a maintained reusable utility rather than a pre-milestone experiment.

The completed Stage 1 harness includes:

- manifest loading and validation
- profile resolution
- deterministic reporting
- backup and write helpers
- apply / verify / inspect / check / plan flows
- discovery commands:
  - profiles
  - examples
  - schema
- wrapper-vs-target failure separation
- wrapper-only retry guidance
- cleanup and archive workflow support
- end-to-end sample coverage
- initial milestone gate coverage

## Current maintenance-mode state

PatchOps is in maintenance-mode handoff cleanup.

That means:

- the core architecture is considered stable
- the main workflow classes are covered
- tests protect the main contracts
- docs and examples are the main remaining source of drift if they are not maintained
- the next changes should be additive, not architecture-breaking

## What is shipped

The currently shipped behavior includes:

### Core wrapper behavior
- manifest loading
- manifest validation
- profile-driven target root resolution
- explicit runtime/interpreter resolution
- deterministic backup behavior
- deterministic file-writing behavior
- process execution with stdout/stderr capture
- report rendering with final ExitCode / Result summary
- failure classification
- verify-only reruns
- wrapper-only retry support

### Supported profiles
- trader
- generic_python
- generic_python_powershell

### Supported workflow classes
- apply
- documentation
- validation
- verify-only
- cleanup
- archive

### Handoff surface
- README
- overview docs
- schema/profile docs
- compatibility and failure-repair docs
- examples docs
- project status docs
- trader-facing usage docs
- patch ledger and stage checklists

## What is not being redesigned

The following are considered stable enough that they should not be redesigned casually:

- manifest model
- profile system
- report contract
- execution model
- rerun model
- thin PowerShell launcher posture
- wrapper/target boundary

## What still needs discipline

The main discipline requirements going forward are:

- keep the docs aligned with shipped behavior
- keep examples current with the schema and workflow surface
- keep the one-report evidence model intact
- keep profile-specific assumptions isolated from the generic core
- keep Git/traceability notes accurate for environments where .git is absent

## Git / traceability note

A missing .git directory or unavailable Git metadata should be treated as a traceability / environment hygiene warning.

It should not be mistaken for evidence that the PatchOps core is broken.

## Optional future work

Possible post-buildout enhancements include:

- richer profile support
- stronger dry-run introspection
- richer report summaries
- broader language/repo support
- additional fixture repositories
- more launcher conveniences

These are additive improvements, not evidence that the initial product failed.

## Done-enough standard

PatchOps is done enough for maintenance mode when:

- the core architecture is stable
- adding profiles is additive rather than architecture-breaking
- the main workflow classes are covered
- the docs are trustworthy enough for a future LLM to use the repo from docs/examples alone
- tests protect the main contracts
- shipped behavior and optional future work are clearly separated

That is the current posture of the repo.