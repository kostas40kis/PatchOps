# L10.3 Microsoft Edge executable filesystem probe explicit activation fixture matrix

L10.3 adds a passive fixture matrix for the accepted L10.2 Microsoft Edge executable filesystem-probe explicit activation CLI/readback.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-activation-fixture-matrix`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-activation-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L10.2 explicit activation CLI/readback remains accepted.
- explicit activation fixture matrix enforced.
- explicit activation CLI/readback enforced.
- explicit activation contract enforced.
- explicit activation modeled only.
- `no_activation_no_auth` fixture modeled.
- `activation_only` fixture modeled.
- `live_and_probe_auth_without_activation` fixture modeled.
- `all_gates_dedicated_profile` fixture modeled.
- `all_gates_default_profile` fixture modeled.
- `all_gates_missing_profile` fixture modeled.
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

`L10.4 Live adapter Microsoft Edge executable filesystem probe explicit activation fixture matrix CLI/readback`
