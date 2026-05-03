# L6.2 Microsoft Edge executable discovery CLI/readback

L6.2 adds a passive CLI/readback layer for the accepted L6.1 Microsoft Edge executable discovery contract.

Command:

`browser-start-supervised-launch-edge-executable-discovery-readback`

Source command:

`browser-start-supervised-launch-edge-executable-discovery-contract`

This patch keeps brief validation output: validation captures large JSON internally and prints only short PASS summaries.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- L6.1 executable discovery passive contract remains accepted.
- Edge executable candidate paths remain modeled.
- `msedge.exe` candidates remain listed for future discovery logic.
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

`L6.3 Live adapter Microsoft Edge executable discovery fixture matrix`
