# L22.4 Microsoft Edge downloaded-archive manifest validation controlled authorization gate

L22.4 adds an explicit future authorization token/readback gate after accepted L22.3b.

This is not manifest validation execution. It is a passive gate that proves the future authorization surface can be read back while all execution permissions remain false.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Manifest validation authorization is readback-only.
- Manifest validation execution allowed: false.
- Manifest validation active: false.
- Manifest validation is not performed.
- Downloaded manifest is not read.
- Archive extraction is not performed.
- Archive member bytes are not read.
- Artifact content is not read.
- Download workflow remains inactive.
- Package-run from browser remains inactive.
- Browser activity is not performed.
- ChatGPT URL may be selected but not opened.
- No Edge start.
- No Selenium import.
- No CDP use.
- No DOM scraping.
- No page inspection.
- No prompt text extraction.
- No conversation reading.
- No click/download/archive-extract/manifest-read/member-byte-read/paste/send/package-run side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Authorization token name:

```text
REQUIRED_MANIFEST_VALIDATION_AUTHORIZATION_TOKEN
```

Token value:

```text
PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY
```

Accepted meaning:

- L22.3b passive plan remains the source checkpoint.
- Default readback is not authorized.
- Authorized readback requires both the explicit flag and the token.
- Even when authorized for the future patch, manifest validation execution remains false in L22.4.

Next patch: L22.5 Microsoft Edge first controlled downloaded-archive manifest validation proof.
