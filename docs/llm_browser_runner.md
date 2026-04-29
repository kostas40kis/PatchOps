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

<!-- PATCHOPS_D0_13_PROCESSED_ARTIFACT_STORE:START -->
## D0.13 processed artifact store

Current implementation status: **D0.13 processed artifact store shipped**.

The browser-runner stream now has a passive duplicate-run prevention store:

```text
patchops/llm_browser/processed_store.py
tests/test_llm_browser_processed_store_current.py
```

Store behavior:

- records processed artifacts by SHA-256;
- records filename, href, local path, result, processed timestamp, report path, and compact notes;
- exposes processed lookup keys for integration with artifact detection;
- skips the same file hash;
- treats the same filename with a different hash as new, while surfacing a warning;
- handles corrupt JSON by backing up the corrupt file and repairing to an empty store;
- uses `LOCALAPPDATA\PatchOps\llm_browser\processed_artifacts.json` by default;
- supports explicit store path and store directory environment overrides.

Safety behavior:

- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by processed-store code;
- no auto-send behavior exists;
- no localhost service is created.
<!-- PATCHOPS_D0_13_PROCESSED_ARTIFACT_STORE:END -->

<!-- PATCHOPS_D0_14_RUN_LOCK:START -->
## D0.14 run lock

Current implementation status: **D0.14 run lock shipped**.

The browser-runner stream now has a passive filesystem run lock:

```text
patchops/llm_browser/run_lock.py
tests/test_llm_browser_run_lock_current.py
```

Run-lock behavior:

- prevents overlapping browser-runner driven PatchOps executions;
- writes a small JSON lock file;
- records PID, owner, acquired timestamp, heartbeat timestamp, and compact metadata;
- second runner exits cleanly when the lock is live;
- stale lock recovery is supported when the recorded PID is gone;
- stale lock recovery is supported when heartbeat age exceeds the configured threshold;
- corrupt lock JSON can be backed up and recovered;
- heartbeat updates only the current owner PID;
- release refuses to remove another process's lock.

Default lock path:

```text
%LOCALAPPDATA%\PatchOps\llm_browser\run.lock
```

Safety behavior:

- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by run-lock code;
- no auto-send behavior exists;
- no localhost service is created.
<!-- PATCHOPS_D0_14_RUN_LOCK:END -->

<!-- PATCHOPS_D0_15_PATCHOPS_SUBPROCESS_RUNNER:START -->
## D0.15 PatchOps subprocess runner

Current implementation status: **D0.15 PatchOps subprocess runner shipped**.

The browser-runner stream now has a narrow PatchOps CLI subprocess wrapper:

```text
patchops/llm_browser/patchops_runner.py
tests/test_llm_browser_patchops_runner_current.py
```

Runner behavior:

- builds the command:

```text
py -3 -m patchops.cli run-package <artifact.zip> --wrapper-root <wrapper-root>
```

or uses the wrapper virtualenv Python when available;

- validates artifact and wrapper-root paths before execution;
- supports explicit timeout configuration;
- captures stdout/stderr;
- extracts outer/inner report paths from JSON or stdout text;
- parses JSON run-package payloads when present;
- treats nonzero exit codes as failure;
- treats `ok:false` as failure even if native exit code is zero;
- treats `inner_result:FAIL` as failure even if native exit code is zero;
- exposes compact result payloads.

Safety behavior:

- D0.15 validation uses fake process runners;
- no real PatchOps bundle is executed during tests;
- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no auto-send behavior exists;
- no localhost service is created.
<!-- PATCHOPS_D0_15_PATCHOPS_SUBPROCESS_RUNNER:END -->

<!-- PATCHOPS_D0_16_ORCHESTRATION_STATE_MODEL:START -->
## D0.16 orchestration state model

Current implementation status: **D0.16 orchestration state model shipped**.

The browser-runner stream now has a passive state-machine model:

```text
patchops/llm_browser/orchestration_state.py
tests/test_llm_browser_orchestration_state_current.py
```

State model:

