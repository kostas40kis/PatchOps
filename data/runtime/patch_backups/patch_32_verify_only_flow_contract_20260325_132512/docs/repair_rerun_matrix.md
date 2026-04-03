# PatchOps repair and rerun matrix

## Use apply when

- files need to be written or rewritten
- backups should be taken again
- validation and smoke commands must run as part of a full patch

## Use verify-only when

- the patch content is already correct
- you only need validation commands rerun
- you want a narrower evidence pass without rewriting target files

## Treat it as a wrapper-only failure when

- quoting breaks a valid command
- the report generation layer fails
- launcher argument forwarding breaks
- a compatibility issue exists in PowerShell or .NET behavior

## Treat it as a target-project failure when

- target tests fail because the repo code is wrong
- a target policy blocks the requested action by design
- the manifest points at the wrong target root or wrong files for the repo

## Best practice

Keep repairs narrow. Prefer fixing the wrapper evidence layer without disturbing target-repo business logic when the target commands already passed.
