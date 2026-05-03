# L8.3 Microsoft Edge executable probe safety preflight fixture matrix

L8.3 adds a passive fixture matrix for the accepted L8.2 Microsoft Edge executable-probe safety preflight CLI/readback surface.

Command:

`browser-start-supervised-launch-edge-executable-probe-safety-preflight-fixture-matrix`

Source command:

`browser-start-supervised-launch-edge-executable-probe-safety-preflight-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L8.2 executable probe safety preflight CLI/readback remains accepted.
- safety preflight fixture matrix enforced.
- fixture matrix modeled.
- `no_auth_dedicated_profile` fixture modeled.
- `live_auth_without_probe_auth` fixture modeled.
- `probe_auth_dedicated_profile` fixture modeled.
- `probe_auth_default_profile` fixture modeled.
- `probe_auth_missing_profile` fixture modeled.
- preflight readback can succeed while preflight_passed is false.
- Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok.
- `--allow-executable-probe` remains the explicit future authorization flag.
- authorization can be present but probe execution remains blocked by phase.
- preflight alone does not perform a probe.
- executable filesystem probe not performed.
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

`L8.4 Live adapter Microsoft Edge executable probe safety preflight fixture matrix CLI/readback`
