# Report Rendering Contract

## Purpose

This document records the current maintained report-rendering truth for PatchOps after the
report-helper cleanup wave. It is meant to be practical rather than speculative.

## Current maintained rules

1. PatchOps still ends every operator run with one canonical Desktop txt report.
2. Header rendering should flow through the shared header helper rather than ad hoc assembly.
3. Command-output rendering should flow through the shared report-output helper surfaces.
4. Empty stdout or empty stderr should not hide the corresponding label.
5. Summary rendering must remain fail-closed and must match required command evidence.

## Shared helper surfaces

The following helper-owned surfaces are part of the current maintained report-rendering path:

- `render_report_header(...)`
- `render_report_command_output_section(...)`
- `render_command_output_section(...)`
- `build_report_command_section(...)`

## Practical expectation

When future maintenance work touches reporting, prefer narrow helper reuse over broad
report rewrites. Preserve the current wording unless a test-backed contradiction requires
a narrow repair.

## Operator truth

The canonical report is still the proof artifact for a run. Handoff surfaces, docs, and
project packets explain context, but they do not replace the report.
