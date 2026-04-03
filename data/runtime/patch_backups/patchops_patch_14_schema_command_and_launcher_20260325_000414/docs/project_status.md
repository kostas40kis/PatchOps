# Project status

## Current state

PatchOps is now a usable Stage 1 wrapper.

Shipped behavior includes:

- explicit manifest loading and validation
- profile discovery and profile summaries
- plan / inspect / apply / verify flows
- starter manifest template generation
- starter manifest template file output through `template --output-path`
- manifest placeholder checks through `check`
- thin PowerShell launchers for inspect, plan, apply, verify, profiles, template, and check
- deterministic report generation with final summary
- backup and file-writing helpers
- compatibility-safe command execution
- harness tests covering the main wrapper contracts

## Immediate next priority

Keep improving the authoring and pre-apply review path without moving target-repo business logic into the wrapper core.

## Still future work

- richer cleanup/archive execution coverage
- more profiles
- more fixture repos for end-to-end proving
- more ergonomic manifest authoring beyond starter templates
- stronger maintenance-mode polish

## Patch 10

Added a `doctor` command and PowerShell launcher so operators and future LLMs can verify profile/environment readiness before manifest generation and pre-apply review.

## Patch 11 status update

Patch 11 adds example-manifest discovery through:

- `patchops.cli examples`
- `powershell\Invoke-PatchExamples.ps1`

This improves first-use ergonomics for future LLMs and operators by making bundled manifest inventory explicit before template generation.

## Patch 12 status

Patch 12 adds a documentation layer that matches the current Stage 1 command surface.

Added:

- `docs/operator_quickstart.md`
- `docs/command_matrix.md`
- `docs/repair_rerun_matrix.md`
- `tests/test_stage1_docs.py`

This keeps the repo easier to hand off before the next round of execution-surface enhancements.

## Patch 13 status

Stage 1 now includes explicit example coverage for all three shipped profiles:

- `trader`
- `generic_python`
- `generic_python_powershell`

This improves handoff quality for future LLMs because profile selection no longer depends only on reading the source code or inferring intent from the existing examples directory.
