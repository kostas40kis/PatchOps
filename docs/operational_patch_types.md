# Operational Patch Types

This guide explains the main patch classes PatchOps supports and how to choose between them.

The goal is not only to list patch types.
The goal is to help an operator or future LLM map a real task to the narrowest correct workflow.

---

## 1. Code patch

Use a **code patch** when the target repo must change source code or tests.

Typical signs:

- Python modules need edits,
- tests need updates,
- the patch changes behavior rather than only documentation or evidence.

Good examples:

- `examples/trader_code_patch.json`
- `examples/generic_python_patch.json`

Choose this class only when code really must change.

---

## 2. Documentation patch

Use a **documentation patch** when the target change is a guide, checklist, handoff note, or other non-code document.

Typical signs:

- the change lives in markdown or similar docs,
- the safest first move is documentation-first,
- the patch should exercise backup/write/reporting without widening into code changes.

Good examples:

- `examples/trader_first_doc_patch.json`
- `examples/trader_doc_patch.json`

---

## 3. Validation patch

Use a **validation patch** when the main goal is to run checks and produce evidence, not necessarily to rewrite files.

Typical signs:

- validation commands matter more than file writes,
- the operator needs proof of current state,
- the patch is closer to a confidence run than a content mutation.

Good examples:

- `examples/generic_verify_patch.json`
- `examples/trader_verify_patch.json`

---

## 4. Cleanup patch

Use a **cleanup patch** when the task is maintenance-oriented and explicitly removes or tidies intermediate artifacts.

Typical signs:

- temporary files or directories need cleanup,
- the task is operational hygiene rather than business-logic change,
- cleanup actions must stay visible in the report.

Cleanup should never be treated as an invisible side effect.

---

## 5. Archive patch

Use an **archive patch** when the task is to preserve, move, or package outputs explicitly.

Typical signs:

- results need to be zipped or moved,
- logs or artifacts need traceable preservation,
- the archive action itself is part of the workflow contract.

Archive actions should remain first-class and traceable.

---

## 6. Verify-only patch

Use a **verify-only patch** when the files are already on disk and the correct next step is a narrow evidence rerun.

Typical signs:

- the patch content already exists,
- the operator wants re-validation,
- another apply pass would add risk or noise.

Good examples:

- `examples/trader_first_verify_patch.json`
- `examples/generic_python_powershell_verify_patch.json`

The thin PowerShell verify launcher exists for this path:

- `powershell/Invoke-PatchVerify.ps1`

---

## 7. How to choose the right class

Use this rule of thumb:

- choose **code patch** when behavior must change,
- choose **documentation patch** when the change is docs-only,
- choose **validation patch** when the goal is evidence and checks,
- choose **cleanup patch** when the work removes or tidies artifacts,
- choose **archive patch** when the work preserves or packages artifacts,
- choose **verify-only patch** when the files are already present and a narrow rerun is the right move.

If uncertain, start narrower.

---

## 8. Why this distinction matters

PatchOps should not make every task look like a generic apply flow.

Clear patch types help preserve:

- explicit workflow choice,
- explicit report scope,
- explicit operator intent,
- and safer reuse by future LLMs.

---

## 9. Bottom line

PatchOps now supports the main intended patch classes:

- code,
- documentation,
- validation,
- cleanup,
- archive,
- verify-only.

The correct job is not “run a patch somehow.”
The correct job is to choose the smallest correct patch class and prove it clearly.
