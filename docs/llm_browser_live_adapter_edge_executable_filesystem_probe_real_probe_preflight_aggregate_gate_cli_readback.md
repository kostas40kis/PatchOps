# L11.6 Microsoft Edge executable filesystem probe real-probe preflight aggregate gate CLI/readback

L11.6 adds a passive CLI/readback layer over the accepted L11.5 real-probe preflight aggregate gate.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-real-probe-preflight-aggregate-readback`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-real-probe-preflight-aggregate-gate`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L11.5 real-probe preflight aggregate gate remains accepted.
- L11.1 real-probe preflight contract remains accepted.
- L11.2 real-probe preflight CLI/readback remains accepted.
- L11.3 real-probe preflight fixture matrix remains accepted.
- L11.4 real-probe preflight fixture matrix CLI/readback remains accepted.
- real-probe preflight aggregate gate CLI/readback enforced.
- real-probe preflight aggregate gate enforced.
- real-probe preflight fixture matrix CLI/readback enforced.
- real-probe preflight fixture matrix enforced.
- real-probe preflight CLI/readback enforced.
- real-probe preflight contract enforced.
- real filesystem probe requires a separate explicit preflight flag.
- six real-probe preflight fixtures remain stable.
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

`L11.7 Live adapter Microsoft Edge executable filesystem probe real-probe preflight broad validation checkpoint`
