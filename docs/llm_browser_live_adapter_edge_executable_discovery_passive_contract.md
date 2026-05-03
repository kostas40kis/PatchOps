# L6.1 Microsoft Edge executable discovery passive contract

L6.1 starts the Microsoft Edge executable-discovery slice after the accepted L5 profile-parent preflight final marker.

Command:

`browser-start-supervised-launch-edge-executable-discovery-contract`

Source command:

`browser-start-supervised-launch-edge-live-start-profile-parent-preflight-final-acceptance-marker`

This patch preserves brief validation output: validation captures large JSON internally and prints only short PASS summaries.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- L5.33 profile parent preflight final marker remains accepted.
- Edge executable candidate paths modeled.
- `msedge.exe` candidates are listed for future discovery logic.
- executable filesystem probe not performed.
- executable path not selected.
- executable launch not attempted.
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

`L6.2 Live adapter Microsoft Edge executable discovery CLI/readback`
