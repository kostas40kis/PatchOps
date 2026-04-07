# Single Canonical Run-Package Report Live Proof

## Purpose

This proof patch exists to verify the new single-report run-package behavior after `zp21_single_canonical_run_package_report`.

The implementation patch already passed its focused test suite.
However, the run that applied it was still orchestrated by the older pre-patch `run-package` process.
That means the applying run itself could not be the live proof.

This patch is the first follow-on bundle intended to run through the updated `run-package` surface.

## What this proof is checking

The maintained behavior is now:

- when launcher execution produces an inner report,
- PatchOps merges the run-package outer context into that inner report,
- the merged inner report becomes the single canonical Desktop artifact,
- and a second Desktop outer txt artifact is not kept.

Fallback behavior remains:

- when setup fails before launcher invocation,
- or when no inner report exists,
- PatchOps still writes one outer fallback report.

## Operator reading

For this proof patch specifically, the key live evidence is not only the green test result.
The key live evidence is also the Desktop artifact pattern after the run:

- expected: one new Desktop txt report for this patch
- not expected: two separate new Desktop txt reports for this patch
