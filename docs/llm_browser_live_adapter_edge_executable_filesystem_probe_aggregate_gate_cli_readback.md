# L9.6 Microsoft Edge executable filesystem probe aggregate gate CLI/readback

L9.6 adds a passive CLI/readback layer for the accepted L9.5 Microsoft Edge executable filesystem-probe aggregate gate.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-aggregate-readback`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-aggregate-gate`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L9.5 executable filesystem probe aggregate gate remains accepted.
- L9.1 executable filesystem probe passive contract remains accepted.
- L9.2 executable filesystem probe CLI/readback remains accepted.
- L9.3 executable filesystem probe fixture matrix remains accepted.
- L9.4 executable filesystem probe fixture matrix CLI/readback remains accepted.
- filesystem probe aggregate gate CLI/readback enforced.
- filesystem probe aggregate gate enforced.
- filesystem probe modeled only.
- filesystem probe fixture matrix remains modeled.
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

`L9.7 Live adapter Microsoft Edge executable filesystem probe broad validation checkpoint`
