# L16.3 Microsoft Edge real-page detection passive plan checkpoint

L16.3 is a passive plan checkpoint for the first future Microsoft Edge real-page detection proof.

It is intentionally faster than L16.2: nested CLI readbacks are not performed. The patch checks that the accepted L16.2 source surfaces exist, that the command chain is registered, and that the future detection plan is safe.

## Source commands

L16.3 is layered on the L16.2 source command:

```text
browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint
```

L16.2 was layered on L16.1:

```text
browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate
```

L16.1 was layered on L15.5:

```text
browser-start-supervised-launch-edge-live-start-handoff-marker-before-real-page-detection
```

The new L16.3 command is:

```text
browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint
```

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint --repo-root C:\dev\patchops --json --compact
```

## Contract

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L16.3.
- passive plan checkpoint only.
- nested CLI readbacks are not performed.
- real-page detection is still not active.
- target URL allowlist remains enforced.
- ChatGPT URL may be planned but not opened.
- page detected means URL/title/readiness metadata only.
- no DOM scraping.
- no prompt text extraction.
- no conversation reading.
- no Microsoft Edge start.
- no Selenium import.
- no ChatGPT interaction.
- no page inspection.
- no artifact detection.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Planned detection shape

The future page-detection proof is planned but not executed:

1. Confirm explicit real-page detection authorization.
2. Start Edge with the dedicated L14 profile and an allowlisted target URL.
3. Detect page identity from safe metadata only: current URL, page title, ready state, and window count.
4. Classify ChatGPT page presence without clicking, reading conversation text, or extracting prompt text.
5. Close only the Edge process tree started by PatchOps unless a later operator flag says otherwise.
6. Emit compact readback for operator review.

## Next patch

L16.4 Microsoft Edge real-page detection controlled live plan authorization gate.
