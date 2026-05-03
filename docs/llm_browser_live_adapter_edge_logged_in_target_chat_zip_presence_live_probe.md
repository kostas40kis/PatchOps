# L25.48A Microsoft Edge logged-in target-chat zip-presence live probe writer quoting repair

L25.48A repairs the L25.48 patch-writer syntax error caused by nested Python raw triple-single-quoted strings around an embedded JavaScript probe.

This repair keeps the same live-browser goal: real Microsoft Edge is the main proof, not synthetic fixture data.

## Goal

Start Microsoft Edge, load the operator-provided ChatGPT conversation, and confirm that a visible `.zip` artifact candidate exists.

## Boundary

Allowed:

- real Microsoft Edge start;
- Selenium import and WebDriver session creation;
- dedicated PatchOps Edge profile directory;
- target ChatGPT URL load;
- minimal DOM artifact-candidate inspection for `.zip` text.

Forbidden:

- clicking download;
- downloading a file;
- reading downloaded file bytes;
- reading artifact content;
- running `run-package` from the browser workflow;
- pasteback;
- send/submit;
- localhost PatchOps server;
- browser extension;
- git commit;
- git push.

A FAIL is useful live evidence and should identify the first real blocker: Selenium dependency, Edge driver/session, login/profile mismatch, target URL access, or selector/artifact detection.

