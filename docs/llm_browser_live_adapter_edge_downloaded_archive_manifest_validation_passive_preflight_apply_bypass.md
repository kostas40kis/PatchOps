
# L22.1e Microsoft Edge downloaded-archive manifest validation passive preflight apply-bypass marker

L22.1e is a stabilized passive preflight marker for downloaded-archive manifest validation.

It deliberately avoids `commands.py` registration and older L-stream imports because L22.1 through L22.1d exposed hidden apply-layer failures/hangs before useful inner diagnostics were surfaced.

## Boundary

- Microsoft Edge first.
- Opera second.
- Manifest validation preflight is readback-only.
- No manifest read.
- No archive extraction.
- No archive member-byte read.
- No downloaded file byte read.
- No downloaded file stat or hash.
- No browser activity.
- No pasteback.
- No package-run.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

## Accepted meaning

Acceptance of L22.1e only means the L22 manifest-validation stream has a stable passive marker and readback payload. Real manifest reads must still be introduced by later separately gated patches.

## Next patch

L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint.
