# L13.1 Microsoft Edge executable filesystem probe execution contract

L13.1 starts the read-only executable filesystem probe layer after the accepted L12 execution preflight stack.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-contract`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-final-acceptance-marker`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L12 execution preflight stack accepted.
- L12.8 execution preflight final acceptance marker remains accepted.
- execution contract enforced.
- read-only filesystem probe.
- small allowlisted Microsoft Edge executable candidate list.
- filesystem probe may be performed only when L12 execution preflight readiness is true.
- executable path may be selected if an allowlisted candidate exists.
- `--allow-executable-filesystem-probe-execution` remains the explicit execution-preflight flag.
- `--allow-real-filesystem-probe` remains the explicit real-probe preflight flag.
- `--activate-executable-filesystem-probe` remains the explicit activation flag.
- `--allow-executable-probe` remains the explicit executable-probe authorization flag.
- no Selenium import.
- no browser start.
- no Edge process start.
- no executable launch attempted.
- no browser session creation.
- no driver creation.
- no profile directory creation.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.

If accepted, continue with:

`L13.2 Live adapter Microsoft Edge executable filesystem probe execution CLI/readback`
- the selected path, if any, is the first existing file from the reported candidate order.
- the fixture candidate may be observed without being selected when a real Edge executable appears earlier in the allowlisted order.
