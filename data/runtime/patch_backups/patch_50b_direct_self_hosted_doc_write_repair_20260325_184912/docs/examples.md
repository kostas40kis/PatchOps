# Examples Guide

This document gives concrete example walkthroughs for the main PatchOps usage patterns.

It exists so a new user or future LLM does not have to infer usage only from raw JSON manifests.
The examples below show what to start from, when to use each example, and what the expected operator path looks like.

---

## How to use these walkthroughs

The safest pattern is:

1. pick the smallest example that matches the job,
2. keep the active profile explicit,
3. review the target files and validation commands,
4. prefer verify-only when the files are already on disk,
5. produce one strong evidence report.

Start from examples and adapt them.
Do not invent a new manifest shape unless the current examples genuinely do not fit the task.

---

## Example 1 — trader code patch example

**Manifest:** `examples/trader_code_patch.json`

Use this when the task really requires changing code inside `C:\dev	rader`.

This is the right starting point when:

- the target repo is the trader project,
- the patch changes Python source or tests,
- the run should behave like a normal apply workflow rather than a verification-only rehearsal.

What to inspect before using it:

- `active_profile` should stay `trader`,
- target file paths should point into the trader repo,
- validation commands should match the narrow proof surface for the patch,
- report expectations should remain explicit.

Use this example carefully.
It is a code-changing path, so it should not be the first choice when a doc-only or verify-only path would be enough.

---

## Example 2 — trader verification-only example

**Manifest:** `examples/trader_first_verify_patch.json`

This is the best first trader walkthrough for low-risk rehearsal.

Use it when:

- files are already on disk,
- the goal is confidence and evidence,
- you want to confirm the trader profile, roots, runtime, and validation path,
- you do not want to widen into a rewrite.

Common operator sequence:

1. run `py -m patchops.cli plan .\examples	rader_first_verify_patch.json --mode verify`
2. review the resolved target root and runtime,
3. optionally use `powershell/Invoke-PatchVerify.ps1 -Preview`,
4. run the actual verify flow only after the preview looks right.

This example is the cleanest starting point for trader-first verification-only work.

---

## Example 3 — generic Python example

**Manifest:** `examples/generic_python_patch.json`

Use this when the target repo is a normal Python project and you want a simple apply example that is not trader-specific.

This is useful when:

- you want to demonstrate PatchOps reuse outside trader,
- the target repo is Python-first,
- you need a small apply walkthrough with backup, write, and validation behavior.

What it proves:

- PatchOps is not trader-only,
- a profile-driven apply workflow can stay simple,
- the wrapper can still produce deterministic evidence outside the first real target profile.

---

## Example 4 — documentation-only example

**Manifest:** `examples/trader_first_doc_patch.json`

Use this when the safest first move is a documentation-only patch.

This is often the right choice when:

- the content being changed is a guide, checklist, or handoff doc,
- the operator wants a low-risk first live usage of the wrapper,
- a future LLM needs a clean starter example for non-code changes.

Documentation-only work is valuable because it exercises backup, write, and evidence behavior without immediately widening into target-repo code change.

---

## Choosing between these examples

Use this quick rule:

- start with the **trader verification-only example** when you want the safest trader-first rehearsal,
- use the **documentation-only example** when the job is docs-first and low-risk,
- use the **trader code patch example** only when real trader code needs to change,
- use the **generic Python example** when you want to prove PatchOps reuse outside trader.

If you are uncertain, start narrower.
A smaller example with a strong report is usually better than a larger example chosen too early.

---

## Bottom line

A new user or LLM should be able to begin from these walkthroughs without guessing.

The examples in this guide provide:

- one trader code patch example,
- one trader verification-only example,
- one generic Python example,
- one documentation-only example.

That is the intended starting surface for practical PatchOps usage.

## Additional specialized examples

A few specialized examples are still worth keeping visible in this guide because other tests and handoff flows rely on them being documented explicitly.

- `examples/generic_allowed_exit_patch.json` demonstrates the `allowed_exit_codes` pattern for cases where a command may legitimately return a non-zero code that is still considered acceptable by the manifest contract.
- `examples/generic_content_path_patch.json` demonstrates the content-path pattern for cases where file content is sourced from a separate path instead of being embedded directly inside the manifest, with companion content such as `generic_content_path_note.txt`.

These are not the first examples most users should start with, but they remain important reference patterns when adapting manifests for more specialized workflows.

<!-- PATCHOPS_PATCH45_OPERATIONAL_TYPES:START -->
## Patch class map

For a direct workflow-choice guide, read `docs/operational_patch_types.md`.

That document maps real tasks to the main PatchOps classes:

- code,
- documentation,
- validation,
- cleanup,
- archive,
- verify-only.
<!-- PATCHOPS_PATCH45_OPERATIONAL_TYPES:END -->
