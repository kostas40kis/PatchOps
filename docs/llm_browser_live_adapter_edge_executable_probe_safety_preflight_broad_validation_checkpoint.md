# L8.7 Microsoft Edge executable probe safety preflight broad validation checkpoint

L8.7 adds a passive broad validation checkpoint for the accepted Microsoft Edge executable-probe safety preflight stack.

Command:

`browser-start-supervised-launch-edge-executable-probe-safety-preflight-broad-validation-checkpoint`

Source command:

`browser-start-supervised-launch-edge-executable-probe-safety-preflight-aggregate-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L8.1 executable probe safety preflight passive contract remains accepted.
- L8.2 executable probe safety preflight CLI/readback remains accepted.
- L8.3 executable probe safety preflight fixture matrix remains accepted.
- L8.4 executable probe safety preflight fixture matrix CLI/readback remains accepted.
- L8.5 executable probe safety preflight aggregate gate remains accepted.
- L8.6 executable probe safety preflight aggregate CLI/readback remains accepted.
- safety preflight broad validation checkpoint enforced.
- fixture matrix modeled.
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

`L8.8 Live adapter Microsoft Edge executable probe safety preflight final acceptance marker`
