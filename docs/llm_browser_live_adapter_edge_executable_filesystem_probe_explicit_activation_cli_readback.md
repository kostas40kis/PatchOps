# L10.2 Microsoft Edge executable filesystem probe explicit activation CLI/readback

L10.2 adds a passive CLI/readback layer for the accepted L10.1 Microsoft Edge executable filesystem-probe explicit activation contract.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-activation-readback`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-activation-contract`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L10.1 explicit activation contract remains accepted.
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

`L10.3 Live adapter Microsoft Edge executable filesystem probe explicit activation fixture matrix`
