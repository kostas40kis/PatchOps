# L11.1 Microsoft Edge executable filesystem probe real-probe preflight contract

L11.1 starts the real-probe preparation layer after the accepted L10 explicit activation stack.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-real-probe-preflight-contract`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-activation-final-acceptance-marker`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L10 explicit activation stack accepted.
- L10.8 explicit activation final acceptance marker remains accepted.
- real-probe preflight contract enforced.
- real filesystem probe requires a separate explicit preflight flag.
- `--allow-real-filesystem-probe` is modeled but does not perform a filesystem probe yet.
- `--activate-executable-filesystem-probe` remains the explicit activation flag.
- `--allow-executable-probe` remains the explicit executable-probe authorization flag.
- real-probe preflight readiness can be true while filesystem probe execution remains blocked.
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

`L11.2 Live adapter Microsoft Edge executable filesystem probe real-probe preflight CLI/readback`
