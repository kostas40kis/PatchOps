# L6.7 Microsoft Edge executable discovery broad validation checkpoint

L6.7 adds a passive broad validation checkpoint for the Microsoft Edge executable-discovery line.

Command:

`browser-start-supervised-launch-edge-executable-discovery-broad-validation-checkpoint`

Source command:

`browser-start-supervised-launch-edge-executable-discovery-aggregate-readback`

This patch keeps brief validation output and compact JSON readback. Nested source summaries remain pruned and exposed only as compact `source_chain_status`.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L6.1 executable discovery passive contract remains accepted.
- L6.2 executable discovery CLI/readback remains accepted.
- L6.3 executable discovery fixture matrix remains accepted.
- L6.4 executable discovery fixture matrix CLI/readback remains accepted.
- L6.5 executable discovery aggregate gate remains accepted.
- L6.6 executable discovery aggregate CLI/readback remains accepted.
- nested source summaries remain pruned.
- source_chain_status is retained as the compact source-chain proof.
- executable discovery broad validation checkpoint enforced.
- Edge executable candidate paths remain modeled.
- fixture matrix remains modeled.
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

`L6.8 Live adapter Microsoft Edge executable discovery final acceptance marker`
