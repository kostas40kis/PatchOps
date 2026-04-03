# Trader Profile Guide

This document explains how PatchOps should be used against `C:\dev\trader` specifically.

The point of this guide is not to make PatchOps trader-only.
The point is to make the trader profile explicit enough that future LLMs and operators do not guess about roots, runtimes, backups, or report expectations.

---

## 1. What the trader profile is

The trader profile is a **profile**, not the identity of the core wrapper.

That means:

- PatchOps stays project-agnostic,
- trader-specific defaults live in the trader profile surface,
- trader business logic remains inside `C:\dev\trader`,
- and future profiles should be addable without redesigning the core.

Keep repeating this rule:

**Trader remains a profile, not the core identity of PatchOps.**

---

## 2. Expected roots

For normal trader usage, the expected roots are:

- workspace root: `C:\dev`
- wrapper project root: `C:\dev\patchops`
- trader target project root: `C:\dev\trader`

The profile should make those assumptions visible and predictable.
A future LLM should not need to rediscover them from scattered reports.

---

## 3. Expected runtime

For trader-first work, the expected runtime is normally:

- `C:\dev\trader\.venv\Scripts\python.exe`

This matters because the target repo owns its own tests and execution environment.
PatchOps should not silently substitute trader runtime behavior with wrapper-local behavior unless the chosen workflow explicitly says so.

The wrapper should still report the resolved runtime clearly.

---

## 4. Backup conventions

Trader runs should preserve the same PatchOps backup discipline:

- if a target file already exists, back it up before overwriting it,
- keep backups under a patch-specific directory,
- preserve relative file paths under the backup root,
- record missing files honestly as `MISSING: <path>`.

Example backup pattern for wrapper-side patch scripts often looks like:

- `C:\dev\patchops\data\runtime\patch_backups\<patch_name_timestamp>\...`

For target-facing workflows, the important rule is not the exact spelling of every folder.
The important rule is that the backup convention is deterministic, auditable, and visible in the report.

---

## 5. Report expectations

Trader-facing PatchOps runs should still produce one canonical evidence artifact.

A good trader report should make these things explicit:

- selected profile,
- wrapper project root,
- target project root,
- resolved runtime path,
- target files,
- backup behavior,
- commands that ran,
- full stdout/stderr,
- final `ExitCode : ...`,
- final `Result   : PASS|FAIL`.

In the usual Windows workflow, the report is expected to land on the Desktop unless the manifest says otherwise.

---

## 6. Which manifests to start from

Future LLMs and operators should start from the trader examples instead of inventing a trader manifest from scratch.

The most important trader manifests are:

- `examples/trader_first_verify_patch.json`
- `examples/trader_first_doc_patch.json`
- `examples/trader_verify_patch.json`
- `examples/trader_doc_patch.json`
- `examples/trader_code_patch.json`

Good practice:

- use `examples/trader_first_verify_patch.json` for low-risk verification rehearsals,
- use the doc-oriented examples for documentation-first work,
- use the code-oriented examples only when the job actually requires target-repo code change.

---

## 7. What trader logic must remain outside PatchOps

This section is critical.

Trader logic that must remain outside PatchOps includes:

- trading strategy,
- execution policy,
- reserve policy,
- portfolio behavior,
- position lifecycle rules,
- market/routing logic,
- domain validation that belongs to the trader repo,
- trader-specific tests and target-side architecture.

PatchOps may execute manifests that touch trader files, but it must not become the home for trader business logic.

---

## 8. How future LLMs should use the trader profile

When the target repo is `C:\dev\trader`, a future LLM should:

1. read `docs/llm_usage.md`,
2. read this trader profile guide,
3. read `docs/trader_readiness_index.md` when the task is trader-first,
4. inspect the trader example manifests,
5. choose between apply and verify-only deliberately,
6. keep trader assumptions inside the trader profile and manifests,
7. keep target-repo business logic in the trader repo.

That is the intended handoff path.

---

## 9. Bottom line

The trader profile should make trader usage explicit while keeping PatchOps reusable.

The correct outcome is:

- trader usage is easy to understand,
- trader-specific assumptions remain isolated,
- reports are predictable,
- runtime expectations are explicit,
- and PatchOps does not drift into trader-only identity.
