# PatchOps LLM Browser Runner

<!-- PATCHOPS_D0_01_OPTIONAL_BROWSER_DEPS:START -->
## D0.1 optional browser dependency foundation

Current implementation status: **D0.1 foundation only**.

This page tracks the additive Selenium LLM browser runner stream. The runner is an optional operator helper for reducing repetitive browser/download/report/pasteback work. It does not change PatchOps' wrapper boundary and does not move target-project business logic into PatchOps.

D0.1 intentionally ships only the dependency and import-safety foundation:

- `pyproject.toml` declares the optional `browser` extra.
- `patchops.llm_browser` can be imported without Selenium installed.
- Browser-specific modules must continue to import Selenium lazily in later patches.
- Core PatchOps commands must remain usable without installing browser automation dependencies.

Install the optional browser dependencies only when working on this stream:

```powershell
Set-Location C:\dev\patchops
.\.venv\Scripts\python.exe -m pip install -e ".[browser]"
```

Direct fallback:

```powershell
Set-Location C:\dev\patchops
.\.venv\Scripts\python.exe -m pip install -U selenium webdriver-manager psutil pyperclip
```

Safety boundaries for this stream:

- no browser extension in this stream,
- no PatchOps localhost server,
- no hidden background web service,
- no silent auto-submit by default,
- no provider-limit bypass,
- no credential, cookie, or token extraction,
- PatchOps canonical reports remain the source of truth.
<!-- PATCHOPS_D0_01_OPTIONAL_BROWSER_DEPS:END -->

<!-- PATCHOPS_D0_02_DEPENDENCY_DOCTOR:START -->
## D0.2 dependency doctor

Current implementation status: **D0.2 dependency doctor repaired by D0.2e**.

The `llm-browser doctor` command is now the first CLI surface for this stream:

```powershell
py -m patchops.cli llm-browser doctor --browser edge --wrapper-root C:\dev\patchops
```

The doctor is intentionally passive. It checks Python, optional imports, browser executable discovery, Downloads, wrapper root, and optional target root.

The doctor must not open Edge or Opera, start Selenium, start a WebDriver process, create a localhost server, store credentials, or auto-submit browser content.

D0.2e repair note:
- tests use injected import probes or call-time monkeypatching, so they do not require Selenium to already be installed;
- `cli.py` is re-patched idempotently so duplicate `llm-browser` wrappers are not stacked;
- docs marker replacement is string-index based, not regex-replacement based, so Windows paths like `C:\dev\patchops` cannot trigger `bad escape \d`.
<!-- PATCHOPS_D0_02_DEPENDENCY_DOCTOR:END -->

<!-- PATCHOPS_D0_03_BROWSER_PATH_DISCOVERY:START -->
## D0.3 browser path discovery

Current implementation status: **D0.3 browser path discovery shipped**.

The browser-runner stream now has a pure-Python browser path discovery module:

```text
patchops/llm_browser/browser_paths.py
```

It can discover Edge and Opera executable candidates without importing Selenium, starting a browser driver, opening a browser window, or creating a network service.

Supported path sources:

- explicit function argument override,
- `PATCHOPS_EDGE_PATH` / `MSEDGE_PATH`,
- `PATCHOPS_OPERA_PATH` / `OPERA_PATH`,
- standard Microsoft Edge install locations,
- Opera and Opera GX locations under `%LOCALAPPDATA%`,
- standard Opera and Opera GX Program Files locations.

The dependency doctor now reuses this module for Edge and Opera discovery instead of owning browser path logic directly.
<!-- PATCHOPS_D0_03_BROWSER_PATH_DISCOVERY:END -->

<!-- PATCHOPS_D0_04_BROWSER_PROFILE_MANAGER:START -->
## D0.4 browser profile manager

Current implementation status: **D0.4 browser profile manager shipped**.

The browser-runner stream now has a pure-Python profile manager:

```text
patchops/llm_browser/browser_profiles.py
```

It creates dedicated automation profile directories without importing Selenium, starting a browser driver, opening a browser window, or creating a network service.

Default profile root:

```text
%LOCALAPPDATA%\PatchOps\llm_browser_profiles\
```

Default profile directories:

```text
edge_chatgpt_default
opera_chatgpt_default
```

Safety behavior:

- the runner does not use the operator's normal browser profile by default;
- profile names must be a single safe path segment;
- parent traversal is rejected;
- explicit profile directory overrides are allowed only when they are safe;
- obvious normal/default Edge and Opera profile paths are rejected;
- directory creation is explicit and test-covered.
<!-- PATCHOPS_D0_04_BROWSER_PROFILE_MANAGER:END -->

<!-- PATCHOPS_D0_05_BROWSER_CONFIG_MODEL:START -->
## D0.5 browser config model

Current implementation status: **D0.5 browser config model shipped**.

The browser-runner stream now has a stable config layer:

```text
patchops/llm_browser/models.py
patchops/llm_browser/config.py
```

