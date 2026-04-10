# Patch ledger

## Patch 35 - final release / maintenance gate
This gate patch recorded the maintenance-mode verdict from the shipped readiness and validation surfaces.
It was a gate patch, not a redesign patch.

## Patch 37C - run-package operator runner test escape repair
This narrow repair fixed the backslash escaping in the canonical quiet-runner contract test so the current operator runner surface compiles and validates again.

## Patch 38 - final source bundle freeze export
This freeze-export patch adds `handoff/final_future_llm_source_bundle.txt` as the preferred durable upload artifact after the maintenance gate and documentation stop.
