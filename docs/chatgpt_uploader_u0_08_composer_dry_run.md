# U0.8 — ChatGPT uploader paste-to-composer dry run

U0.8 adds a safe paste-to-composer dry-run gate for the PatchOps Co-Pilot uploader.

The layer can:

```text
resolve a normal Edge ChatGPT target candidate
verify that the target is unambiguous
count composer candidates
prepare a dry-run payload
optionally paste only when explicitly gated
write JSON/TXT evidence
```

Default validation uses the fake provider. Real Edge access requires:

```text
--provider pywinauto
--allow-real-edge
```

Actual paste additionally requires:

```text
--allow-paste
```

U0.8 still forbids:

```text
file upload
send/submit
Selenium/WebDriver
DOM automation
CAPTCHA/Cloudflare bypass
conversation text logging
random page clicking
```

A PASS for this patch is not permission to send. Sending is reserved for the later explicit send gate.
