# L12.5 Microsoft Edge executable filesystem probe execution preflight aggregate gate

L12.5 adds a passive aggregate gate over the accepted L12 execution preflight stack.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-aggregate-gate`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-fixture-matrix-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L12.1 execution preflight contract remains accepted.
- L12.2 execution preflight CLI/readback remains accepted.
- L12.3 execution preflight fixture matrix remains accepted.
- L12.4 execution preflight fixture matrix CLI/readback remains accepted.
- execution preflight aggregate gate enforced.
- execution preflight fixture matrix CLI/readback enforced.
- execution preflight fixture matrix enforced.
- execution preflight CLI/readback enforced.
- execution preflight contract enforced.
- filesystem probe execution requires a separate explicit execution-preflight flag.
- six execution preflight fixtures remain stable.
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

`L12.6 Live adapter Microsoft Edge executable filesystem probe execution preflight aggregate gate CLI/readback`
