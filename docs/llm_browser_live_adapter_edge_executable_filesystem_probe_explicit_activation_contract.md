# L10.1 Microsoft Edge executable filesystem probe explicit activation contract

L10.1 starts the Microsoft Edge executable filesystem-probe explicit-activation layer after the accepted L9 passive filesystem-probe slice.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-activation-contract`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-final-acceptance-marker`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L9 executable filesystem probe passive slice accepted.
- L9.8 executable filesystem probe final marker remains accepted.
- explicit activation contract enforced.
- explicit activation modeled only.
- `--activate-executable-filesystem-probe` is the new explicit activation flag.
- `--allow-executable-probe` remains the explicit executable-probe authorization flag.
- activation requires live-start authorization, executable-probe authorization, and explicit filesystem-probe activation.
- activation can be requested while filesystem probe execution remains blocked by phase.
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

`L10.2 Live adapter Microsoft Edge executable filesystem probe explicit activation CLI/readback`