```text
IDLE
WAITING_FOR_REPLY_STABLE
LOOKING_FOR_ARTIFACT
DOWNLOADING
RUNNING_PATCHOPS
SUMMARY_READY
WAITING_FOR_USER_NEXT_REPLY
```

Blocked states:

```text
BLOCKED_ARTIFACT_MISSING
BLOCKED_DOWNLOAD_FAILED
BLOCKED_BAD_ZIP
BLOCKED_PATCHOPS_RUN_FAILED
BLOCKED_REPORT_MISSING
BLOCKED_SELECTOR_DRIFT
BLOCKED_DRIVER_FAILURE
BLOCKED_RUN_LOCK_HELD
BLOCKED_REPEATED_FAILURES
```

Behavior:

- legal transitions are explicit;
- illegal transitions fail closed;
- blocked states are terminal;
- repeated failure counts can stop the loop;
- compact state snapshots preserve artifact filename, sha256, downloaded path, canonical report path, browser, failure count, last error, and transition history;
- PatchOps result status maps to `SUMMARY_READY`, `BLOCKED_REPORT_MISSING`, or `BLOCKED_PATCHOPS_RUN_FAILED`.

Safety behavior:

- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by orchestration-state code;
- no auto-send behavior exists;
- no localhost service is created.
<!-- PATCHOPS_D0_16_ORCHESTRATION_STATE_MODEL:END -->

<!-- PATCHOPS_D0_17_CANONICAL_REPORT_LOCATOR:START -->
## D0.17 canonical report locator

Current implementation status: **D0.17 canonical report locator shipped**.

The browser-runner stream now has a passive canonical report locator:

```text
patchops/llm_browser/report_locator.py
tests/test_llm_browser_report_locator_current.py
```

Locator behavior:

- consumes `PatchOpsRunResult` from `patchops_runner.py`;
- prefers explicit `outer_report_path` / `inner_report_path` payload fields;
- falls back to report paths discovered in stdout/stderr;
- falls back to newest report file from configured search roots;
- parses compact report summary fields:
  - result;
  - exit code;
  - patch name;
  - failure category;
  - pass/fail status;
  - text length only, not full report text;
- reports missing explicit paths fail-closed.

Safety behavior:

- validation uses temp report files only;
- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by report-locator code;
- no auto-send behavior exists;
- no localhost service is created.
<!-- PATCHOPS_D0_17_CANONICAL_REPORT_LOCATOR:END -->

<!-- PATCHOPS_D0_17B_REPORT_LOCATOR_PATCH_FIELD_REPAIR:START -->
## D0.17b report locator patch-field repair

Current implementation status: **D0.17 repaired by D0.17b**.

D0.17b fixes canonical report parsing so the parser does not treat the heading:

```text
PATCHOPS RUN-PACKAGE OUTER REPORT
```

as a `Patch:` field.

Repair behavior:

- the patch-name parser now requires a real colon-delimited `Patch : ...` field;
- `PATCHOPS ...` headings are ignored;
- reports without a `Patch : ...` line return `patch = None`;
- all report-location behavior remains passive and filesystem-only.

This repairs the D0.17 focused-test failure where `summary.patch` was parsed as `OPS RUN-PACKAGE OUTER REPORT` instead of the real patch line.
<!-- PATCHOPS_D0_17B_REPORT_LOCATOR_PATCH_FIELD_REPAIR:END -->

<!-- PATCHOPS_D0_18_PASTEBACK_SUMMARY_FORMATTER:START -->
## D0.18 pasteback summary formatter

Current implementation status: **D0.18 pasteback summary formatter shipped**.

The browser-runner stream now has a passive pasteback summary formatter:

```text
patchops/llm_browser/pasteback_summary.py
tests/test_llm_browser_pasteback_summary_current.py
```

Formatter behavior:

- consumes compact metadata from:
  - `CanonicalReportLocation`;
  - `PatchOpsRunResult`;
  - `OrchestrationSnapshot`;
- formats bounded PASS/FAIL/UNKNOWN summaries;
- includes patch name, report path, result, exit code, failure category, runner reason, orchestration state, artifact filename, sha256, last error, and failure count when available;
- clamps long lines;
- limits notes;
- chooses fail-closed next actions for timeout, missing report, failed runner output, and repeated failures;
- emits payload metadata without full report text.

