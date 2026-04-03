# Stage 2 entry criteria

Stage 2 should begin intentionally, not accidentally.

## Stage 2 should not start until
- Stage 1 is treated as a baseline.
- consolidation docs exist and are current.
- at least one real trader-facing PatchOps usage has been exercised deliberately.
- the operator flow is stable enough that future LLMs do not need to guess how to use PatchOps.

## Likely Stage 2 themes
- more deliberate wrapper-only rerun / repair tooling
- stronger release discipline
- more explicit manifest/version evolution rules
- safer target-profile extensions
- better operator ergonomics around real project usage

## What Stage 2 is not
- moving trader logic into PatchOps
- mixing target-repo business rules into the wrapper
- uncontrolled feature growth without baseline stability

## Handoff intent

When Stage 2 begins, the repo should already have:
- a maintained patch ledger,
- a freeze checklist,
- a release checklist,
- a trader first-usage guide,
- proven end-to-end authoring patterns from Stage 1.
