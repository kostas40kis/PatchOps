# Release checklist

This checklist is for a lightweight internal release of PatchOps after Stage 1 hardening.

## Before release
- [ ] Run `py -m pytest -q`
- [ ] Run `py -m patchops.cli profiles`
- [ ] Run `py -m patchops.cli doctor --profile trader`
- [ ] Run `py -m patchops.cli examples`
- [ ] Run `py -m patchops.cli schema`
- [ ] Run `py -m patchops.cli template --profile trader --mode apply --patch-name trader_stage1_template`
- [ ] Run `py -m patchops.cli check <manifest>`
- [ ] Run `py -m patchops.cli inspect <manifest>`
- [ ] Run `py -m patchops.cli plan <manifest>`

## Docs review
- [ ] `README.md` reflects the real command surface.
- [ ] `docs/project_status.md` reflects the real stage.
- [ ] `docs/patch_ledger.md` is current.
- [ ] `docs/operator_quickstart.md` still matches the recommended flow.
- [ ] `docs/repair_rerun_matrix.md` still matches actual rerun behavior.

## Operational readiness
- [ ] The team agrees on the first real trader-facing PatchOps usage.
- [ ] The manifest for that run is reviewed before apply.
- [ ] The first trader starter manifest is reviewed (`trader_first_doc_patch.json` or `trader_first_verify_patch.json`).
- [ ] A clear rollback/backout approach exists for the target repo.
- [ ] The report location and naming expectations are understood.

## After release
- [ ] Treat Stage 1 as a baseline, not a moving target.
- [ ] Start Stage 2 intentionally instead of mixing it into Stage 1 cleanup.

<!-- PATCHOPS_PATCH57_RELEASE_EVIDENCE_GUIDANCE:START -->
## Release-readiness evidence artifact

When you need a stable release-gate artifact, use the deterministic report-path flow instead of relying only on console JSON.

CLI example:

```powershell
py -m patchops.cli release-readiness --profile trader --core-tests-green --report-path C:\Users\Public\patchops_release_readiness.txt
```

PowerShell launcher example:

```powershell
.\powershell\Invoke-PatchReadiness.ps1 -Profile trader -CoreTestsGreen -ReportPath C:\Users\Public\patchops_release_readiness.txt
```

Expected evidence contract:
- UTF-8 text file
- deterministic headings and label wording
- explicit wrapper root, focused profile, status, core test state, missing surfaces, issues, and recommended commands
- suitable for archiving alongside release/freeze notes
<!-- PATCHOPS_PATCH57_RELEASE_EVIDENCE_GUIDANCE:END -->

<!-- PATCHOPS_PATCH58_RELEASE_TEST_SURFACE:START -->
## Release-readiness test surface

The release-readiness command is now expected to confirm not only docs, examples, workflows, and launchers, but also the maintained release-test surface itself.

At minimum, the release gate should be able to see:
- `tests/test_release_readiness_command.py`
- `tests/test_powershell_readiness_launcher.py`
- `tests/test_profile_summary_command.py`
- `tests/test_powershell_launchers.py`

This does not replace `py -m pytest -q`.
It makes the maintained release contract more explicit and easier to audit.
<!-- PATCHOPS_PATCH58_RELEASE_TEST_SURFACE:END -->