The main config object is `BrowserRunConfig` with these fields:

```text
browser
wrapper_root
target_root
download_dir
profile_dir
chat_url
auto_download
auto_paste
auto_send
poll_seconds
stability_seconds
run_package_timeout_seconds
```

Safety defaults:

```text
auto_send = False
poll_seconds = 5
stability_seconds = 15
run_package_timeout_seconds = 1800
```

D0.5 deliberately rejects `auto_send=True`. A later reviewed patch can introduce an explicit unlock if needed, but this model prevents silent auto-submit behavior by default.

Validation behavior:

- browser must be `edge` or `opera`;
- wrapper root must exist;
- target root must exist if supplied;
- download directory must exist;
- profile directory must not point at an obvious normal/default browser profile;
- chat URL must be HTTP/HTTPS;
- timing values must be positive;
- config construction does not open a browser or start Selenium.
<!-- PATCHOPS_D0_05_BROWSER_CONFIG_MODEL:END -->

<!-- PATCHOPS_D0_06_SELENIUM_EDGE_FACTORY:START -->
## D0.6 Selenium browser factory for Edge

Current implementation status: **D0.6 Selenium Edge factory shipped**.

The browser-runner stream now has the first Selenium factory/controller layer:

```text
patchops/llm_browser/browser_factory.py
patchops/llm_browser/edge_controller.py
```

D0.6 adds:

```text
py -m patchops.cli llm-browser open --browser edge --wrapper-root C:\dev\patchops --download-dir C:\Users\kostas\Downloads
```

Factory behavior:

- Selenium imports are lazy;
- `browser_factory.py` can be imported without importing Selenium;
- Edge options use the dedicated PatchOps profile directory;
- Edge options set `download.default_directory`;
- Edge options disable notifications;
- `edge_controller.open_edge()` opens the configured chat URL only when called.

Safety behavior:

- validation tests use fake Selenium classes, so patch validation does not open a browser;
- there is still no artifact detection;
- no PatchOps command is run by the browser code;
- no auto-send flag is exposed on the open command;
- no localhost service is created.
<!-- PATCHOPS_D0_06_SELENIUM_EDGE_FACTORY:END -->

<!-- PATCHOPS_D0_07_SELENIUM_OPERA_FACTORY:START -->
## D0.7 Selenium browser factory for Opera

Current implementation status: **D0.7 Selenium Opera factory shipped**.

The browser-runner stream now has an Opera factory/controller layer:

```text
patchops/llm_browser/browser_factory.py
patchops/llm_browser/opera_controller.py
```

D0.7 extends the open command:

```text
py -m patchops.cli llm-browser open --browser opera --wrapper-root C:\dev\patchops --download-dir C:\Users\kostas\Downloads
```

Factory behavior:

- Selenium imports are lazy;
- Opera support uses Selenium's Chromium/Chrome options with Opera's binary location;
- Opera options use the dedicated PatchOps profile directory;
- Opera options set `download.default_directory`;
- Opera options disable notifications;
- `opera_controller.open_opera()` opens the configured chat URL only when called.

Safety behavior:

- validation tests use fake Selenium classes, so patch validation does not open a browser;
- there is still no artifact detection;
- no PatchOps command is run by the browser code;
- no auto-send flag is exposed on the open command;
- no localhost service is created.
<!-- PATCHOPS_D0_07_SELENIUM_OPERA_FACTORY:END -->

<!-- PATCHOPS_D0_08_BROWSER_SESSION_LIFECYCLE:START -->
## D0.8 browser session lifecycle smoke tests

Current implementation status: **D0.8 browser session lifecycle shipped**.

The browser-runner stream now has a session lifecycle helper:

```text
patchops/llm_browser/session.py
```

Lifecycle behavior:

- constructing `BrowserSession` does not start a browser;
- `start()` creates exactly one driver;
- `start()` can optionally navigate to the configured ChatGPT URL;
- `navigate(url)` requires an already-started, open session;
- `close()` is idempotent;
- shutdown prefers `driver.quit()` and falls back to `driver.close()`;
- context-manager usage closes the session even when an exception occurs.

Safety behavior:

- tests use fake drivers, so patch validation does not open Edge or Opera;
- there is still no artifact detection;
- no PatchOps command is run by browser session code;
- no auto-send behavior exists;
- no localhost service is created.
<!-- PATCHOPS_D0_08_BROWSER_SESSION_LIFECYCLE:END -->

<!-- PATCHOPS_D0_09_CHATGPT_PAGE_READINESS:START -->
## D0.9 ChatGPT page readiness detector

Current implementation status: **D0.9 ChatGPT page readiness detector shipped**.

The browser-runner stream now has passive, fixture-first page readiness helpers:

