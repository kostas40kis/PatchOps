# U0.8D — composer candidate selector repair

U0.8D repairs the live Edge dry-run blocker found after U1.0.

Observed live evidence:

```text
FocusStatus: PASS_TARGET_FOCUSED
ComposerStatus: BLOCKED_COMPOSER_NOT_UNIQUE
ComposerCandidates: 2
PasteAttempted: false
SendPerformed: false
```

The two visible UIA Edit controls likely include the Edge address/search bar plus the ChatGPT composer. U0.8C counted visible Edit controls but did not score them.

U0.8D adds a safe composer candidate selector:

```text
score UIA Edit controls
reject address/search/url/omnibox controls
prefer Message ChatGPT / Ask anything / prompt-like labels
redact unknown Edit names in evidence
paste only when exactly one high-confidence composer exists
```

Safety boundary remains:

```text
no upload
no send/submit
no Selenium/WebDriver
no DOM automation
no CAPTCHA/Cloudflare bypass
no conversation text logging
real Edge gated
actual paste gated
```
