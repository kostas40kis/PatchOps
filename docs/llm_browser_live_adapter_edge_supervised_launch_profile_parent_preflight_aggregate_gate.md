# L5.30 Microsoft Edge supervised launch profile parent preflight aggregate gate

L5.30 adds a passive aggregate gate over the Microsoft Edge profile-parent preflight chain.

Command:

`browser-start-supervised-launch-edge-live-start-profile-parent-preflight-aggregate-gate`

Source command:

`browser-start-supervised-launch-edge-live-start-profile-parent-preflight-readback`

Boundary:

- Microsoft Edge first.
- Opera second.
- `--allow-live-start` remains explicit operator authorization.
- `--profile-dir` remains required before any future live startup can proceed.
- dedicated non-default profile required.
- default Microsoft Edge profile remains forbidden.
- default profile path rejected before parent preflight can proceed.
- profile parent preflight aggregate gate stays model/readback-only.
- L5.28 profile parent preflight contract remains accepted.
- L5.29 profile parent preflight CLI/readback remains accepted.
- profile parent path derived by the source chain.
- profile parent filesystem probe not performed.
- profile parent directory not created.
- profile parent creation is not allowed in L5.30.
- profile parent must exist before future live start.
- profile parent probe required before future live start.
- manual user login required.
- silent auto-submit remains false.
- no Selenium import.
- no browser start.
- no Edge process start.
- no browser session creation.
- no driver creation.
- no profile directory creation.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.

The command only aggregates the accepted L5.28 and L5.29 parent-preflight surfaces. It does not call Selenium, does not launch Edge, does not probe or create filesystem paths, and does not run downloaded packages from adapter logic.

If accepted, continue with:

`L5.31 Live adapter Microsoft Edge supervised launch profile parent preflight aggregate gate CLI/readback`