Safety behavior:

- formatting does not paste or send anything;
- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by pasteback-summary code;
- no auto-send behavior exists;
- no localhost service is created.
<!-- PATCHOPS_D0_18_PASTEBACK_SUMMARY_FORMATTER:END -->

<!-- PATCHOPS_D0_19_COMPOSER_PASTE_HELPER:START -->
## D0.19 composer paste helper

Current implementation status: **D0.19 composer paste helper shipped**.

The browser-runner stream now has a narrow composer paste helper:

```text
patchops/llm_browser/composer_paste.py
tests/test_llm_browser_composer_paste_current.py
```

Composer helper behavior:

- finds a ChatGPT-like composer using CSS selector candidates;
- supports textarea and contenteditable composer shapes;
- ignores disabled composers;
- clicks/focuses the composer before setting text;
- prefers JavaScript text insertion when available;
- falls back to `clear()` + `send_keys()`;
- supports pasting a `PastebackSummary`-like object through its `.text` field;
- returns compact payload metadata;
- explicitly does **not** submit/send the message.

Safety behavior:

- validation uses fake drivers and fake elements only;
- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by composer-paste code;
- no auto-send behavior exists;
- no localhost service is created.
<!-- PATCHOPS_D0_19_COMPOSER_PASTE_HELPER:END -->

<!-- PATCHOPS_D0_20_END_TO_END_DRY_RUN_ORCHESTRATOR:START -->
## D0.20 end-to-end dry-run orchestrator

Current implementation status: **D0.20 end-to-end dry-run orchestrator shipped**.

The browser-runner stream now has a passive dry-run orchestrator:

```text
patchops/llm_browser/dry_run_orchestrator.py
tests/test_llm_browser_dry_run_orchestrator_current.py
```

Dry-run behavior:

- wires together page readiness, artifact detection, orchestration state, PatchOps runner results, canonical report location, and pasteback summary formatting;
- proves the end-to-end loop shape without performing side effects;
- stops at the appropriate state when later-stage facts are not supplied;
- blocks on missing artifacts, already-processed artifacts, failed runner results, missing reports, and failed canonical reports;
- reaches `SUMMARY_READY` only when a detected artifact, downloaded path, ok runner result, and PASS canonical report are supplied;
- returns planned actions such as:
  - `would_acquire_run_lock`;
  - `would_click_download_candidate_and_wait_for_stable_file`;
  - `would_run_patchops_run_package`;
  - `would_locate_canonical_report`;
  - `would_paste_summary_without_submit`;
- records that no side effects were performed.

Safety behavior:

- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by dry-run orchestrator code;
- no composer paste happens here;
- no message is submitted/sent;
- no localhost service is created.
<!-- PATCHOPS_D0_20_END_TO_END_DRY_RUN_ORCHESTRATOR:END -->

<!-- PATCHOPS_D0_20B_DRY_RUN_MISSING_REPORT_STATUS_REPAIR:START -->
## D0.20b dry-run missing-report status repair

Current implementation status: **D0.20 repaired by D0.20b**.

D0.20b fixes pasteback summary status precedence for the dry-run orchestrator.

Repair behavior:

- blocked orchestration states now override a successful lower-level runner result;
- `BLOCKED_REPORT_MISSING` formats as `FAIL`, even when `PatchOpsRunResult.ok` is true;
- `BLOCKED_REPORT_MISSING` chooses the fail-closed next action:
  `Stop and inspect why the canonical report was not found.`;
- no dry-run side effects are introduced.

This repairs the D0.20 focused-test failure where the dry-run entered `BLOCKED_REPORT_MISSING` but the pasteback summary still reported `PASS`.
<!-- PATCHOPS_D0_20B_DRY_RUN_MISSING_REPORT_STATUS_REPAIR:END -->

<!-- PATCHOPS_D0_21_DRY_RUN_CLI_COMMAND:START -->
## D0.21 dry-run CLI command

