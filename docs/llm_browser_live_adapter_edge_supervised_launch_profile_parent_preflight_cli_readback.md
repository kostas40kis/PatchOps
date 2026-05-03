# L5.29 Microsoft Edge supervised launch profile parent preflight CLI/readback

L5.29 adds a passive CLI/readback layer for the accepted L5.28 Microsoft Edge profile parent preflight contract.

Command:

`browser-start-supervised-launch-edge-live-start-profile-parent-preflight-readback`

Source command:

`browser-start-supervised-launch-edge-live-start-profile-parent-preflight-contract`

Boundary:

- Microsoft Edge first.
- Opera second.
- `--allow-live-start` remains explicit operator authorization.
- `--profile-dir` remains required before any future live startup can proceed.
- dedicated non-default profile required.
- default Microsoft Edge profile remains forbidden.
- default profile path rejected before parent preflight can proceed.
- profile parent preflight CLI/readback stays model/readback-only.
- profile parent path derived by the L5.28 source contract.
- profile parent filesystem probe not performed.
- profile parent directory not created.
- profile parent creation is not allowed in L5.29.
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

The command only reads back the accepted L5.28 source contract through module and `patchops.cli llm-browser` surfaces. It does not call Selenium, does not launch Edge, does not probe or create filesystem paths, and does not run downloaded packages from adapter logic.

If accepted, continue with:

`L5.30 Live adapter Microsoft Edge supervised launch profile parent preflight aggregate gate`
