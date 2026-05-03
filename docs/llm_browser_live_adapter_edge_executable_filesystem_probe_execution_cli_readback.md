# L13.2 Microsoft Edge executable filesystem probe execution CLI/readback

L13.2 adds a passive CLI/readback layer over the accepted L13.1 read-only executable filesystem probe execution contract.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-readback`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-contract`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L13.1 execution contract remains accepted.
- L12 execution preflight stack accepted.
- execution CLI/readback enforced.
- execution contract enforced.
- read-only filesystem probe.
- small allowlisted Microsoft Edge executable candidate list.
- filesystem probe may be performed only when L12 execution preflight readiness is true.
- selected path, if any, is an existing reported candidate.
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

`L13.3 Live adapter Microsoft Edge executable filesystem probe execution fixture matrix`