Current implementation status: **D0.21 dry-run CLI command shipped**.

The browser-runner stream now exposes a passive CLI surface:

```text
py -m patchops.cli llm-browser dry-run --snapshot-file <chat_snapshot.html> --json
```

Implemented files:

```text
patchops/llm_browser/commands.py
tests/test_llm_browser_dry_run_cli_current.py
```

Dry-run CLI behavior:

- accepts either `--snapshot-file` or `--snapshot-html`;
- accepts optional `--processed-artifact` keys;
- accepts optional supplied facts:
  - `--downloaded-path`;
  - `--runner-status pass|fail`;
  - `--runner-reason`;
  - `--runner-exit-code`;
  - `--report-path`;
- emits JSON with `--json`;
- emits a readable summary and planned actions without `--json`;
- supports `--strict` to return nonzero when the dry run blocks;
- returns planned actions instead of doing them;
- reaches `SUMMARY_READY` only when supplied facts prove the happy path;
- keeps missing canonical reports fail-closed.

Safety behavior:

- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by the dry-run CLI;
- no composer paste happens here;
- no message is submitted/sent;
- no localhost service is created;
- no `--auto-send` option exists.
<!-- PATCHOPS_D0_21_DRY_RUN_CLI_COMMAND:END -->

<!-- PATCHOPS_D0_22_BROWSER_RUNNER_INTEGRATION_SKELETON:START -->
## D0.22 browser runner integration skeleton

Current implementation status: **D0.22 browser runner integration skeleton shipped**.

The browser-runner stream now has an adapter-driven integration boundary:

```text
patchops/llm_browser/runner_integration.py
tests/test_llm_browser_runner_integration_current.py
```

Integration skeleton behavior:

- composes the passive dry-run orchestrator with explicit adapter slots:
  - snapshot provider;
  - download provider;
  - PatchOps provider;
  - report provider;
  - paste provider;
- has a `BrowserRunnerSafetyPolicy`;
- blocks `allow_send` unconditionally;
- blocks any side-effect adapter when `dry_run_only=True`;
- defaults to dry-run/skeleton mode;
- exposes planned actions and compact payloads;
- can exercise fake adapters in tests without Selenium or real PatchOps;
- records side effects only when explicit non-dry-run options and fake adapters are used.

Safety behavior:

- no browser starts during validation;
- no Selenium dependency is required;
- no real download click happens here;
- no real PatchOps command is run by integration tests;
- no real composer paste happens here;
- no message is submitted/sent;
- no localhost service is created;
- `allow_send` is rejected.
<!-- PATCHOPS_D0_22_BROWSER_RUNNER_INTEGRATION_SKELETON:END -->

<!-- PATCHOPS_D0_23_BROWSER_RUNNER_INTEGRATION_CLI_DRY_MODE:START -->
## D0.23 browser runner integration CLI dry mode

Current implementation status: **D0.23 browser runner integration CLI dry mode shipped**.

The browser-runner stream now exposes a CLI dry integration surface:

```text
py -m patchops.cli llm-browser run-once --dry-run --snapshot-file <chat_snapshot.html> --json
```

Implemented files:

```text
patchops/llm_browser/commands.py
tests/test_llm_browser_run_once_cli_dry_mode_current.py
```

Run-once dry-mode behavior:

- adds `llm-browser run-once`;
- D0.23 supports `run-once --dry-run` only;
- live `run-once` without `--dry-run` returns a clear nonzero diagnostic;
- accepts either `--snapshot-file` or `--snapshot-html`;
- accepts `--processed-artifact`;
- emits JSON with `--json`;
- emits readable summary and planned integration actions without `--json`;
- supports `--strict` to return nonzero when blocked;
- uses the D0.22 adapter-driven integration skeleton;
- returns planned actions instead of doing them;
- rejects dry-run side-effect flags through the safety policy;
- provides no `--auto-send` or `--allow-send` option.

Safety behavior:

- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by the run-once dry CLI;
- no composer paste happens here;
- no message is submitted/sent;
- no localhost service is created.
<!-- PATCHOPS_D0_23_BROWSER_RUNNER_INTEGRATION_CLI_DRY_MODE:END -->

