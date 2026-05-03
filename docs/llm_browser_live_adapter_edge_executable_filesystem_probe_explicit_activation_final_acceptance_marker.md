# L10.8 Microsoft Edge executable filesystem probe explicit activation final acceptance marker

L10.8 closes the accepted Microsoft Edge executable filesystem-probe explicit-activation stack.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-activation-final-acceptance-marker`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-activation-broad-validation-checkpoint`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L10 explicit activation stack accepted.
- L10.1 explicit activation contract remains accepted.
- L10.2 explicit activation CLI/readback remains accepted.
- L10.3 explicit activation fixture matrix remains accepted.
- L10.4 explicit activation fixture matrix CLI/readback remains accepted.
- L10.5 explicit activation aggregate gate remains accepted.
- L10.6 explicit activation aggregate gate CLI/readback remains accepted.
- L10.7 explicit activation broad validation checkpoint remains accepted.
- explicit activation final acceptance marker enforced.
- explicit activation broad validation checkpoint enforced.
- explicit activation aggregate gate CLI/readback enforced.
- explicit activation aggregate gate enforced.
- explicit activation modeled only.
- six activation fixtures remain stable.
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

`L11.1 Live adapter Microsoft Edge executable filesystem probe real-probe preflight contract`
