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