# L26.12W Actionable Artifact Candidate Inventory

L26.12V safely proved that post-idle artifact-like candidates can be detected without clicking. It found artifact candidates and recorded only hashes/counts.

L26.12W makes that candidate list actionable for a later gated click/download proof while still being non-invasive:

1. reuse the L26.12U single inner PatchOps report upload + submit + idle flow;
2. scan Edge UIA after readiness;
3. identify artifact-like controls;
4. record hashed candidate fingerprints;
5. record hashed rectangles and basic actionability counts;
6. record control types only, not labels/text;
7. do not click candidates or downloads;
8. do not log prompt, file, or conversation text.

This patch prepares the selection layer for a future explicitly-gated candidate click/download proof.