```text
patchops/llm_browser/chat_page_contract.py
patchops/llm_browser/reply_stability.py
tests/fixtures/llm_browser/chatgpt_reply_with_zip.html
tests/fixtures/llm_browser/chatgpt_reply_without_zip.html
tests/fixtures/llm_browser/chatgpt_reply_streaming.html
tests/test_llm_browser_page_readiness_current.py
```

The contract extracts only compact metadata:

```text
latest assistant reply text/hash
assistant message count
streaming indicator
composer enabled state
downloadable .zip candidates from the latest assistant reply
```

Safety behavior:

- fixture tests do not touch real ChatGPT;
- no Selenium driver starts during validation;
- older assistant messages are ignored for artifact candidates;
- full message text is not emitted in payloads;
- readiness is blocked while streaming;
- readiness is blocked when the composer is disabled;
- reply stability requires the latest assistant hash to remain unchanged for the configured stability window.
<!-- PATCHOPS_D0_09_CHATGPT_PAGE_READINESS:END -->

<!-- PATCHOPS_D0_09B_ARTIFACT_DEDUPE_REPAIR:START -->
## D0.9b artifact candidate dedupe repair

Current implementation status: **D0.9 repaired by D0.9b**.

D0.9b fixes artifact candidate extraction when a `.zip` appears both as a real download link `href` and as visible anchor text.

Repair behavior:

- candidates are deduplicated by case-insensitive filename;
- href-backed candidates are preferred over text-only candidates;
- distinct `.zip` filenames are still preserved;
- the parser still only scans the latest assistant message;
- full message text is still not emitted in payloads.

This repairs the D0.9 focused-test failure where one visible download link produced two identical candidates.
<!-- PATCHOPS_D0_09B_ARTIFACT_DEDUPE_REPAIR:END -->

<!-- PATCHOPS_D0_10_DOWNLOADABLE_ARTIFACT_DETECTOR:START -->
## D0.10 downloadable artifact detector

Current implementation status: **D0.10 downloadable artifact detector shipped**.

The browser-runner stream now has a passive PatchOps artifact detector:

```text
patchops/llm_browser/artifact_detector.py
tests/test_llm_browser_artifact_detector_current.py
```

Detection behavior:

- consumes `ChatPageSnapshot` from `chat_page_contract.py`;
- only considers candidates from the latest assistant reply;
- accepts filenames matching `patch_*_patchops_bundle.zip`;
- ignores non-PatchOps `.zip` files;
- ignores already processed artifacts by filename or href key;
- preserves href-backed candidates when available;
- blocks detection while the reply is streaming;
- blocks detection when the composer is disabled;
- emits compact metadata only.

Safety behavior:

- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens in D0.10;
- no PatchOps command is run by detector code;
- no auto-send behavior exists;
- no localhost service is created.
<!-- PATCHOPS_D0_10_DOWNLOADABLE_ARTIFACT_DETECTOR:END -->

<!-- PATCHOPS_D0_11_DOWNLOAD_MANAGER:START -->
## D0.11 download manager

Current implementation status: **D0.11 download manager shipped**.

The browser-runner stream now has passive download-file management:

```text
patchops/llm_browser/download_manager.py
tests/test_llm_browser_download_manager_current.py
```

Download manager behavior:

- validates expected artifact filenames with the `patch_*_patchops_bundle.zip` contract;
- computes the expected local path inside the configured download directory;
- detects browser partial-download files such as `.crdownload`, `.part`, and `.tmp`;
- waits for a file to exist and be old enough to count as stable;
- can prepare a downloaded bundle by copying it to a runtime/prepared directory;
- emits compact state payloads for reporting.

Safety behavior:

- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens in D0.11;
- no PatchOps command is run by download-manager code;
- no auto-send behavior exists;
- no localhost service is created.
<!-- PATCHOPS_D0_11_DOWNLOAD_MANAGER:END -->

<!-- PATCHOPS_D0_12_BROWSER_CLICK_TO_DOWNLOAD_BRIDGE:START -->
## D0.12 browser click-to-download bridge

Current implementation status: **D0.12 browser click-to-download bridge shipped**.

The browser-runner stream now has a narrow bridge from detected artifact metadata to local download waiting:

```text
patchops/llm_browser/download_bridge.py
tests/test_llm_browser_download_bridge_current.py
```

Bridge behavior:

- finds a browser element that matches the detected `ArtifactCandidate`;
- matches by href, visible text, `download` attribute, or download aria label;
- clicks the matched element only when explicitly called;
- waits for the expected local `patch_*_patchops_bundle.zip` file to finish via `download_manager.py`;
- can prepare the completed file by copying it to a runtime/prepared directory;
- returns compact result payloads.

Safety behavior:

- validation uses fake driver and fake element objects only;
- no real browser starts during validation;
- no Selenium dependency is required for tests;
- no PatchOps command is run by bridge code;
- no auto-send behavior exists;
- no localhost service is created.
<!-- PATCHOPS_D0_12_BROWSER_CLICK_TO_DOWNLOAD_BRIDGE:END -->
