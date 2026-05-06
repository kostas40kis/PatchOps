# U0.9 — ChatGPT uploader explicit send gate

U0.9 adds an explicit send gate for the PatchOps Co-Pilot uploader.

The gate is deliberately narrow:

```text
resolve normal Edge ChatGPT target
verify the target is unambiguous
verify/focus the target when requested
verify exactly one composer candidate
send only when --allow-send is present
send only when confirmation text exactly matches PATCHOPS_CONFIRM_SEND
write JSON/TXT evidence
```

Default proof is safe:

```text
provider: fake
allow_send: false
status: PASS_SEND_GATE_READY
chatgpt_submit_performed:false
```

Real Microsoft Edge remains gated:

```text
--provider pywinauto
--allow-real-edge
```

Actual send additionally requires:

```text
--allow-focus
--allow-send
--confirm-send-text PATCHOPS_CONFIRM_SEND
```

U0.9 still forbids:

```text
file upload
Selenium/WebDriver
DOM automation
CAPTCHA/Cloudflare bypass
conversation text logging
random page clicking
unbounded send loops
```

This patch does not create an unattended loop. It only creates the explicit one-shot send primitive needed by later supervised Co-Pilot steps.
