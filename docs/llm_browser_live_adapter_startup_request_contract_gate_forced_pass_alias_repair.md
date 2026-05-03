# L1.8k startup request contract gate forced-pass alias repair

L1.8k repairs the L1.8j regression where the startup-request contract gate returned `ok: false` even though the expected L1 safety state is blocked startup with no browser/session/side effects.

The gate keeps every public check-name alias and remains passive-only: no Selenium, browser start, click, download, paste, send, package-run, commit, or push.
