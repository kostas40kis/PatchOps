# L22.3b Microsoft Edge downloaded-archive manifest validation passive plan checkpoint

L22.3b is a launcher-direct repair for the L22.3/L22.3a hang seam.

It defines a passive manifest-validation plan after accepted L22.1e and L22.2 evidence.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- Manifest validation plan is readback-only.
- Manifest validation execution allowed: false.
- Manifest validation active: false.
- Manifest validation is not performed.
- Downloaded manifest is not read.
- Archive extraction is not performed.
- Archive member bytes are not read.
- Browser activity is not performed.
- Pasteback remains inactive.
- Package-run from browser remains inactive.
- No Selenium import.
- No CDP use.
- No DOM scraping.
- No prompt text extraction.
- No conversation reading.
- No artifact content reading.
- No click/download/archive-extract/manifest-read/member-byte-read/paste/send/package-run side effect.

Next patch: L22.4 Microsoft Edge downloaded-archive manifest validation controlled authorization gate.
