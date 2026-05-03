# LLM Browser L1.1 Live Adapter Skeleton Contract

This document starts the L-phase after the D0 dry-mode closeout.

L1.1 creates a passive live-adapter skeleton contract only. It does not start a browser and it does not require Selenium.

## Purpose

The live-adapter skeleton gives future L-phase patches a stable Python interface for browser work without introducing browser side effects.

The skeleton is deliberately blocked:

- no browser startup;
- no live page read;
- no latest assistant reply detection;
- no download click;
- no PatchOps package execution;
- no composer paste;
- no send/submit.

## Source file

```text
patchops/llm_browser/live_adapter.py
```

## Public objects

The L1.1 skeleton exports:

```text
LiveAdapterPolicy
LiveAdapterResult
LiveAdapterSkeleton
LiveAdapterStatus
create_live_adapter_skeleton
```

## Safety policy

`LiveAdapterPolicy` defaults every live side-effect flag to false:

```text
enable_live_browser = false
allow_download_click = false
allow_patchops_execution = false
allow_composer_paste = false
allow_send_submit = false
```

Even if a caller constructs a permissive policy manually, L1.1 still refuses side-effecting operations because no L2-L9 gates exist yet.

## Required blocked operations

The skeleton must block these operations:

```text
start_browser
read_page
detect_latest_assistant_reply
click_download
run_patchops_package
paste_to_composer
send_or_submit
```

Each blocked operation must return a result with:

```text
ok = false
side_effects_performed = []
```

`send_or_submit` must remain unsupported.

## Capability contract

`describe_capabilities()` must report:

```text
stream = L1
phase = L1.1
selenium_required = false
browser_starts = false
side_effects_supported = false
```

## No optional dependency import

The L1.1 module must be importable without Selenium, browser drivers, or browser optional dependencies installed.

No import of Selenium is allowed in `patchops/llm_browser/live_adapter.py`.

## D-to-L boundary

D0 is the dry-mode validation/reporting/docs stream.

L1 starts the future live-adapter stream, but L1.1 is still no-side-effect skeleton work.

L1.1 must not silently expand D0 into live browser automation.

## Next patch

The next patch should be:

```text
L1.2 Live adapter skeleton CLI/readback
```

L1.2 may expose a passive CLI/readback command for the skeleton, but it must still not start a browser.

<!-- PATCHOPS_L1_02_LIVE_ADAPTER_CLI_READBACK_START -->

## L1.2 CLI/readback extension

L1.2 extends the no-side-effect skeleton with passive readback only.

The supported smoke command is:

```powershell
py -m patchops.cli llm-browser live-adapter --json
```

The JSON payload is a capability contract. It proves the adapter can describe itself without optional browser dependencies and without creating a browser session. All live operations remain blocked and raise `LiveAdapterBlockedError` if called directly.

Next patch: **L1.3 Live adapter passive contract gate**.

<!-- PATCHOPS_L1_02_LIVE_ADAPTER_CLI_READBACK_END -->
