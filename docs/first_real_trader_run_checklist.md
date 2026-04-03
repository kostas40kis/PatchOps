# First real trader run checklist

Use this checklist right before the first real trader-facing PatchOps execution.

## Environment
- [ ] PatchOps tests are green.
- [ ] `patchops.cli doctor --profile trader` reports `ok: true`.
- [ ] The trader profile runtime path looks correct.
- [ ] The Desktop report location or custom report location is understood.

## Manifest review
- [ ] The manifest uses `active_profile: trader`.
- [ ] `target_project_root` is correct.
- [ ] backup files are explicit.
- [ ] validation commands are explicit.
- [ ] placeholder content has been replaced.
- [ ] the change is intentionally low-risk.

## Review-before-run sequence
- [ ] `check` completed
- [ ] `inspect` completed
- [ ] `plan` completed
- [ ] verify/apply choice is explicit

## After run
- [ ] One canonical report exists.
- [ ] `ExitCode` and `Result` are explicit.
- [ ] stdout/stderr are captured.
- [ ] Any failure is classified as wrapper-only or trader-side.
