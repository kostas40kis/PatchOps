# L5.31 Microsoft Edge supervised launch profile parent preflight aggregate gate CLI/readback

L5.31 adds a passive CLI/readback layer for the accepted L5.30 Microsoft Edge profile parent preflight aggregate gate.

Command:

`browser-start-supervised-launch-edge-live-start-profile-parent-preflight-aggregate-readback`

Source command:

`browser-start-supervised-launch-edge-live-start-profile-parent-preflight-aggregate-gate`

This patch also changes the validation style for this line of work: validation uses brief validation output by capturing large JSON payloads inside Python and printing only a small PASS summary. This is meant to avoid giant Desktop reports.

Boundary:

- Microsoft Edge first.
- Opera second.
- profile parent aggregate gate remains accepted.
- profile parent filesystem probe not performed.
- profile parent directory not created.
- default Microsoft Edge profile remains forbidden.
- no Selenium import.
- no browser start.
- no Edge process start.
- no profile directory creation.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.

If accepted, continue with:

`L5.32 Live adapter Microsoft Edge supervised launch profile parent preflight broad validation checkpoint`

## L5.31a brief validator import-path repair

L5.31a repairs the L5.31 brief validator. Running `python scripts/patch_l5_31_brief_validate.py` places `scripts/` on `sys.path`, so the local `patchops` package was not importable. The repair inserts the repository root into `sys.path` before importing PatchOps modules.

The successful-report-size improvement remains: the validator parses JSON internally and prints only short PASS lines instead of echoing full nested payloads.

If accepted, continue with:

`L5.32 Live adapter Microsoft Edge supervised launch profile parent preflight broad validation checkpoint`