<!-- PATCHOPS_D0_24_MINIMAL_AUDIT_LOG:START -->
## D0.24 minimal audit log

Current implementation status: **D0.24 minimal audit log shipped**.

The browser-runner stream now has a passive JSONL audit layer:

```text
patchops/llm_browser/audit_log.py
tests/test_llm_browser_audit_log_current.py
```

Audit behavior:

- appends compact JSONL events;
- supports default path resolution:
  - `PATCHOPS_LLM_BROWSER_AUDIT_LOG`;
  - `PATCHOPS_LLM_BROWSER_STORE_DIR\audit.jsonl`;
  - `%LOCALAPPDATA%\PatchOps\llm_browser\audit.jsonl`;
- records:
  - event type;
  - event id;
  - timestamp;
  - source;
  - status;
  - patch name;
  - artifact filename;
  - artifact sha256;
  - canonical report path;
  - orchestration state;
  - reason / next action;
  - compact sanitized metadata;
- can build events from pasteback summaries;
- can build events from browser-runner integration results;
- rotates the audit file when it exceeds the configured byte limit;
- reads back recent events while ignoring corrupt JSON lines.

Safety behavior:

- audit logging only writes local JSONL evidence;
- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by audit-log code;
- no composer paste happens here;
- no message is submitted/sent;
- no localhost service is created.
<!-- PATCHOPS_D0_24_MINIMAL_AUDIT_LOG:END -->

<!-- PATCHOPS_D0_24B_AUDIT_LOG_METADATA_JSON_REPAIR:START -->
## D0.24b audit-log metadata JSON repair

Current implementation status: **D0.24 repaired by D0.24b**.

D0.24b fixes audit metadata sanitization so JSON-native metadata remains structured.

Repair behavior:

- preserves lists used by `planned_actions`;
- preserves empty lists used by `side_effects_performed`;
- preserves nested dictionaries;
- converts tuples to JSON arrays;
- still stringifies unknown objects;
- still clamps long strings;
- keeps audit events compact and JSONL-safe.

This repairs the D0.24 focused-test failure where `planned_actions` was stringified instead of remaining a JSON array.
<!-- PATCHOPS_D0_24B_AUDIT_LOG_METADATA_JSON_REPAIR:END -->

<!-- PATCHOPS_D0_24C_AUDIT_LOG_TEST_CONTRACT_ALIGNMENT:START -->
## D0.24c audit-log test contract alignment

Current implementation status: **D0.24 repaired by D0.24c**.

D0.24c aligns the audit-log tests and implementation around one contract:

- audit metadata preserves JSON-native arrays and dictionaries;
- `planned_actions` remains a JSON array;
- `side_effects_performed` remains a JSON array;
- tuples are converted to JSON arrays;
- unknown objects are stringified;
- long string leaves are clamped wherever they appear;
- existing audit-log tests now assert the structured metadata contract instead of the old stringified-list behavior.

This repairs the D0.24b failure where the old D0.24 test still expected `"list": "[1, 2]"`, and the new regression test expected unclamped list strings despite the configured clamp limit.
<!-- PATCHOPS_D0_24C_AUDIT_LOG_TEST_CONTRACT_ALIGNMENT:END -->

<!-- PATCHOPS_D0_25_WIRE_AUDIT_LOG_INTO_CLI:START -->
## D0.25 wire audit log into dry-run/run-once CLI

Current implementation status: **D0.25 audit-log CLI wiring shipped**.

The browser-runner stream now wires the passive audit log into the passive CLI surfaces:

```text
patchops/llm_browser/audit_log.py
patchops/llm_browser/commands.py
tests/test_llm_browser_audit_log_dry_run_event_current.py
tests/test_llm_browser_cli_audit_log_current.py
```

CLI behavior:

- `llm-browser dry-run` accepts:
  - `--audit-log <path>`;
  - `--audit-source <name>`;
- `llm-browser run-once --dry-run` accepts:
  - `--audit-log <path>`;
  - `--audit-source <name>`;
