# L12.3 Microsoft Edge executable filesystem probe execution preflight fixture matrix

L12.3 adds a passive fixture matrix over the accepted L12.2 execution preflight CLI/readback.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-fixture-matrix`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L12.2 execution preflight CLI/readback remains accepted.
- execution preflight fixture matrix enforced.
- execution preflight CLI/readback enforced.
- execution preflight contract enforced.
- filesystem probe execution requires a separate explicit execution-preflight flag.
- `no_gates` fixture modeled.
- `execution_flag_only` fixture modeled.
- `real_ready_without_execution_flag` fixture modeled.
- `execution_preflight_ready_dedicated_profile` fixture modeled.
- `execution_preflight_ready_default_profile` fixture modeled.
- `execution_preflight_ready_missing_profile` fixture modeled.
- `--allow-executable-filesystem-probe-execution` is modeled but does not execute a filesystem probe yet.
- `--allow-real-filesystem-probe` remains the explicit real-probe preflight flag.
- `--activate-executable-filesystem-probe` remains the explicit activation flag.
- `--allow-executable-probe` remains the explicit executable-probe authorization flag.
- execution preflight readiness can be true while filesystem probe execution remains blocked.
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

`L12.4 Live adapter Microsoft Edge executable filesystem probe execution preflight fixture matrix CLI/readback`
