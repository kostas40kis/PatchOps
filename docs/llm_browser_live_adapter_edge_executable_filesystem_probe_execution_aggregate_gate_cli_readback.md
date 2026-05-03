# L13.6 Microsoft Edge executable filesystem probe execution aggregate gate CLI/readback

L13.6 adds a passive CLI/readback layer over the accepted L13.5 Microsoft Edge executable filesystem probe execution aggregate gate.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-aggregate-gate-readback`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-aggregate-gate`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L13.5 aggregate gate remains accepted.
- L13.4 fixture matrix CLI/readback remains accepted.
- L13.3 execution fixture matrix remains accepted.
- L13.2 execution CLI/readback remains accepted.
- L13.1 execution contract remains accepted.
- L12 execution preflight stack accepted.
- execution aggregate gate CLI/readback enforced.
- execution aggregate gate enforced.
- execution fixture matrix CLI/readback enforced.
- execution fixture matrix enforced.
- execution CLI/readback enforced.
- execution contract enforced.
- preserve the L13.1/L13.1a truthful-selection contract.
- read-only filesystem probe.
- small allowlisted Microsoft Edge executable candidate list.
- filesystem probe may be performed only when L12 execution preflight readiness is true.
- selected path, if any, is an existing reported candidate.
- no Selenium import.
- no browser start.
- no Edge process start.
- no executable launch attempted.
- no browser session creation.
- no driver creation.
- no profile directory creation.
- no click/download/paste/send/package-run side effect.
- no git commit or git push.
- no localhost PatchOps server.
- no browser extension.

If accepted, continue with:

`L13.7 Live adapter Microsoft Edge executable filesystem probe execution broad validation checkpoint`
