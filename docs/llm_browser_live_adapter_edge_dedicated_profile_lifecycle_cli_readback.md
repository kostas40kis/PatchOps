# L14.5 Microsoft Edge dedicated profile lifecycle CLI/readback

L14.5 adds a passive CLI/readback layer over the accepted L14.4 Microsoft Edge dedicated profile lifecycle preflight.

Command:

`browser-start-supervised-launch-edge-dedicated-profile-lifecycle-cli-readback`

Source command:

`browser-start-supervised-launch-edge-dedicated-profile-lifecycle-preflight`

Boundary:

- L14.4 profile lifecycle preflight remains accepted.
- dedicated profile lifecycle CLI/readback enforced.
- profile readback truthful.
- profile lifecycle CLI/readback is passive.
- profile candidate under allowed runtime root.
- profile lifecycle steps are passive.
- profile directory creation deferred.
- profile directory create allowed: false.
- profile directory cleanup allowed: false.
- profile directory delete allowed: false.
- profile directory created: false.
- profile directory mutated: false.
- filesystem writes performed: none.
- launch execution allowed: false.
- operator review required before live start.
- Microsoft Edge first.
- Opera second.
- no Selenium import.
- no browser start.
- no Edge process start.
- no browser session creation.
- no driver creation.
- no click/download/paste/send/package-run side effect.
- no git commit or git push.
- no localhost PatchOps server.
- no browser extension.

CLI/readback behavior:

- The default profile candidate is read back as `data/runtime/browser_profiles/edge_supervised_l14`.
- The profile candidate must stay under `data/runtime/browser_profiles`.
- A candidate outside the allowed root fails closed without creating or mutating any directory.
- Compact JSON is supported with `--json --compact`.

If accepted, continue with:

`L14.6 Microsoft Edge dedicated profile lifecycle aggregate gate, still no launch`
