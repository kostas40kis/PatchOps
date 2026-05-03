# L9.1 Microsoft Edge executable filesystem probe passive contract

L9.1 starts the Microsoft Edge executable filesystem-probe slice after the accepted L8 safety-preflight final marker.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-contract`

Source command:

`browser-start-supervised-launch-edge-executable-probe-safety-preflight-final-acceptance-marker`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L8 executable probe safety preflight slice accepted.
- L8.8 executable probe safety preflight final marker remains accepted.
- filesystem probe contract enforced.
- filesystem probe modeled only.
- filesystem probe not performed.
- candidate path labels modeled only.
- executable path not selected.
- executable launch not attempted.
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

`L9.2 Live adapter Microsoft Edge executable filesystem probe CLI/readback`
