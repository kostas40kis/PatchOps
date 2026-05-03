# L25.49C operator-pasted Edge probe HTML quoting repair

L25.49C repairs the L25.49B patch-writer HTML quoting/indentation failure.

L25.49B failed before Edge could open because the generated patch writer treated the embedded HTML instruction page as Python code. L25.49C replaces the instruction page with safe string concatenation and reruns the same operator-pasted live-browser proof.

## Flow

1. PatchOps opens Microsoft Edge to a neutral instruction page.
2. The operator manually pastes/navigates to the ChatGPT conversation link.
3. The operator manually handles Cloudflare/login if needed.
4. PatchOps waits and verifies that the loaded page exposes at least one visible download or `.zip` candidate.
5. PatchOps stops.

## Boundary

Allowed:

- real Microsoft Edge start through Selenium;
- operator manual URL paste/navigation;
- operator manual Cloudflare/login handling;
- minimal DOM inspection for visible download or `.zip` candidates;
- report candidate metadata hints only.

Forbidden:

- Cloudflare bypass automation;
- PatchOps pasting the URL;
- automated download clicking;
- downloading files by PatchOps;
- reading artifact bytes;
- archive extraction;
- running `run-package`;
- pasteback;
- send/submit;
- localhost PatchOps server;
- browser extension;
- git commit or git push.

A PASS proves only that the operator-pasted live page contains a visible downloadable candidate. L25.50 may click/download only after L25.49C is accepted.

