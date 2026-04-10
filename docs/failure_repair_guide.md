# Failure repair guide

## Purpose

This document is the maintained operator guide for deciding what failed first and how narrowly to repair it.

Its job is to keep three boundaries clear:

1. wrapper failure versus target-content failure,
2. normal execution versus exceptional recovery,
3. bundle-authoring drift versus real target-project defects.

## First question after any run

Read the canonical Desktop txt report first.

Do not decide from partial terminal output alone.
The report is the authoritative artifact for:

- result,
- exit code,
- failure category,
- failing command,
- stdout/stderr,
- and recommended next mode.

## Failure classes to keep separate

### Wrapper failure

Examples:
- launcher syntax drift,
- bad report plumbing,
- bundle launcher oddities such as a stray leading character before `param(`,
- script/helper behavior that fails before the intended repo contract is actually exercised.

Repair wrapper failures narrowly and first.

### Target-content failure

Examples:
- new code or tests fail,
- doc contract tests fail,
- a new helper has the wrong payload shape,
- a newly authored test file is malformed.

Repair only the first truthful failing content layer.

### Environment failure

Examples:
- missing toolchain,
- missing Git,
- wrong working path,
- unexpected local machine state.

Do not misclassify environment problems as product regressions.

## Normal flow versus exceptional flow

The normal maintained path remains:

- `check`
- `inspect`
- `plan`
- `apply` or `verify`

The exceptional bootstrap recovery path exists only for the case where the normal PatchOps CLI import chain is too broken to trust:

- `py -m patchops.bootstrap_repair`
- `py -m patchops.cli bootstrap-repair`

That recovery path is **not a second apply engine**.
Return to the normal maintained flow immediately after recovery succeeds.

## Bundle and launcher failures

Treat bundle-authoring problems as their own narrow class of operator-facing failure.

Common examples:
- wrong root shape,
- missing files under `content/`,
- malformed `bundle_meta.json`,
- wrong launcher placement,
- stray leading characters in `run_with_patchops.ps1`.

The canonical root launcher truth is documented in `docs/root_launcher_shape_contract.md`.
If a bundle launcher drifts from that contract, repair the launcher shape or the launcher-emission source before broadening the patch scope.

## Emitted helper script failures

The maintained emitted helper surface is `emit-operator-script`.
If an emitted script fails, ask:

1. did the script itself fail before producing the intended payload?
2. is the payload shape wrong?
3. did PowerShell 5.1 compatibility behavior regress?
4. did the helper overwrite or omit required doc/test contract lines?

Repair the smallest truthful layer only.

## Maintenance and readiness failures

For combined maintenance work, use `maintenance-gate`.
If the gate fails, inspect:
- which sub-gate failed,
- whether it is a regression gate, smoke gate, or readiness issue,
- and whether the report classifies the failure as wrapper, target, or environment.

Do not repair the whole stack at once.

## Publish step failures

The repo-owned publish helper is `powershell/Push-PatchOpsToGitHub.ps1`.

If the publish step fails:
- confirm Git identity,
- confirm the repo path,
- check for `.git\index.lock`,
- and treat publishing as a local/manual step that can be retried after the repo itself is already green.

A publish failure does not automatically mean the PatchOps code surface is broken.

## Repair discipline

- prefer narrow content repairs,
- preserve passing surfaces,
- add or update the smallest relevant contract test,
- and keep PowerShell thin while leaving reusable mechanics in Python.
