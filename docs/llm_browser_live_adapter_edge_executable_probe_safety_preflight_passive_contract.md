# L8.1 Microsoft Edge executable probe safety preflight passive contract

L8.1 starts the Microsoft Edge executable-probe safety preflight slice after the accepted L7 authorization final marker.

Command:

`browser-start-supervised-launch-edge-executable-probe-safety-preflight-contract`

Source command:

`browser-start-supervised-launch-edge-executable-probe-authorization-final-acceptance-marker`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L7.8 executable probe authorization final marker remains accepted.
- L7 executable probe authorization slice accepted.
- safety preflight contract enforced.
- safety preflight modeled only.
- preflight alone does not perform a probe.
- Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok.
- `--allow-executable-probe` remains the explicit future authorization flag.
- authorization can be present but probe execution remains blocked by phase.
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

`L8.2 Live adapter Microsoft Edge executable probe safety preflight CLI/readback`
