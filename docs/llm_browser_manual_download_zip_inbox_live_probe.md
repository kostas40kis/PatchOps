# L25.49A manual zip path or latest Downloads zip live probe

L25.49A repairs the L25.49 manual-download bridge usability.

L25.49 required a new zip created after validation started. That is too brittle for the operator loop because the zip may already exist by the time PatchOps starts watching, the browser may preserve an older modified time, or the operator may need to choose the exact downloaded file.

L25.49A accepts either:

1. an explicit `--zip-path` selected by the operator, or
2. the latest recent `.zip` in the watched Downloads/inbox folder.

## Boundary

Allowed:

- validate a real local `.zip` selected by the operator;
- validate the latest recent `.zip` in Downloads;
- stable-size checks;
- zip container validity checks;
- record the path, filename, size, and evidence in the PatchOps report.

Forbidden:

- Cloudflare bypass automation;
- browser automation;
- Selenium use;
- ChatGPT DOM scraping;
- automated download clicking;
- archive extraction;
- running `run-package`;
- pasteback;
- send/submit;
- localhost PatchOps server;
- browser extension;
- git commit or git push.

L25.50 may run `run-package` against the validated zip only after L25.49A is accepted.

