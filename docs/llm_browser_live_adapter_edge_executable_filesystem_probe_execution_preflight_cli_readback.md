# L12.2 Microsoft Edge executable filesystem probe execution preflight CLI/readback

L12.2 adds a passive CLI/readback layer over the accepted L12.1 execution preflight contract.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-readback`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-contract`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L12.1 execution preflight contract remains accepted.
- execution preflight CLI/readback enforced.
- execution preflight contract enforced.
- filesystem probe execution requires a separate explicit execution-preflight flag.
- `--allow-executable-filesystem-probe-execution` is modeled but does not execute a filesystem probe yet.
- `--allow-real-filesystem-probe` remains the explicit real-probe preflight flag.
- `--activate-executable-filesystem-probe` remains the explicit activation flag.
- `--allow-executable-probe` remains the explicit executable-probe authorization flag.
- execution preflight readiness can be true while filesystem probe execution remains blocked.
- filesystem probe not performed.
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

`L12.3 Live adapter Microsoft Edge executable filesystem probe execution preflight fixture matrix`
