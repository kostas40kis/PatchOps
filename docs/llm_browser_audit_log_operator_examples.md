# LLM Browser Audit Log Operator Examples

This document is an operator-facing reference for the optional PatchOps LLM browser runner audit log.

The audit log is a compact JSONL evidence stream. It records what the browser-runner decision layer saw, what it planned, and whether it would have blocked or continued. It is not a command log that performs actions.

## Safety contract

The audit-log surfaces are passive.

They do not:

- start a browser;
- start Selenium;
- click a download link;
- run PatchOps;
- paste into a composer;
- submit or send a message;
- start a localhost service;
- delete, clear, or mutate old audit entries during readback.

The write path is opt-in and append-only through `--audit-log`.

The readback path is read-only through `llm-browser audit-log`.

There is still no `--auto-send` or `--allow-send` option.

## Default location

When no explicit audit path is provided to the lower-level audit API, the default path is resolved in this order:

1. `PATCHOPS_LLM_BROWSER_AUDIT_LOG`
2. `PATCHOPS_LLM_BROWSER_STORE_DIR\audit.jsonl`
3. `%LOCALAPPDATA%\PatchOps\llm_browser\audit.jsonl`
4. `~\.patchops\llm_browser\audit.jsonl`

For normal operator scripts, prefer an explicit path first:

```powershell
$audit = "$env:TEMP\patchops_llm_browser_audit.jsonl"
```

## Write one dry-run audit event

Use `dry-run` when you have a saved or synthetic ChatGPT page snapshot and want the passive decision result.

```powershell
py -m patchops.cli llm-browser dry-run `
  --snapshot-file "C:\dev\patchops\data\snapshots\chatgpt_reply.html" `
  --audit-log "$env:TEMP\patchops_llm_browser_audit.jsonl" `
  --json
```

This appends one `dry_run_result` JSONL event.

Expected event fields include:

- `event_type`
- `event_id`
- `timestamp`
- `source`
- `status`
- `state`
- `artifact_filename` when a candidate was detected
- `report_path` when a report is known
- `reason`
- `metadata.planned_actions`
- `metadata.side_effects_performed`

## Write one run-once dry-mode audit event

Use `run-once --dry-run` to exercise the integration skeleton without live side effects.

```powershell
py -m patchops.cli llm-browser run-once `
  --dry-run `
  --snapshot-file "C:\dev\patchops\data\snapshots\chatgpt_reply.html" `
  --audit-log "$env:TEMP\patchops_llm_browser_audit.jsonl" `
  --json
```

This appends one `integration_result` JSONL event.

## Read recent audit events as JSON

```powershell
py -m patchops.cli llm-browser audit-log `
  --path "$env:TEMP\patchops_llm_browser_audit.jsonl" `
  --limit 5 `
  --json
```

Use `--limit 0` to return all matching events.

## Read recent audit events as compact text

```powershell
py -m patchops.cli llm-browser audit-log `
  --path "$env:TEMP\patchops_llm_browser_audit.jsonl" `
  --limit 5
```

The text output is intended for quick operator inspection. JSON output is better for tooling.

## Filter by event type

```powershell
py -m patchops.cli llm-browser audit-log `
  --path "$env:TEMP\patchops_llm_browser_audit.jsonl" `
  --event-type dry_run_result `
  --json
```

Useful event types:

- `dry_run_result`
- `integration_result`
- `pasteback_summary`

## Filter by status

```powershell
py -m patchops.cli llm-browser audit-log `
  --path "$env:TEMP\patchops_llm_browser_audit.jsonl" `
  --status FAIL `
  --json
```

Common statuses:

- `PASS`
- `FAIL`
- `UNKNOWN`

## Missing or corrupt log behavior

A missing audit file is treated as an empty audit log.

Corrupt JSONL lines are ignored by the underlying reader so one bad line does not hide later valid events.

## Operator interpretation guide

### BLOCKED_ARTIFACT_MISSING

The runner found a stable assistant reply but no unused PatchOps bundle link.

Typical next step:

- upload the latest canonical report or ask for the next bundle.

### DOWNLOADING

The runner found a candidate bundle and would click/download it in a future live mode.

In current dry mode, no click occurs. The audit event records the planned action only.

### RUNNING_PATCHOPS

The dry-run had enough supplied metadata to reach the point where PatchOps would be invoked.

In current dry mode, PatchOps is not invoked unless a supplied fake/synthetic result is provided to the passive layer.

### BLOCKED_REPORT_MISSING

PatchOps runner metadata was ok, but the canonical report could not be located.

Treat this as fail-closed.

### SUMMARY_READY

The passive flow reached a state where the pasteback summary can be prepared.

Even here, current surfaces do not auto-send anything.

## Recommended operator loop

1. Run `llm-browser dry-run` or `llm-browser run-once --dry-run` with `--audit-log`.
2. Read the latest audit entries with `llm-browser audit-log --limit 5`.
3. Check `status`, `state`, and `metadata.planned_actions`.
4. Upload the canonical report when a patch fails or evidence is incomplete.
5. Continue patch-by-patch only when the report and audit state agree.

## Troubleshooting examples

### Show all FAIL events

```powershell
py -m patchops.cli llm-browser audit-log `
  --path "$env:TEMP\patchops_llm_browser_audit.jsonl" `
  --status FAIL `
  --limit 0 `
  --json
```

### Show only integration events

```powershell
py -m patchops.cli llm-browser audit-log `
  --path "$env:TEMP\patchops_llm_browser_audit.jsonl" `
  --event-type integration_result `
  --limit 10
```

### Use a per-run audit path

```powershell
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$audit = "$env:TEMP\patchops_llm_browser_audit_$stamp.jsonl"

py -m patchops.cli llm-browser run-once `
  --dry-run `
  --snapshot-file "C:\dev\patchops\data\snapshots\chatgpt_reply.html" `
  --audit-log $audit `
  --json

py -m patchops.cli llm-browser audit-log `
  --path $audit `
  --json
```

## Contract summary

The audit log is evidence, not automation authority.

It answers:

- what did the runner decide;
- what candidate artifact was seen;
- what state did orchestration reach;
- what planned actions were produced;
- what side effects were performed;
- where the report evidence is.

For D0.27, operator examples remain dry-mode examples only.
