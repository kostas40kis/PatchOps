from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_live_no_send_executor_plan import (  # noqa: E402
    BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_INVALID_JSON,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_MISSING,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_NOT_READY,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSAFE,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSUPPORTED_KIND,
    DEFAULT_CONTRACT_RELATIVE_PATH,
    DEFAULT_MARKER_RELATIVE_PATH,
    DEFAULT_PLAN_RELATIVE_PATH,
    PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED,
    PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_WRITTEN,
    load_and_validate_preflight_contract,
    write_executor_plan,
    write_executor_plan_marker,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a no-action Chrome live no-send executor plan from the preflight contract.")
    parser.add_argument("--contract-json", default=DEFAULT_CONTRACT_RELATIVE_PATH)
    parser.add_argument("--plan-json", default=DEFAULT_PLAN_RELATIVE_PATH)
    parser.add_argument("--plan-marker", default=DEFAULT_MARKER_RELATIVE_PATH)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    plan = load_and_validate_preflight_contract(args.contract_json)
    if args.plan_json:
        write_executor_plan(plan, args.plan_json)
    if args.plan_marker:
        write_executor_plan_marker(plan, args.plan_marker)

    payload = plan.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {plan.result}")
        print(f"OK: {str(plan.ok).lower()}")
        print(f"PLAN_KIND: {plan.plan_kind}")
        print(f"EXPECTED_BROWSER: {plan.expected_browser}")
        print(f"CONTRACT_KIND: {plan.contract_kind or ''}")
        print(f"CONTRACT_RESULT: {plan.contract_result or ''}")
        print(f"EXECUTOR_PLAN_READY: {str(plan.executor_plan_ready).lower()}")
        print(f"NO_SEND_VERIFIED: {str(plan.no_send_verified).lower()}")
        print(f"ATTACHMENT_VERIFIED: {str(plan.attachment_verified).lower()}")
        print("executor_plan_performs_browser_action:false")
        print("executor_plan_performs_chatgpt_submit:false")
        print("executor_plan_reads_conversation_text:false")
        print("browser_action_performed:false")
        print("chatgpt_submit_performed:false")
        print("send_allowed:false")
        print("raw_conversation_text_available:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print("conversation_text_logged:false")
        print("raw_conversation_text_logged:false")
        print(f"REASON: {plan.reason}")

    if plan.result in {
        PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED,
        PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_WRITTEN,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_MISSING,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_INVALID_JSON,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSUPPORTED_KIND,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_NOT_READY,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSAFE,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())