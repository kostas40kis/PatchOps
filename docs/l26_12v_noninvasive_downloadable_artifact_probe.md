# L26.12V Non-Invasive Downloadable Artifact Probe

L26.12U accepted the single-upload contract: exactly one short safe copy whose bytes matched the inner PatchOps apply report was uploaded, submitted, and followed by idle/readiness observation.

L26.12V adds the first post-idle artifact detection layer. It is intentionally non-invasive:

1. reuse the L26.12U single-report upload + submit + idle flow;
2. after readiness, scan the Edge UIA tree for downloadable-artifact candidates;
3. record only counts and hashed fingerprints;
4. do not log prompt, file, or conversation text;
5. do not click links, files, or download buttons;
6. pass even when no artifact candidate exists, because this patch proves the safe probe mechanism, not download behavior.

A later patch can use this candidate inventory as the input for a separately gated download/click proof.
