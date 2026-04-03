# Failure and Repair Guide

## Failure classes

### Target-project failure
Examples:

- tests fail because patch content is wrong
- target policy blocks the action

### Wrapper failure
Examples:

- manifest is invalid
- profile resolution fails
- report generation crashes
- command invocation shape is broken by wrapper mechanics

## Stage 1 recovery paths

- use `patchops verify` when files are already written and you need a clean evidence rerun
- fix wrapper-only issues without rewriting target content when possible
