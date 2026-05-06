# U1.0 — ChatGPT uploader content pasteback fallback

U1.0 adds the local content-pasteback fallback builder for PatchOps Co-Pilot.

It is an offline/local builder. It does not open a browser, paste into ChatGPT, upload a file, or send a message.

## Purpose

When full file upload is unavailable or not desired, the uploader needs a safe text payload that can be delivered later by the already-built paste/send gates.

U1.0 supports:

```text
small safe report -> full report content pasteback payload
large report      -> compact summary only
unsafe-looking report -> compact summary only
empty report      -> blocked
```

Chunking is deliberately not implemented in U1.0. Chunked pasteback belongs to U1.1.

## Safety boundary

U1.0 preserves:

```text
file_upload_attempted:false
chatgpt_submit_performed:false
selenium_used:false
webdriver_used:false
browser_dom_automation_used:false
cloudflare_bypass_attempted:false
captcha_bypass_attempted:false
conversation_text_logged:false
clipboard_written:false
paste_attempted:false
```

## Output artifacts

The runner writes:

```text
content_pasteback_payload.txt
content_pasteback_result.json
```

The payload uses:

```text
PATCHOPS_REPORT_CONTENT_PASTEBACK
...
END_PATCHOPS_REPORT_CONTENT_PASTEBACK
```

U1.0 must not emit `PATCHOPS_REPORT_CHUNK`; that marker is reserved for U1.1.
