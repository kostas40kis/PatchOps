# L14.4 Microsoft Edge dedicated profile lifecycle preflight

L14.4 adds a passive dedicated profile lifecycle preflight over the accepted L14.3 dry-run plan readback layer.

Command:

`browser-start-supervised-launch-edge-dedicated-profile-lifecycle-preflight`

Source command:

`browser-start-supervised-launch-edge-launch-dry-run-plan-readback`

Boundary:

- L14.3 dry-run plan remains accepted.
- dedicated profile lifecycle preflight enforced.
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

Profile lifecycle steps:

1. compute_dedicated_profile_candidate_path.
2. verify_profile_candidate_under_repo_runtime_browser_profiles.
3. record_profile_lifecycle_intent_readback_only.
4. defer_profile_directory_creation_to_future_authorized_stage.
5. stop_before_any_filesystem_write_or_browser_launch.

If accepted, continue with:

`L14.5 Microsoft Edge dedicated profile lifecycle CLI/readback, still no launch`
