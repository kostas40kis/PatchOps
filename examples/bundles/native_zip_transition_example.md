# Native Zip Transition Example

This example exists to make the milestone concrete.

Before the native zip milestone:
- receive a zip bundle,
- manually unzip it,
- run the bundled PowerShell launcher from the extracted folder.

After the native zip milestone:
- receive a zip bundle,
- do not manually unzip it,
- start from the raw zip,
- let PatchOps extract it,
- let PatchOps call the bundled `.ps1`,
- and read the one canonical Desktop txt report.

The older manifest-driven PatchOps commands still remain supported.
The zip path is additive, not a replacement.
