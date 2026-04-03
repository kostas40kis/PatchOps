# Failure Repair Guide

This guide explains how to choose the right recovery path after a PatchOps run fails or produces incomplete evidence.

The goal is not to guess.
The goal is to classify the failure clearly enough that you can rerun narrowly, preserve evidence discipline, and avoid widening into a blind full rerun when it is not needed.

---

## 1. Why this guide exists

PatchOps distinguishes between **target-repo content behavior** and **wrapper mechanics**.

That distinction matters because a failing run can mean very different things:

- the target repo logic is actually broken,
- the wrapper failed to execute commands safely,
- the patch content likely succeeded but the report/evidence layer failed,
- or the correct action is a verification-only rerun rather than a new apply pass.

The right recovery depends on the failure class.

---

## 2. The four main cases

### 2.1 Content failure

Choose **content failure** when the wrapper appears to have executed correctly, but the target repo work itself failed.

Common signs:

- file writes completed,
- the wrapper report is structurally complete,
- validation commands ran,
- and the failure is inside target-repo tests, scripts, or logic.

Typical examples:

- pytest fails because the new code is wrong,
- a target repo import error appears,
- a target repo command returns a real functional failure.

Recommended action:

- fix the content,
- rerun through the normal patch flow,
- keep the recovery scoped to the actual bad content.

Do **not** treat this as a wrapper-only problem.

### 2.2 Wrapper failure

Choose **wrapper failure** when PatchOps itself failed to execute or evidence the run safely.

Common signs:

- broken quoting or path resolution,
- runtime detection failure,
- report writer crash,
- launcher shape problem,
- incomplete or malformed report sections,
- shell compatibility issue,
- backup helper failure.

In wrapper failure cases, the target repo may be fine, but the wrapper cannot yet prove what happened safely enough.

Recommended action:

- repair the wrapper problem first,
- avoid assuming target content is bad unless the evidence clearly says so,
- prefer a narrow rerun mode when the target content likely already succeeded.

### 2.3 Verification-only rerun case

Choose **verification-only rerun** when the files are already on disk and the correct next step is to re-check them and rerun validation commands without rewriting the files.

This is the right path when:

- the patch content is already present,
- you want a clean evidence report,
- you want to confirm current repo state,
- and widening into another write pass would add unnecessary risk or noise.

Expected characteristics:

- writes are skipped,
- expected target files are re-checked,
- validation commands are rerun,
- rerun scope is explicit in the report.

Use the thin PowerShell verify launcher when it helps the operator workflow:

- `powershell/Invoke-PatchVerify.ps1`

Preview first when appropriate so the verify-only plan is clear before running it.

### 2.4 Wrapper-only repair case

Choose **wrapper-only repair** when the patch content likely succeeded but the wrapper/evidence layer failed after or around that success.

Typical examples:

- report generation failed after files were written,
- a launcher or quoting issue happened after validation likely already completed,
- the final evidence artifact is incomplete even though target work probably succeeded.

This is narrower than a generic rerun.

Expected characteristics:

- the recovery intent is explicit,
- writes stay skipped,
- expected target files are re-checked,
- validation-oriented reruns remain narrow,
- missing expected files force escalation instead of silently widening into full apply.

---

## 3. Quick decision table

| Situation | Best classification | Best next step |
|---|---|---|
| Tests ran and failed in the target repo | Content failure | Fix content and rerun normal patch flow |
| Wrapper could not resolve runtime/path/reporting safely | Wrapper failure | Repair wrapper behavior first |
| Files already exist and you only need re-validation | Verification-only rerun | Use verify-only path |
| Content likely succeeded but wrapper evidence failed | Wrapper-only repair | Use wrapper-only retry path |

---

## 4. Escalation rules

Not every narrow rerun is safe.

Escalate out of a narrow rerun when:

- expected target files are missing,
- the report cannot establish what was actually written,
- the current repo state no longer matches the supposed prior run,
- the operator cannot explain why a narrow retry would still be trustworthy,
- or the wrapper repair path begins to look like a hidden full apply.

In those cases, stop pretending it is a narrow rerun and switch to a more explicit recovery path.

---

## 5. Evidence expectations for every recovery path

Every recovery path still needs one strong report.

A good rerun or repair report should make these things explicit:

- workspace root,
- wrapper project root,
- target project root,
- runtime/interpreter path,
- target files,
- whether writes were performed or skipped,
- command lines that actually ran,
- full stdout/stderr,
- the failure classification or retry intent,
- and final `ExitCode` / `Result`.

A narrow rerun without strong evidence is not a trustworthy recovery.

---

## 6. Guidance for future LLMs and operators

Before choosing a rerun mode, answer these questions explicitly:

1. Did the target content likely fail, or did the wrapper fail?
2. Are the expected files already on disk?
3. Is the goal to rewrite content, or only to re-check and re-evidence it?
4. Would a broader rerun hide the real problem?
5. Can the report clearly explain the recovery choice?

If those answers are still vague, do not widen blindly.
Reclassify the problem first.

---

## 7. Bottom line

PatchOps recovery should be:

- explicit,
- narrow when safe,
- auditable,
- evidence-driven,
- and honest about when escalation is required.

The correct question is not “How do we rerun something?”

The correct question is:

**What failed, and what is the narrowest trustworthy recovery path?**
