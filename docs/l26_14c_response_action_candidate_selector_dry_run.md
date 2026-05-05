# L26.14C Response Action Candidate Selector Dry Run

L26.14B proved the response state can be classified as stable across two UIA snapshots. L26.14C adds a safe selector dry run before any future interaction.

L26.14C:

1. uploads the stable latest canonical browser-evidence report as the single browser target;
2. submits and observes idle/readiness;
3. publishes the next current canonical report and updates the latest pointer;
4. runs the response-readiness stability classifier;
5. scans the UIA tree for response-action/composer candidates;
6. selects the best candidate by rank, control type, fingerprint hash, and rectangle hash;
7. records only hashes, geometry hashes, ranks, and coarse candidate kinds;
8. does not click the selected candidate;
9. does not log labels, prompt text, conversation text, or file content;
10. does not use DOM/WebDriver/Selenium or run-package.

This prepares the future explicitly-gated interaction patch while keeping L26.14C itself non-invasive.
