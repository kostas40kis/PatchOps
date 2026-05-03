# L5.28 Microsoft Edge supervised launch profile parent preflight contract

L5.28 adds a passive profile parent preflight contract for the Microsoft Edge supervised-launch path.

Command:

`browser-start-supervised-launch-edge-live-start-profile-parent-preflight-contract`

Source command:

`browser-start-supervised-launch-edge-live-start-default-profile-rejection-gate`

Boundary:

- Microsoft Edge first.
- Opera second.
- `--allow-live-start` remains explicit operator authorization.
- `--profile-dir` remains required before any future live startup can proceed.
- dedicated non-default profile required.
- default Microsoft Edge profile remains forbidden.
- default profile path rejected before parent preflight can proceed.
- profile parent preflight contract enforced.
- profile parent path derived.
- profile parent filesystem probe not performed.
- profile parent directory not created.
- profile parent creation is not allowed in L5.28.
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

The current contract is still model/readback-only. It derives the parent path from the supplied dedicated profile path but does not call Selenium, does not launch Edge, does not probe the filesystem for the parent, and does not create either the parent directory or the profile directory.

If accepted, continue with:

`L5.29 Live adapter Microsoft Edge supervised launch profile parent preflight CLI/readback`
