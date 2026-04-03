# Report rendering contract

## Purpose

This maintenance note records the current report-rendering contract after the MP15 helper reuse repair.

## Maintained rule

PatchOps now routes one additional workflow path through the shared report-helper model: command output rendering.
The maintained contract is:

- command-section data stays explicit and structured,
- command text remains visible,
- working directory is rendered as a string-facing field,
- stdout and stderr stay separate report surfaces,
- empty stdout or stderr still renders as an explicit section instead of disappearing,
- PowerShell remains the thin operator boundary while Python owns reusable reporting helpers.

## Why this matters

This keeps the canonical report readable for operators, tests, and future LLM handoff without reopening the renderer architecture.

## Maintenance guidance

Prefer narrow helper/model repairs over broad renderer rewrites.
If report output structure drifts again, repair the shared helper contract first and rerun the maintained reporting and summary-truth tests before changing wider workflow code.