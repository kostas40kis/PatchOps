# L9.3 Microsoft Edge executable filesystem probe fixture matrix

L9.3 adds a passive fixture matrix for the accepted L9.2 Microsoft Edge executable filesystem-probe CLI/readback layer.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-fixture-matrix`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L9.2 executable filesystem probe CLI/readback remains accepted.
- filesystem probe fixture matrix enforced.
- filesystem probe modeled only.
- `no_auth_dedicated_profile` fixture modeled.
- `live_auth_without_probe_auth` fixture modeled.
- `probe_auth_dedicated_profile` fixture modeled.
- `probe_auth_default_profile` fixture modeled.
- `probe_auth_missing_profile` fixture modeled.
- candidate path labels modeled only.
- filesystem probe not performed.
- executable path not selected.
- executable launch not attempted.
- filesystem probe readback can report contract_ready=true while filesystem probe remains blocked.
- preflight readback can succeed while preflight_passed is false.
- Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok.
- `--allow-executable-probe` remains the explicit future authorization flag.
- authorization can be present but filesystem probe execution remains blocked by phase.
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

`L9.4 Live adapter Microsoft Edge executable filesystem probe fixture matrix CLI/readback`
