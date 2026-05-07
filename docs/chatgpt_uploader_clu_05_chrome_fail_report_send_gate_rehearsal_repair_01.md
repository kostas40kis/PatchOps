# CLU-05 repair 01: test helper override ordering

Patch `clu_05_chrome_fail_report_send_gate_rehearsal_repair_01` fixes a generated test helper bug in CLU-05.

## Failure fixed

The focused test `test_operator_report_file_must_still_exist` created valid CLU-04-style evidence, deleted the report file, and passed that evidence into `run_ready` as an override.

The helper still eagerly built default evidence first:

```text
"consistency_evidence_payload": passing_evidence(report)
```

That recomputed `sha256_file(report)` after the file had been deleted, causing `FileNotFoundError` before the production function could return the intended blocked result.

## Repair

The test helper now checks for a supplied `consistency_evidence_payload` override before building default evidence.

This keeps the production behavior unchanged and lets the test exercise the intended path:

```text
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH
```

## Safety boundary

This is a test-only repair. It adds no browser action, no upload, no Send behavior, no DOM automation, no Selenium/WebDriver, no bypass behavior, no raw conversation logging, no random clicks, and no unbounded loop.