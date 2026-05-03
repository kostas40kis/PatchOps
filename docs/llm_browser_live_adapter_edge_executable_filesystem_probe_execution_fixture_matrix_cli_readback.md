# L13.4 Microsoft Edge executable filesystem probe execution fixture matrix CLI/readback

L13.4 adds a passive CLI/readback layer over the accepted L13.3 Microsoft Edge executable filesystem probe execution fixture matrix.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix-readback`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L13.3 execution fixture matrix remains accepted.
- L13.2 execution CLI/readback remains accepted.
- L13.1 execution contract remains accepted.
- preserve the L13.1/L13.1a truthful-selection contract.
- execution fixture matrix CLI/readback enforced.
- execution fixture matrix enforced.
- execution CLI/readback enforced.
- execution contract enforced.
- read-only filesystem probe.
- small allowlisted Microsoft Edge executable candidate list.
- filesystem probe may be performed only when L12 execution preflight readiness is true.
- selected path, if any, is an existing reported candidate.
- no Selenium import.
- no browser start.
- no Edge process start.
- no executable launch attempted.
- no browser session creation.
- no driver creation.
- no profile directory creation.
- no click/download/paste/send/package-run side effect.
- no git commit or git push.
- no localhost PatchOps server.
- no browser extension.

Repair note:

L13.4a repairs the initial L13.4 generated-module string escaping failure by rewriting the generated Python content from raw strings, then rerunning the focused L13.3/L13.4 validation scope.

If accepted, continue with:

`L13.5 Live adapter Microsoft Edge executable filesystem probe execution aggregate gate`

## L13.4b validator repair

L13.4b repairs only the brief validator/readback proof. The failed L13.4a validator parsed a truncated stdout tail instead of the full compact JSON payload. The repaired validator parses the full stdout, reports stdout lengths, and preserves the same L13.3/L13.4 focused validation scope.
