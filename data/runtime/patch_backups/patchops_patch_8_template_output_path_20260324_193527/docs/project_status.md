# PatchOps Project Status

## Current shipped behavior

PatchOps currently ships a usable Stage 1 wrapper with:

- manifest loading and validation
- profile resolution
- trader profile
- generic Python profile
- generic Python + PowerShell profile
- deterministic backups
- deterministic file writing
- process execution with stdout/stderr capture
- human-readable one-report output
- apply workflow
- verify-only workflow
- inspect command
- plan command
- profiles command
- template command
- thin PowerShell launchers for apply / verify / inspect / plan / profiles / template
- example manifests
- harness test coverage for the main contracts

## Stable core contracts

The following shapes should now be treated as stable enough for normal use:

- manifest-driven execution
- profile-based target resolution
- one-report evidence discipline
- explicit backup and file-writing evidence
- wrapper vs target failure separation
- verify-only narrow rerun behavior
- safe pre-apply review through inspect and plan
- profile discovery before manifest creation
- profile-aware starter templates

## Recommended user flow

A future LLM or operator should normally use this order:

1. `profiles`
2. `template`
3. edit the generated manifest
4. `inspect`
5. `plan`
6. `apply` or `verify`
7. review the one canonical report

## Still future work

The project is already useful, but some work still remains outside the initial Stage 1 circle, including possible future enhancements such as:

- richer cleanup / archive flows
- more advanced dry-run introspection
- more profiles
- better integration fixtures
- richer handoff summaries
- more ergonomic manifest authoring beyond starter templates

These are improvements, not evidence that the current wrapper is unusable.