- each invocation appends exactly one compact JSONL event when `--audit-log` is provided;
- `dry-run` writes `event_type = dry_run_result`;
- `run-once --dry-run` writes `event_type = integration_result`;
- audit events include:
  - status;
  - patch/artifact filename;
  - state;
  - report path when available;
  - reason / next action;
  - planned actions as JSON arrays;
  - side effects performed as JSON arrays;
- text output prints the audit-log path when audit logging is enabled;
- live `run-once` rejection does not write an audit event.

Safety behavior:

- audit logging is opt-in through `--audit-log`;
- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by audit-log CLI wiring;
- no composer paste happens here;
- no message is submitted/sent;
- no localhost service is created;
- no `--auto-send` / `--allow-send` option exists.
<!-- PATCHOPS_D0_25_WIRE_AUDIT_LOG_INTO_CLI:END -->

<!-- PATCHOPS_D0_26_AUDIT_LOG_READBACK_CLI:START -->
## D0.26 audit-log readback CLI

Current implementation status: **D0.26 audit-log readback CLI shipped**.

The browser-runner stream now has a read-only audit viewer:

```text
py -m patchops.cli llm-browser audit-log --path <audit.jsonl> --json
py -m patchops.cli llm-browser audit-log --path <audit.jsonl> --limit 5
```

Implemented files:

```text
patchops/llm_browser/commands.py
tests/test_llm_browser_audit_log_readback_cli_current.py
```

Audit-log readback behavior:

- reads compact JSONL audit events through `AuditLog.read_events`;
- supports `--path`;
- supports `--limit`, with `0` meaning all events;
- supports `--event-type`;
- supports `--status`;
- emits JSON with `--json`;
- emits compact text without `--json`;
- missing audit files are treated as an empty audit log;
- corrupt JSONL lines remain ignored by the underlying audit reader;
- shows planned actions and side effects as JSON-array metadata;
- performs no mutation, cleanup, or deletion.

Safety behavior:

- readback is read-only;
- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by audit-log readback;
- no composer paste happens here;
- no message is submitted/sent;
- no localhost service is created;
- no `--auto-send`, `--delete`, or `--clear` option exists.
<!-- PATCHOPS_D0_26_AUDIT_LOG_READBACK_CLI:END -->

<!-- PATCHOPS_D0_27_AUDIT_LOG_DOCS_OPERATOR_EXAMPLES:START -->
## D0.27 audit-log docs and operator examples

Current implementation status: **D0.27 audit-log docs and operator examples shipped**.

The browser-runner stream now has operator-facing audit-log documentation:

```text
docs/llm_browser_audit_log_operator_examples.md
tests/test_llm_browser_audit_log_docs_current.py
```

Documentation coverage:

- audit-log safety contract;
- explicit statement that audit logging is passive and append-only;
- default audit path resolution order;
- `llm-browser dry-run --audit-log` example;
- `llm-browser run-once --dry-run --audit-log` example;
- `llm-browser audit-log --path --limit --json` readback example;
- event-type filtering examples;
- status filtering examples;
- missing/corrupt log behavior;
- interpretation guide for:
  - `BLOCKED_ARTIFACT_MISSING`;
  - `DOWNLOADING`;
  - `RUNNING_PATCHOPS`;
  - `BLOCKED_REPORT_MISSING`;
  - `SUMMARY_READY`;
- recommended operator loop;
- troubleshooting examples.

Safety behavior:

- docs describe dry-mode examples only;
- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by this docs patch;
- no composer paste happens here;
- no message is submitted/sent;
- no localhost service is created;
- no `--auto-send`, `--delete`, or `--clear` option is documented.
<!-- PATCHOPS_D0_27_AUDIT_LOG_DOCS_OPERATOR_EXAMPLES:END -->

<!-- PATCHOPS_D0_28_BROWSER_RUNNER_DRY_MODE_RELEASE_GATE:START -->
## D0.28 browser-runner dry-mode release gate

Current implementation status: **D0.28 browser-runner dry-mode release gate shipped**.

The browser-runner stream now has a passive release-gate command:

```text
py -m patchops.cli llm-browser release-gate --repo-root C:\dev\patchops --json
```

