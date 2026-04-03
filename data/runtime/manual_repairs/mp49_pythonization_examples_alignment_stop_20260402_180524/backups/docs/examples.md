# Examples Guide

Start from examples and adapt them.

Examples are no longer the first state-reconstruction surface for future LLM takeover.
Current repo-state takeover should begin with:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

After that, examples remain the intended starting surface for practical PatchOps usage when you need to build the next manifest.

## Current bundled example set

### Generic apply-oriented examples

generic python example:
- `examples/generic_python_patch.json`
- `examples/generic_backup_patch.json`
- `examples/generic_content_path_patch.json`
- `examples/generic_report_dir_patch.json`
- `examples/generic_report_prefix_patch.json`
- `examples/generic_smoke_audit_patch.json`
- `examples/generic_allowed_exit_patch.json`

The allowed-exit example exists to show `allowed_exit_codes`.
The content-path example exists to show `generic_content_path_note.txt`.

### Generic mixed Python + PowerShell profile examples

- `examples/generic_python_powershell_patch.json`
- `examples/generic_python_powershell_verify_patch.json`

### Trader walkthroughs

trader code patch example:
- `examples/trader_code_patch.json`

documentation-only example:
- `examples/trader_first_doc_patch.json`

trader verification-only example:
- `examples/trader_first_verify_patch.json`

Also present:
- `examples/trader_doc_patch.json`
- `examples/trader_verify_patch.json`

## Example workflow

For normal authoring:

1. start from the closest example
2. adapt only what is necessary
3. run:
   - `py -m patchops.cli check <manifest>`
   - `py -m patchops.cli inspect <manifest>`
   - `py -m patchops.cli plan <manifest>`
4. only then run apply or verify

### Operator note

Use `powershell/Invoke-PatchVerify.ps1` when the right move is a narrow verification rerun rather than a full apply pass.

If you are uncertain, start narrower.

That is the intended starting surface for practical PatchOps usage.

## Bottom line

Examples help you build the next manifest.

They should not be the first tool for reconstructing current repo state.

<!-- PATCHOPS_PATCH76_PROJECT_PACKET_PRACTICAL_USAGE:START -->
## Project packets and new target onboarding

Project packets are now part of the normal PatchOps usage story.

When starting a brand-new target project:

1. read the generic PatchOps packet first,
2. create or refresh `docs/projects/<project_name>.md`,
3. use that packet to choose the smallest correct profile,
4. then choose the closest bundled example manifest,
5. run `check`, `inspect`, and `plan` before `apply` or `verify`,
6. inspect the canonical report,
7. update the project packet before continuing.

Important boundary:

- project packets do **not** replace examples,
- examples remain the baseline starter surface for real manifest authoring,
- project packets explain the target,
- manifests tell PatchOps what to do right now.

For the first maintained packet example, see:

- `docs/projects/trader.md`
<!-- PATCHOPS_PATCH76_PROJECT_PACKET_PRACTICAL_USAGE:END -->

<!-- PATCHOPS_PATCH84_EXAMPLES_STARTER_GUIDANCE:START -->
## Examples remain the baseline even with helpers

The onboarding helpers do not replace examples.
They reduce blank-page authoring and point operators toward the closest conservative starting surface.

Recommended operator order:
1. inspect the closest examples,
2. use `recommend-profile` when profile choice is unclear,
3. use `starter` only to generate a conservative first manifest skeleton,
4. narrow the manifest deliberately before apply or verify.

This keeps examples as the baseline and helpers as accelerators.
<!-- PATCHOPS_PATCH84_EXAMPLES_STARTER_GUIDANCE:END -->

<!-- PATCHOPS_PATCH88_EXAMPLES:START -->
## Handoff-first continuation examples

Use these examples when PatchOps work is already in progress and the right first surface is the handoff bundle, not a brand-new target onboarding packet.

### Example 1 — export the current handoff bundle from a known report

```powershell
py -m patchops.cli export-handoff --report-path C:\Users\kostas\Desktop\patch_87_handoff_operator_docs_stop_20260328_124012.txt --wrapper-root C:\dev\patchops
```

Expected stable outputs under `handoff/` include:

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`
- `handoff/latest_report_index.json`
- `handoff/next_prompt.txt`
- `handoff/bundle/current/`

### Example 2 — operator continuation flow

When handing off to the next LLM during an already-running PatchOps effort:

1. run handoff export,
2. upload the generated handoff files or the compact bundle,
3. paste `handoff/next_prompt.txt`,
4. continue from the exact next recommended action.

### Example 3 — when not to use handoff first

Do **not** use handoff as the first step when the job is to onboard a brand-new target project.

For brand-new target onboarding, start with the generic PatchOps packet, then create or refresh the relevant project packet under `docs/projects/`.

Simple rule:

- handoff = continuation of current PatchOps run-state,
- project packet = maintained target-facing contract,
- manifest = exact instructions for this run,
- report = evidence of what happened.
<!-- PATCHOPS_PATCH88_EXAMPLES:END -->
\n\n<!-- PATCHOPS_PATCH92_EXAMPLES:START -->
## Onboarding bootstrap examples

Use onboarding bootstrap artifacts when the job is to start a brand-new target project faster.

Expected bootstrap outputs include:

- `onboarding/current_target_bootstrap.md`
- `onboarding/current_target_bootstrap.json`
- `onboarding/next_prompt.txt`
- `onboarding/starter_manifest.json`

Simple rule:

- onboarding bootstrap = helper bundle for first use of a brand-new target,
- project packet = maintained target-facing contract,
- handoff = continuation of already-running PatchOps work,
- report = evidence of what happened.
<!-- PATCHOPS_PATCH92_EXAMPLES:END -->\n

<!-- PATCHOPS_F7_FINAL_DOC_STOP_EXAMPLES:START -->
## Final example selection guidance

Use examples mechanically instead of starting from a blank page when one of these already matches the work.

### For already-running PatchOps continuation

- use the handoff bundle first,
- then choose the smallest matching example only if a new manifest must be authored.

### For brand-new generic target work

Lowest-friction generic starts:

- `examples/generic_python_patch.json`
- `examples/generic_verify_patch.json`
- `examples/generic_python_powershell_patch.json`
- `examples/generic_python_powershell_verify_patch.json`

### For conservative trader-target starts

Lowest-friction trader starts:

- `examples/trader_first_doc_patch.json`
- `examples/trader_first_verify_patch.json`

Broader trader examples:

- `examples/trader_doc_patch.json`
- `examples/trader_verify_patch.json`
- `examples/trader_code_patch.json`

### Boundary reminder

Examples are starter surfaces.
They do not replace project packets, handoff files, manifests, or canonical reports.
<!-- PATCHOPS_F7_FINAL_DOC_STOP_EXAMPLES:END -->


## content_path resolution rule

`examples/generic_content_path_patch.json` demonstrates the maintained `content_path` authoring contract.

Author relative `content_path` values as wrapper-relative paths from the wrapper project root.

PatchOps resolves the wrapper-root candidate first. If that file does not exist, PatchOps falls back to manifest-local resolution so older nested-manifest flows still load cleanly. That manifest-local behavior is compatibility fallback, not the primary authoring rule.

The external payload for the maintained example lives at `examples/content/generic_content_path_note.txt`.
