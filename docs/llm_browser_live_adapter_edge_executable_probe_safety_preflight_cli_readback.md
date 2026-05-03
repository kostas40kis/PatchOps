# L8.2 Microsoft Edge executable probe safety preflight CLI/readback

L8.2 adds a passive CLI/readback layer for the accepted L8.1 Microsoft Edge executable-probe safety preflight contract.

Command:

`browser-start-supervised-launch-edge-executable-probe-safety-preflight-readback`

Source command:

`browser-start-supervised-launch-edge-executable-probe-safety-preflight-contract`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L8.1 executable probe safety preflight passive contract remains accepted.
- safety preflight CLI/readback enforced.
- safety preflight modeled only.
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

`L8.3 Live adapter Microsoft Edge executable probe safety preflight fixture matrix`
