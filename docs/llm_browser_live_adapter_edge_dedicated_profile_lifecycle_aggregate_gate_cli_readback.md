# L14.7 Microsoft Edge dedicated profile lifecycle aggregate gate CLI/readback

L14.7 adds a passive CLI/readback layer over the accepted L14.6 Microsoft Edge dedicated profile lifecycle aggregate gate.

Command:

`browser-start-supervised-launch-edge-dedicated-profile-lifecycle-aggregate-gate-cli-readback`

Source command:

`browser-start-supervised-launch-edge-dedicated-profile-lifecycle-aggregate-gate`

Boundary:

- L14.6 profile lifecycle aggregate gate remains accepted.
- dedicated profile lifecycle aggregate gate CLI/readback enforced.
- profile aggregate CLI/readback truthful.
- profile aggregate CLI/readback is passive.
- profile aggregate truthful.
- profile aggregate gate is passive.
- profile readback truthful.
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

- The aggregate gate remains the source of truth.
- The CLI/readback layer adds compact JSON readback over the accepted aggregate gate.
- The CLI/readback layer fails closed when the profile candidate is outside `data/runtime/browser_profiles`.
- The CLI/readback layer does not create, delete, clean, or mutate profile directories.

If accepted, continue with:

`L14.8 Microsoft Edge dedicated profile lifecycle broad validation checkpoint, still no launch`
