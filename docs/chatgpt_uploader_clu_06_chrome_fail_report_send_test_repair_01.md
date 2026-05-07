# CLU-06 repair 01: test helper gate override ordering

Patch `clu_06_chrome_fail_report_send_test_repair_01` fixes a generated test helper bug in CLU-06.

## Failure fixed

The focused test `test_operator_report_file_must_exist` created valid send-gate evidence, deleted the operator report, and passed that gate evidence into `run_ready` as an override.

The helper still eagerly built default gate evidence first:

```text
"send_gate_payload": ready_gate(report)
```

That recomputed `sha256_file(report)` after the file had been deleted, causing `FileNotFoundError` before the production function could return the intended blocked result.

## Repair

The test helper now checks for a supplied `send_gate_payload` override before building default gate evidence.

This keeps production behavior unchanged and lets the test exercise the intended result:

```text
BLOCKED_CHROME_FAIL_REPORT_SEND_HASH_MISMATCH
```

## Safety boundary

This is a test-only repair. It adds no browser action, no upload, no Send behavior, no DOM automation, no Selenium/WebDriver, no bypass behavior, no raw conversation logging, no random clicks, and no unbounded loop.