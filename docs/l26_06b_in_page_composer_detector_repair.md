# L26.6B In-Page Composer Detector Repair

L26.6A repaired serialization and completed a real scan, but the highest-scoring prompt/input candidate was the Microsoft Edge address/search bar. That is browser chrome, not the ChatGPT composer.

L26.6B keeps the diagnostic-only boundary and repairs candidate quality:

- filters browser chrome and omnibox candidates;
- tracks RootWebArea / in-page scope;
- reports accepted in-page candidates separately from filtered browser chrome candidates;
- rejects a browser-chrome top candidate;
- still performs no prompt entry, prompt paste/send, clicks, downloads, run-package, or challenge bypass.

The next focus/input patch must not start until the top accepted candidate is in-page, not browser chrome.