Implemented files:

```text
patchops/llm_browser/dry_mode_release_gate.py
patchops/llm_browser/commands.py
tests/test_llm_browser_dry_mode_release_gate_current.py
```

Release-gate behavior:

- imports required passive llm-browser modules;
- verifies the integration safety policy rejects auto-send;
- verifies dry-run side-effect flags remain rejected;
- verifies audit metadata preserves JSON arrays;
- verifies a missing-artifact dry-run blocks with no side effects;
- verifies dry-mode/audit-log documentation exists and contains required operator contract phrases;
- verifies the expected llm-browser command surfaces are registered:
  - `doctor`;
  - `open`;
  - `dry-run`;
  - `run-once`;
  - `audit-log`;
  - `release-gate`;
- emits compact JSON with `--json`;
- emits compact text without `--json`;
- exits nonzero when the gate fails.

Safety behavior:

- release-gate is passive validation only;
- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps command is run by the gate;
- no composer paste happens here;
- no message is submitted/sent;
- no localhost service is created;
- no `--auto-send`, `--allow-send`, or `--live` option exists.
<!-- PATCHOPS_D0_28_BROWSER_RUNNER_DRY_MODE_RELEASE_GATE:END -->

<!-- PATCHOPS_D0_29_COMMIT_BROAD_VALIDATION_CHECKPOINT:START -->
## D0.29 commit and broad validation checkpoint

Current implementation status: **D0.29 commit and broad validation checkpoint shipped**.

The browser-runner stream now has a passive checkpoint command:

```text
py -m patchops.cli llm-browser checkpoint --repo-root C:\dev\patchops --json
```

Implemented files:

```text
patchops/llm_browser/dry_mode_checkpoint.py
patchops/llm_browser/commands.py
tests/test_llm_browser_dry_mode_checkpoint_current.py
```

Checkpoint behavior:

- runs the passive dry-mode release-gate evaluation;
- reads `git status --short --branch`;
- detects whether there are uncommitted changes;
- recommends a commit when the repository is dirty;
- emits a safe commit hint instead of committing:
  - `git add -A; git commit -m "..."`
- lists broad validation commands for the operator to run;
- emits JSON with `--json`;
- emits compact text without `--json`;
- exits nonzero only when the checkpoint gate itself fails.

Safety behavior:

- checkpoint is passive guidance only;
- no git commit is performed;
- no git push is performed;
- no broad pytest run is started by the checkpoint command;
- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps package command is run by the checkpoint command;
- no composer paste happens here;
- no message is submitted/sent;
- no localhost service is created;
- no `--commit`, `--push`, `--run-tests`, `--auto-send`, or `--live` option exists.
<!-- PATCHOPS_D0_29_COMMIT_BROAD_VALIDATION_CHECKPOINT:END -->

<!-- PATCHOPS_D0_30_OPERATOR_BROAD_VALIDATION_SCRIPT:START -->
## D0.30 operator broad validation script

Current implementation status: **D0.30 operator broad validation script shipped**.

The browser-runner stream now includes a broad validation script for operators:

```text
scripts/llm_browser_broad_validation.ps1
tests/test_llm_browser_broad_validation_script_current.py
```

Example usage:

```powershell
.\scripts\llm_browser_broad_validation.ps1 -RepoRoot C:\dev\patchops
```

Plan-only smoke usage:

```powershell
.\scripts\llm_browser_broad_validation.ps1 -RepoRoot C:\dev\patchops -PlanOnly
```

Script behavior:

- writes a single Desktop report by default;
- supports `-ReportPath` for controlled smoke/testing output;
- supports `-PlanOnly`;
- supports `-SkipFullPytest`;
- captures stdout and stderr for each native command;
- applies per-command timeouts;
- records timed-out commands as failures;
- runs:
  - `git status --short --branch`;
  - `python -m compileall patchops tests`;
  - `python -m patchops.cli llm-browser release-gate --repo-root <RepoRoot> --json`;
  - `python -m patchops.cli llm-browser checkpoint --repo-root <RepoRoot> --json`;
  - `python -m patchops.cli llm-browser doctor --browser none --json`;
  - `python -m patchops.cli llm-browser audit-log --path <missing-temp-file> --json`;
  - `python -m pytest -q` unless `-SkipFullPytest` is provided;
