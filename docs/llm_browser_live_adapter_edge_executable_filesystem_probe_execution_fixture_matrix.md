# L13.3 Microsoft Edge executable filesystem probe execution fixture matrix

L13.3 adds a fixture matrix over the accepted L13.2 read-only executable filesystem probe execution CLI/readback.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L13.2 execution CLI/readback remains accepted.
- L13.1 execution contract remains accepted.
- L12 execution preflight stack accepted.
- execution fixture matrix enforced.
- execution CLI/readback enforced.
- execution contract enforced.
- read-only filesystem probe.
- small allowlisted Microsoft Edge executable candidate list.
- filesystem probe may be performed only when L12 execution preflight readiness is true.
- selected path, if any, is an existing reported candidate.
- `no_gates` fixture modeled.
- `execution_flag_only` fixture modeled.
- `real_ready_without_execution_flag` fixture modeled.
- `execution_ready_missing_extra_candidate` fixture modeled.
- `execution_ready_fixture_observed` fixture modeled.
- `--allow-executable-filesystem-probe-execution` remains the explicit execution-preflight flag.
- `--allow-real-filesystem-probe` remains the explicit real-probe preflight flag.
- `--activate-executable-filesystem-probe` remains the explicit activation flag.
- `--allow-executable-probe` remains the explicit executable-probe authorization flag.
- no Selenium import.
- no browser start.
- no Edge process start.
- no executable launch attempted.
- no browser session creation.
- no driver creation.
- no profile directory creation.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.

If accepted, continue with:

`L13.4 Live adapter Microsoft Edge executable filesystem probe execution fixture matrix CLI/readback`
