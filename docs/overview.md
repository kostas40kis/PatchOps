# Overview

PatchOps is a standalone wrapper and evidence system.

## Process execution note

The preferred internal path is:
- run_command_result
- normalize_execution_result
- ExecutionResult
- patchops.execution.process_runner
- patchops.execution.result_model

Avoid ad hoc subprocess loops and PowerShell patch bodies for reusable mechanics.
