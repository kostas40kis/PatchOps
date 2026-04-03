# PatchOps current handoff

This file is the current human-readable resume point for a future LLM or operator.

## Resume snapshot

Project               : PatchOps
Wrapper Project Root  : C:\dev\patchops
Target Project Root   : C:\dev\patchops
Current Stage         : Stage 2 in progress
Latest Run Mode       : apply
Current Status        : pass
Latest Attempted Patch: Patch 127
Latest Passed Patch   : Patch 127
Latest Report Path    : C:\Users\kostas\Desktop\patch_127_final_contract_lock_validation_sweep_20260328_181707.txt
Failure Class         : none
Next Action           : Continue with Patch 128.
Next Recommended Mode : new_patch
Recommendation Why    : The latest exported report passed, so the trustworthy next step is the next planned patch.
Escalation Required   : no
Known Blockers        : 0
Do Not Redesign       : Keep PowerShell thin and reusable logic in Python unless the evidence forces deeper change.

## Must-read files before acting

- `docs/llm_usage.md`
- `docs/project_status.md`
- `docs/patch_ledger.md`
- `docs/manifest_schema.md`
- `docs/failure_repair_guide.md`

## Resume rules

- PatchOps owns patch application, validation, evidence, retry, and handoff mechanics.
- Target repos own their own business logic.
- Prefer narrow repair over broad rewrite.
- Preserve the one-report evidence contract.
