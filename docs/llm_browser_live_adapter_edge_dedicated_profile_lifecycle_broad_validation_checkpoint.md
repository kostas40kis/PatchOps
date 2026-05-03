# L14.8 Microsoft Edge dedicated profile lifecycle broad validation checkpoint

L14.8 adds a passive broad validation checkpoint over the accepted L14.7 Microsoft Edge dedicated profile lifecycle aggregate gate CLI/readback layer.

Command:

`browser-start-supervised-launch-edge-dedicated-profile-lifecycle-broad-validation-checkpoint`

Source command:

`browser-start-supervised-launch-edge-dedicated-profile-lifecycle-aggregate-gate-cli-readback`

Boundary:

- L14.7 profile lifecycle aggregate gate CLI/readback remains accepted.
- dedicated profile lifecycle broad validation checkpoint enforced.
- planned broad-validation commands are readback only.
- no validation commands are executed by adapter logic.
- profile broad checkpoint truthful.
- profile broad checkpoint is passive.
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

Broad checkpoint behavior:

- Planned validation commands are exposed as strings and are not run by adapter logic.
- The PatchOps direct-manifest validation for this patch runs focused L14 compile, brief readback, and pytest evidence separately.
- The checkpoint fails closed when the profile candidate is outside `data/runtime/browser_profiles`.

If accepted, continue with:

`L14.9 Microsoft Edge dedicated profile lifecycle final acceptance marker, still no launch`
