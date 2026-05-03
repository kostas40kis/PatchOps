# L5.27 Microsoft Edge supervised launch default profile rejection gate

L5.27 gives the future Microsoft Edge live-start path a separate passive rejection gate for the normal/default Edge profile. It reads back the accepted L5.26 profile gate and makes the default-profile boundary explicit before any real browser launch code exists.

Microsoft Edge first. Opera second.

This patch is still passive. It does not start Edge and it does not create a profile directory.

## CLI commands

Source L5.26 profile gate:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-profile-gate --repo-root C:\dev\patchops --allow-live-start --profile-dir C:\dev\patchops\data\runtime\browser_profiles\edge_l5_26_candidate --json --compact
```

L5.27 default profile rejection gate with a default profile candidate:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-default-profile-rejection-gate --repo-root C:\dev\patchops --allow-live-start --profile-dir "C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default" --json --compact
```

L5.27 default profile rejection gate with a dedicated non-default profile candidate:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-default-profile-rejection-gate --repo-root C:\dev\patchops --allow-live-start --profile-dir C:\dev\patchops\data\runtime\browser_profiles\edge_l5_27_candidate --json --compact
```

## Default profile rejection behavior

The gate reports:

- default profile rejection gate enforced;
- default Microsoft Edge profile forbidden;
- default profile candidate detected;
- default profile path rejected;
- dedicated non-default profile remains passive-blocked.

The future live-start path must never use the operator's normal Microsoft Edge profile. A candidate ending in Microsoft Edge `User Data\Default` is rejected even when `--allow-live-start` is present.

## Preserved live-start gates

The readback keeps these future live-start gates visible:

- explicit operator authorization required;
- `--allow-live-start` authorization flag required;
- `--profile-dir` dedicated profile argument required;
- dedicated profile required;
- default profile forbidden;
- manual user login required;
- silent auto-submit remains false;
- no localhost PatchOps server;
- no browser extension.

## Passive safety boundary for this patch

This patch remains readback-only. It does not perform live browser automation.

Required passive guarantees:

- no Selenium import;
- no browser start;
- no Edge process start;
- no browser session creation;
- no driver creation;
- no profile directory creation;
- no adapter filesystem writes except intended PatchOps source/docs/tests written by PatchOps;
- no click/download/paste/send/package-run side effect;
- no automatic git commit;
- no automatic git push.

## Next patch

If accepted, continue with:

`L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract`

## L5.27a missing-auth readback repair

L5.27a repairs the L5.27 missing-authorization and missing-profile readback branch. The wrapped L5.26 profile gate can legitimately report a missing authorization or missing profile refusal before it reaches default-profile rejection. L5.27a therefore treats L5.26 as healthy when it still reports PASS, remains passive, and performs no browser/profile/Selenium/click/download/paste/send/package-run side effects.

The default Microsoft Edge profile rejection behavior remains unchanged. A default Microsoft Edge profile path is still rejected when explicit authorization and a profile path are both present.

If accepted, continue with:

`L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract`

## L5.27b no-auth profile path repair

L5.27b repairs the failed L5.27a validation branch. L5.27a correctly relaxed the wrapped L5.26 passive-health check, but its validation manifest passed the default Edge profile path with an accidental control-character separator. L5.27b makes the L5.27 default-profile readback resilient to that malformed separator and makes the dedicated non-default passive-block check scenario-aware: without `--allow-live-start`, startup is blocked by missing authorization before the dedicated-profile passive branch is expected to pass.

The accepted behavior remains unchanged for the real default Microsoft Edge profile path: when `--allow-live-start` and `--profile-dir` are both present, a normal/default Microsoft Edge profile is still rejected.

If accepted, continue with:

`L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract`

## L5.27c wrapped L5.26 semantic repair

L5.27c repairs the remaining L5.27b failure. L5.27 owns default Microsoft Edge profile rejection. The wrapped L5.26 dedicated-profile gate is older and may correctly report FAIL when it is deliberately fed a default Edge profile. L5.27c therefore treats wrapped L5.26 as acceptable when either:

- L5.26 reports PASS and remains passive; or
- L5.26 reports the expected default-profile refusal while still preserving every passive safety invariant.

This keeps the real L5.27 default-profile contract intact: a normal/default Microsoft Edge profile is rejected and startup remains blocked. It also keeps missing authorization, missing profile, and dedicated non-default profile scenarios passive.

No behavior in this repair starts a browser, imports Selenium, creates a driver, creates a profile directory, clicks/downloads, pastes/sends, runs packages, commits, or pushes.

If accepted, continue with:

`L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract`

## L5.27d stale repair-test expectation repair

L5.27d repairs the stale L5.27a regression test expectation left behind after L5.27c. L5.27c correctly made the L5.27 readback accept wrapped L5.26 when L5.26 safely rejects a deliberately supplied default Microsoft Edge profile. The old L5.27a test still expected wrapped L5.26 to report `ok: true` and `status: PASS` for that default-profile input. L5.27d updates that test to assert the real invariant instead: L5.26 may refuse the default profile, but it must remain passive and must not start a browser, import Selenium, create a profile, click/download, paste/send, or run a package.

If accepted, continue with:

`L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract`
