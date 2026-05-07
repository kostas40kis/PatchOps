# U3 C28 uploader status target config named lanes

Patch `u3_c28_uploader_status_target_config_named_lanes` adds the status-target config validator for explicit browser lanes.

## Purpose

The config shape is:

```json
{
  "status_chat": {
    "browser_lane": "chrome",
    "target_url": "https://chatgpt.com/c/...",
    "target_url_sha256": "<hash>",
    "enabled": true
  }
}
```

## Allowed browser lanes

```text
chrome
edge
```

## Rejected browser lanes

```text
any
auto
all
default
firefox
brave
opera
vivaldi
chromium
```

## Boundaries

This patch performs config validation only.

It does not open Chrome or Edge, type, paste, upload, send, inspect the DOM, use Selenium/WebDriver, read raw conversation text, or attempt CAPTCHA/Cloudflare bypass.

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_uploader_status_target_config_validation.json
data/runtime/copilot_handoff/latest_uploader_status_target_config_validation.txt
```

Evidence includes only redacted target display and URL hashes. It does not log raw conversation text.

## Acceptance labels

```text
PASS_UPLOADER_STATUS_TARGET_CONFIG_VALIDATED
BLOCKED_STATUS_TARGET_CONFIG_MISSING
BLOCKED_STATUS_TARGET_BROWSER_UNSUPPORTED
BLOCKED_STATUS_TARGET_URL_INVALID
```

## CLI

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_status_target_config_doctor.py `
  --config-path data/config/uploader_status_target_config.json
```

To write an example config:

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_status_target_config_doctor.py `
  --write-example-config `
  --no-write-evidence
```