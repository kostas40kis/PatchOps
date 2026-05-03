
# L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint apply-bypass

L22.2 proves the accepted L22.1e manifest-validation passive preflight marker through direct module readback.

This patch deliberately keeps the L22.1e apply-bypass style because L22.1c and L22.1d exposed a PatchOps apply validation-command hang seam.

## Boundary

- Microsoft Edge first.
- Opera second.
- Manifest validation CLI/readback checkpoint is readback-only.
- L22.1e marker remains accepted.
- Default manifest preflight readback remains passive.
- Authorized manifest preflight readback remains passive.
- Manifest validation preflight authorization remains readback-only.
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
- No commands.py registration.
- Zero PatchOps validation commands expected.

## Expected readback

The bounded post-apply self-check should confirm:

- `ok:true`.
- `patch:"L22.2"`.
- `l22_1e_marker_accepted:true`.
- `default_manifest_preflight_readback_ok:true`.
- `authorized_manifest_preflight_readback_ok:true`.
- `default_manifest_validation_preflight_authorized:false`.
- `authorized_manifest_validation_preflight_authorized:true`.
- `manifest_validation_preflight_authorization_remains_readback_only:true`.
- `downloaded_manifest_read:false`.
- `downloaded_archive_extracted:false`.
- `downloaded_archive_member_bytes_read:false`.
- `browser_started:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L22.3 Microsoft Edge downloaded-archive manifest validation passive plan checkpoint.
