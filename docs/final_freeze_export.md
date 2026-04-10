# Final freeze export

## Purpose

This note records the narrow F8 closeout step for PatchOps.

The preferred durable upload artifact after the maintenance gate and the final documentation stop is:

`handoff/final_future_llm_source_bundle.txt`

## When to use it

Use `handoff/final_future_llm_source_bundle.txt` when:
- chat history is unavailable,
- one durable upload file is preferred,
- or a future LLM needs one stable repo snapshot instead of a broader conversation history.

## What it does not replace

The freeze-export artifact does not replace:
- `handoff/current_handoff.md` for immediate continuation,
- `handoff/current_handoff.json` for machine-readable continuation,
- `handoff/latest_report_copy.txt` for current run evidence,
- canonical Desktop txt reports for operator truth,
- or the normal PatchOps command surfaces.

## Current rule

Use the handoff bundle for immediate run-state continuation.
Use `handoff/final_future_llm_source_bundle.txt` when one durable history-compression artifact is preferred.
