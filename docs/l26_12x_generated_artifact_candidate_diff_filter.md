# L26.12X Generated Artifact Candidate Diff Filter

L26.12W found two actionable artifact-like candidates, but it is not safe to click yet because those controls may be the uploaded report attachment or existing browser UI.

L26.12X adds a non-invasive diff filter:

1. scan artifact candidates before upload as a baseline;
2. run the accepted single inner PatchOps report upload + submit + idle flow;
3. scan artifact candidates after submit/idle;
4. subtract baseline fingerprints from the post-submit inventory;
5. record only novel candidate fingerprints, rectangle hashes, control types, and counts;
6. keep generated-candidate click permission disabled;
7. do not click candidates or downloads;
8. do not log prompt, file, or conversation text.

This protects the future click/download proof from accidentally clicking the uploaded input attachment or an existing browser/tab control.
