# L6.5 Microsoft Edge executable discovery aggregate gate

L6.5 adds a passive aggregate gate for the Microsoft Edge executable-discovery line.

Command:

`browser-start-supervised-launch-edge-executable-discovery-aggregate-gate`

Source command:

`browser-start-supervised-launch-edge-executable-discovery-fixture-matrix-readback`

This patch keeps brief validation output: validation captures large JSON internally and prints only short PASS summaries.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L6.1 executable discovery passive contract remains accepted.
- L6.2 executable discovery CLI/readback remains accepted.
- L6.3 executable discovery fixture matrix remains accepted.
- L6.4 executable discovery fixture matrix CLI/readback remains accepted.
- executable discovery aggregate gate enforced.
- Edge executable candidate paths remain modeled.
- fixture matrix remains modeled.
- `msedge.exe` candidates remain listed for future discovery logic.
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

`L6.6 Live adapter Microsoft Edge executable discovery aggregate gate CLI/readback`

## L6.5a compact JSON readback repair

L6.5a repairs the original L6.5 timeout by pruning full nested source summaries from the aggregate payload. The aggregate gate still proves L6.1 through L6.4 remain accepted, but exposes that proof as compact `source_chain_status` and boolean acceptance fields instead of echoing the entire nested chain.

This preserves brief validation output and makes `--json --compact` safe for CLI readback.
