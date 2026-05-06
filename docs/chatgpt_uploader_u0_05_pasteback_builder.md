# U0.5 ChatGPT uploader PATCHOPS_LLM_PASTEBACK builder

U0.5 adds the compact pasteback text builder for the PatchOps Co-Pilot uploader stream.

It consumes the U0.4 report parser output and renders a bounded message with these markers:

```text
PATCHOPS_LLM_PASTEBACK
...
END_PATCHOPS_LLM_PASTEBACK
```

## Scope

Allowed:

```text
parse local PatchOps report evidence
build compact status/result/exit-code/failure-layer text
include canonical report path
include conservative next action
write local text/json evidence files
```

Forbidden in U0.5:

```text
clipboard writes
browser focus
Edge control
paste into ChatGPT
file upload
send/submit
Selenium/WebDriver
DOM automation
CAPTCHA or Cloudflare bypass
```

The next patch after this remains U0.6 clipboard set/verify only after U0.5 passes.
