# L12.1 Microsoft Edge executable filesystem probe execution preflight contract

L12.1 starts the execution-preflight layer after the accepted L11 real-probe preflight stack.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-contract`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-real-probe-preflight-final-acceptance-marker`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L11 real-probe preflight stack accepted.
- L11.8 real-probe preflight final acceptance marker remains accepted.
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

`L12.2 Live adapter Microsoft Edge executable filesystem probe execution preflight CLI/readback`
