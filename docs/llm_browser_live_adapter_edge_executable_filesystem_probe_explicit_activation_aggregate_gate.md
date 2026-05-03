# L10.5 Microsoft Edge executable filesystem probe explicit activation aggregate gate

L10.5 adds a passive aggregate gate for the accepted Microsoft Edge executable filesystem-probe explicit-activation stack.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-activation-aggregate-gate`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-activation-fixture-matrix-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L10.1 explicit activation contract remains accepted.
- L10.2 explicit activation CLI/readback remains accepted.
- L10.3 explicit activation fixture matrix remains accepted.
- L10.4 explicit activation fixture matrix CLI/readback remains accepted.
- explicit activation aggregate gate enforced.
- explicit activation fixture matrix CLI/readback enforced.
- explicit activation fixture matrix enforced.
- explicit activation CLI/readback enforced.
- explicit activation contract enforced.
- explicit activation modeled only.
- `--activate-executable-filesystem-probe` remains the explicit activation flag.
- `--allow-executable-probe` remains the explicit executable-probe authorization flag.
- activation readiness can be true while filesystem probe execution remains blocked.
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

`L10.6 Live adapter Microsoft Edge executable filesystem probe explicit activation aggregate gate CLI/readback`
