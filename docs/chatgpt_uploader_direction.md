# ChatGPT uploader direction

## Purpose

This document locks the new uploader direction after the normal Edge upload-picker ladder showed too much fragility.

The uploader is responsible for delivering PatchOps report evidence into a target ChatGPT conversation. PatchOps remains the source of truth. The browser is only a delivery bridge.

## Current decision

Use a new package:

```text
patchops/chatgpt_uploader
```

Do not keep widening the old picker-repair ladder as the primary uploader path.

## Mode order

```text
Mode A: file-input / file-chooser upload probe
Mode B: content pasteback fallback
Mode C: compact PATCHOPS_LLM_PASTEBACK summary
```

## Safety defaults

The foundation and doctor layers must not:

```text
open a browser
upload a file
send a ChatGPT message
use WebDriver
attempt Cloudflare or CAPTCHA bypass
log conversation text
perform random page clicks
```

Every future live phase must carry explicit safety flags and must remain unsent by default.

## Why this is separate from edge_rpa

The existing `patchops/edge_rpa` ladder contains useful evidence and UIA diagnostics, but uploader reliability should now be proven through a small dedicated package with testable local primitives first.

The new package starts with:

```text
models
target URL parsing
dependency doctor
safe report staging
safety policy
```

Live target readiness, file-input discovery, tiny upload probe, full report upload, and quota/content fallback should come later as separate narrow patches.
