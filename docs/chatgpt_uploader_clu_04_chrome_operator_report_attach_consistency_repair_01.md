# CLU-04 repair 01: preserve child send-risk classification

Patch `clu_04_chrome_operator_report_attach_consistency_runner_repair_01` fixes the CLU-04 consistency runner classification for child send-risk failures.

## Failure fixed

The focused test `test_send_risk_blocks_immediately` expected:

```text
BLOCKED_CHROME_ATTACH_CONSISTENCY_SEND_RISK
```

The runner returned:

```text
BLOCKED_CHROME_ATTACH_CONSISTENCY_FLAKY
```

## Root cause

The CLU-03 child attach probe correctly exposes send-risk evidence through its result label and `send_risk_detected` field, but the CLU-04 aggregation loop only escalated send risk when forbidden submit/upload/send/post flags were true.

A child result with label `BLOCKED_SEND_RISK` therefore fell through to the generic flaky path.

## Repair

CLU-04 now treats a child result as send-risk when either condition is true:

```text
child.send_risk_detected == true
child.result_label == BLOCKED_SEND_RISK
```

The runner still refuses to proceed and still keeps all no-send/no-submit/no-DOM safety evidence unchanged.

## Safety boundary

This is a classification repair only. It does not add browser actions, Send behavior, DOM automation, Selenium/WebDriver, Cloudflare/CAPTCHA bypass, raw conversation logging, random clicks, or unbounded loops.