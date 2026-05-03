# L13.1a repair note

The first L13.1 attempt failed because the validation expected the injected fixture path to be the selected executable.

That expectation is too strict on a workstation where a real Microsoft Edge executable exists earlier in the allowlisted candidate order. The repaired tests now assert the truthful contract:

- the read-only probe runs only when the accepted L12 execution preflight is ready;
- the injected fixture is observed as an existing candidate;
- the selected path, if any, is one of the reported existing file candidates;
- no executable launch, Selenium import, browser start, profile write, click/download, paste/send, package-run, commit, or push occurs.
