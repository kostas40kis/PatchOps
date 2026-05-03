# L9.2 Microsoft Edge executable filesystem probe CLI/readback

L9.2 adds a passive CLI/readback layer for the accepted L9.1 Microsoft Edge executable filesystem-probe contract.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-readback`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-contract`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L9.1 executable filesystem probe passive contract remains accepted.
- filesystem probe CLI/readback enforced.
- filesystem probe contract enforced.
- filesystem probe modeled only.
- filesystem probe readback can report contract_ready=true while filesystem probe remains blocked.
- candidate path labels modeled only.
- filesystem probe not performed.
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

`L9.3 Live adapter Microsoft Edge executable filesystem probe fixture matrix`
