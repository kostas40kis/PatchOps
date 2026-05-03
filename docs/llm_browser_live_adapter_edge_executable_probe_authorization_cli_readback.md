# L7.2 Microsoft Edge executable probe authorization CLI/readback

L7.2 adds a passive CLI/readback layer for the accepted L7.1 Microsoft Edge executable-probe authorization contract.

Command:

`browser-start-supervised-launch-edge-executable-probe-authorization-readback`

Source command:

`browser-start-supervised-launch-edge-executable-probe-authorization-contract`

This patch keeps brief validation output and compact JSON readback. Nested source summaries remain pruned and exposed only as compact source status.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L7.1 executable probe authorization passive contract remains accepted.
- `--allow-executable-probe` remains the explicit future authorization flag.
- executable probe authorization CLI/readback enforced.
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

`L7.3 Live adapter Microsoft Edge executable probe authorization fixture matrix`