- exits `0` only when all executed commands pass.

Safety behavior:

- broad validation is operator-run, not automatic background work;
- the script does not run git commit;
- the script does not run git push;
- the script does not start a browser;
- the script does not start Selenium;
- the script does not click or download artifacts;
- the script does not run PatchOps packages;
- the script does not paste/send messages;
- no localhost service is created;
- no `--auto-send`, `--allow-send`, or live automation option is added.
<!-- PATCHOPS_D0_30_OPERATOR_BROAD_VALIDATION_SCRIPT:END -->

<!-- PATCHOPS_D0_30B_BROAD_VALIDATION_DOCS_PHRASE_REPAIR:START -->
## D0.30b broad validation docs phrase repair

Current implementation status: **D0.30 repaired by D0.30b**.

D0.30b repairs the D0.30 docs-contract failure by explicitly documenting the operator script's **full pytest** behavior.

The operator broad validation script is still:

```text
scripts/llm_browser_broad_validation.ps1
```

The script writes a single Desktop report by default, supports `PlanOnly`, supports `SkipFullPytest`, and runs **full pytest** by default through:

```text
python -m pytest -q
```

Use `-SkipFullPytest` only when the operator intentionally wants the broad validation script to skip the full pytest step.

Safety behavior remains unchanged:

- the script does not run git commit;
- the script does not run git push;
- the script does not start a browser;
- the script does not start Selenium;
- the script does not click or download artifacts;
- the script does not run PatchOps packages;
- the script does not paste/send messages;
- no localhost service is created.
<!-- PATCHOPS_D0_30B_BROAD_VALIDATION_DOCS_PHRASE_REPAIR:END -->

<!-- PATCHOPS_D0_31_BROAD_VALIDATION_REPORT_PARSER:START -->
## D0.31 broad validation report parser

Current implementation status: **D0.31 broad validation report parser shipped**.

The operator broad-validation flow now has a stable report-location contract and a parser.

Implemented files:

```text
patchops/llm_browser/broad_validation_report.py
patchops/llm_browser/commands.py
scripts/llm_browser_broad_validation.ps1
tests/test_llm_browser_broad_validation_report_current.py
tests/test_llm_browser_broad_validation_report_location_current.py
```

Report-location behavior:

- the operator script now defaults to a Desktop report folder:
  - `Desktop\patchops_reports`;
- each broad-validation run writes:
  - `Desktop\patchops_reports\patchops_llm_browser_broad_validation_YYYYMMDD_HHMMSS.txt`;
- each run also updates a Desktop pointer file:
  - `Desktop\patchops_latest_llm_browser_broad_validation_report.txt`;
- the pointer file contains:
  - result;
  - report path;
  - report folder;
  - a ready-to-copy Notepad command.

Parser behavior:

- `patchops/llm_browser/broad_validation_report.py` can parse result, exit code, commands, failures, and timeouts from broad-validation txt reports;
- `llm-browser broad-report --path <report.txt> --json` emits structured JSON;
- `llm-browser broad-report --path <report.txt>` emits a compact text summary;
- `--strict` returns nonzero when the parsed report is not PASS.

Example parser command:

```powershell
py -m patchops.cli llm-browser broad-report --path "$env:USERPROFILE\Desktop\patchops_reports\patchops_llm_browser_broad_validation_YYYYMMDD_HHMMSS.txt" --json
```

Safety behavior:

- the parser is read-only;
- the pointer file only points to the latest report;
- no browser starts during validation;
- no Selenium dependency is required;
- no download click happens here;
- no PatchOps package command is run by the parser;
- no composer paste happens here;
- no message is submitted/sent;
- no localhost service is created;
- no `--auto-send`, `--allow-send`, or `--live` option exists.
<!-- PATCHOPS_D0_31_BROAD_VALIDATION_REPORT_PARSER:END -->
