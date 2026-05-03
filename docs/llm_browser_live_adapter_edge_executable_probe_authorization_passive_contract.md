# L7.1 Microsoft Edge executable probe authorization passive contract

L7.1 starts the Microsoft Edge executable-probe authorization slice after the accepted L6 executable-discovery final marker.

Command:

`browser-start-supervised-launch-edge-executable-probe-authorization-contract`

Source command:

`browser-start-supervised-launch-edge-executable-discovery-final-acceptance-marker`

This patch keeps brief validation output and compact JSON readback. Nested source summaries remain pruned and exposed only as compact `source_chain_status`.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L6.8 executable discovery final marker remains accepted.
- L6 executable discovery slice accepted.
- `--allow-executable-probe` is modeled as the future explicit authorization flag.
- executable probe authorization modeled.
- authorization alone does not perform a probe.
- executable probe remains blocked by phase.
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

`L7.2 Live adapter Microsoft Edge executable probe authorization CLI/readback`
