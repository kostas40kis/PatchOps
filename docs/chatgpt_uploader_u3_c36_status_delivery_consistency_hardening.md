# U3 C36 status delivery consistency hardening

Patch `u3_c36_status_delivery_consistency_hardening` adds the final no-browser consistency doctor for uploader PASS/FAIL status delivery.

## Purpose

C36 hardens the status-delivery chain with:

```text
ledger JSONL
idempotency key
exact message hash
operator report hash
selected action hash
browser lane schema
bounded retry count
bounded timeout
final doctor evidence
```

## Matrix preserved

```text
PASS + status chat configured -> post_status_message
PASS + no status chat configured -> record_pass_locally_no_upload
FAIL/BLOCKED -> upload_operator_report
```

## Allowed browser lanes

```text
chrome
edge
```

No generic browser lane is introduced.

## Acceptance labels

```text
PASS_STATUS_DELIVERY_CONSISTENCY_HARDENED
BLOCKED_STATUS_DELIVERY_SCHEMA_INVALID
BLOCKED_STATUS_DELIVERY_HASH_MISMATCH
BLOCKED_STATUS_DELIVERY_IDEMPOTENCY_CONFLICT
BLOCKED_STATUS_DELIVERY_UNBOUNDED_RETRY
BLOCKED_STATUS_DELIVERY_UNBOUNDED_TIMEOUT
BLOCKED_STATUS_DELIVERY_UNSAFE_FLAGS
```

## Outputs

```text
data/runtime/copilot_handoff/latest_status_delivery_consistency.json
data/runtime/copilot_handoff/latest_status_delivery_consistency.txt
data/runtime/copilot_handoff/status_delivery_consistency_ledger.jsonl
```

## CLI examples

Validate the latest router policy:

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_status_delivery_consistency_doctor.py
```

Validate a PASS status route:

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_status_delivery_consistency_doctor.py `
  --patch-name demo_patch `
  --patch-result PASS `
  --selected-action post_status_message `
  --browser-lane chrome `
  --status-chat-configured `
  --pass-status-message "demo_patch has passed"
```

Validate a FAIL report route:

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_status_delivery_consistency_doctor.py `
  --patch-name demo_patch `
  --patch-result FAIL `
  --selected-action upload_operator_report `
  --browser-lane edge `
  --operator-report-path C:\path\to\operator_report.txt
```

## Safety boundary

C36 is a no-browser final doctor. It does not focus, type, paste, upload, send, inspect DOM, use Selenium/WebDriver, bypass CAPTCHA/Cloudflare, log raw conversation text, random-click, or run unbounded loops.