# L6.6 Microsoft Edge executable discovery aggregate gate CLI/readback

L6.6 adds a passive CLI/readback layer for the accepted L6.5/L6.5a Microsoft Edge executable discovery aggregate gate.

Command:

`browser-start-supervised-launch-edge-executable-discovery-aggregate-readback`

Source command:

`browser-start-supervised-launch-edge-executable-discovery-aggregate-gate`

This patch keeps brief validation output and compact JSON readback. Nested source summaries remain pruned and exposed only as compact `source_chain_status`.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L6.5 executable discovery aggregate gate remains accepted.
- nested source summaries remain pruned.
- source_chain_status is retained as the compact source-chain proof.
- executable discovery aggregate gate CLI/readback enforced.
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

`L6.7 Live adapter Microsoft Edge executable discovery broad validation checkpoint`
