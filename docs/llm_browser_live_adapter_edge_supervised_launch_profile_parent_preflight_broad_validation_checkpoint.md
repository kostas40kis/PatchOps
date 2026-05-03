# L5.32 Microsoft Edge supervised launch profile parent preflight broad validation checkpoint

L5.32 adds a passive broad validation checkpoint for the Microsoft Edge profile-parent preflight chain.

Command:

`browser-start-supervised-launch-edge-live-start-profile-parent-preflight-broad-validation-checkpoint`

Source command:

`browser-start-supervised-launch-edge-live-start-profile-parent-preflight-aggregate-readback`

This checkpoint keeps the L5.31a brief validation output approach: validation captures large JSON internally and prints only short PASS summaries.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- L5.28 profile parent preflight contract remains accepted.
- L5.29 profile parent preflight CLI/readback remains accepted.
- L5.30 profile parent preflight aggregate gate remains accepted.
- L5.31 profile parent preflight aggregate CLI/readback remains accepted.
- dedicated non-default profile remains required.
- default Microsoft Edge profile remains forbidden.
- profile parent filesystem probe not performed.
- profile parent directory not created.
- no Selenium import.
- no browser start.
- no Edge process start.
- no browser session creation.
- no driver creation.
- no profile directory creation.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.

If accepted, continue with:

`L5.33 Live adapter Microsoft Edge supervised launch profile parent preflight final acceptance marker`
