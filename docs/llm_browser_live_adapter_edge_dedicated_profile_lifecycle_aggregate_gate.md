# L14.6 Microsoft Edge dedicated profile lifecycle aggregate gate

L14.6 adds a passive aggregate gate over the accepted L14.5 Microsoft Edge dedicated profile lifecycle CLI/readback layer.

Command:

`browser-start-supervised-launch-edge-dedicated-profile-lifecycle-aggregate-gate`

Source command:

`browser-start-supervised-launch-edge-dedicated-profile-lifecycle-cli-readback`

Boundary:

- L14.5 profile lifecycle CLI/readback remains accepted.
- dedicated profile lifecycle aggregate gate enforced.
- profile aggregate truthful.
- profile aggregate gate is passive.
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

Aggregate behavior:

- The aggregate gate fails closed when the profile candidate is outside `data/runtime/browser_profiles`.
- The aggregate gate does not create, delete, clean, or mutate profile directories.
- Compact JSON is supported with `--json --compact`.

If accepted, continue with:

`L14.7 Microsoft Edge dedicated profile lifecycle aggregate gate CLI/readback, still no launch`
