# Examples Guide

This document gives concrete example walkthroughs for the main PatchOps usage patterns.

It exists so a new user or future LLM does not have to infer usage only from raw JSON manifests.
The examples below show what to start from, when to use each example, and what the expected operator path looks like.

---

## How to use these walkthroughs

The safest pattern is:

1. pick the smallest example that matches the job,
2. inspect it,
3. check it,
4. plan it,
5. apply it only when the target and scope are correct,
6. use verify-only reruns when content is already on disk and the goal is narrow validation/evidence.

Do not start by inventing a new manifest shape if an existing example already covers the workflow class you need.

---

## Current bundled example set

PatchOps currently ships a broad example surface that covers the main supported workflow classes.

### Generic apply-oriented examples

Use these when the target is a normal Python repo and the job is a real write/apply flow:

- `generic_python_patch.json`
- `generic_backup_patch.json`
- `generic_content_path_patch.json`
- `generic_report_dir_patch.json`
- `generic_report_prefix_patch.json`
- `generic_smoke_audit_patch.json`
- `generic_allowed_exit_patch.json`

### Generic verify-only example

Use this when files are already on disk and the goal is a narrow validation rerun:

- `generic_verify_patch.json`

### Generic mixed Python/PowerShell examples

Use these when the target repo contains both Python and PowerShell behavior:

- `generic_python_powershell_patch.json`
- `generic_python_powershell_verify_patch.json`

### Generic maintenance example

Use this when the patch is operational or maintenance-oriented rather than a normal code rewrite:

- `generic_cleanup_archive_patch.json`

### Trader-oriented examples

Use these only for trader-targeted workflows:

- `trader_code_patch.json`
- `trader_doc_patch.json`
- `trader_verify_patch.json`
- `trader_first_doc_patch.json`
- `trader_first_verify_patch.json`

That gives a maintained bundled example count of 16.

---

## Fastest starting points

### Need the smallest generic apply example?
Start with:
- `generic_python_patch.json`

### Need a backup-oriented example?
Start with:
- `generic_backup_patch.json`

### Need a verify-only rerun example?
Start with:
- `generic_verify_patch.json`

### Need a content-path example for staged file content?
Start with:
- `generic_content_path_patch.json`

### Need a cleanup/archive-style manifest?
Start with:
- `generic_cleanup_archive_patch.json`

### Need a trader-first low-risk entry point?
Start with:
- `trader_first_verify_patch.json`
- or `trader_first_doc_patch.json`

---

## Expected operator path

The recommended operator path for examples is:

1. inspect the manifest
2. check the manifest
3. plan the manifest
4. confirm profile / target root / runtime
5. apply only when the write scope is correct
6. use verify-only when a narrow rerun is the correct recovery behavior

This is especially important in Windows/PowerShell environments where explicit roots, explicit runtimes, and strong reporting matter.

---

## How examples map to workflow classes

PatchOps examples now cover the main maintained workflow classes:

- code patch flow
- documentation patch flow
- validation patch flow
- cleanup/archive flow
- verification-only rerun flow

That coverage is one of the reasons the repo is now considered done enough for maintenance mode rather than still being an unstable buildout.

---

## What examples are for

Examples are not meant to be copied blindly.

They are meant to:

- show the expected manifest shape
- show profile selection
- show how target roots are expressed
- show how validation commands are represented
- show how rerun-safe verify manifests differ from apply manifests
- give future LLMs a trustworthy starting point

---

## Current examples posture

The examples should now be treated as part of the maintained contract surface.

That means:

- keep them schema-valid
- keep them aligned with the real CLI behavior
- keep them aligned with the real docs
- do not let them drift into historical fiction