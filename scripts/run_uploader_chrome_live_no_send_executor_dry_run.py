from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_live_no_send_executor_dry_run import (  # noqa: E402
    BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_INVALID_JSON,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_MISSING,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_NOT_READY,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSAFE,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSUPPORTED_KIND,
    DEFAULT_DRY_RUN_RELATIVE_PATH,
    DEFAULT_MARKER_RELATIVE_PATH,
    DEFAULT_PLAN_RELATIVE_PATH,
    PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED,
    PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_WRITTEN,
    load_and_validate_executor_plan,
    write_executor_dry_run,
    write_executor_dry_run_marker,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the Chrome live no-send executor plan in dry-run mode. No browser action is performed.")
    parser.add_argument("--plan-json", default=DEFAULT_PLAN_RELATIVE_PATH)
    parser.add_argument("--dry-run-json", default=DEFAULT_DRY_RUN_RELATIVE_PATH)
    parser.add_argument("--dry-run-marker", default=DEFAULT_MARKER_RELATIVE_PATH)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    dry_run = load_and_validate_executor_plan(args.plan_json)
    if args.dry_run_json:
        write_executor_dry_run(dry_run, args.dry_run_json)
    if args.dry_run_marker:
        write_executor_dry_run_marker(dry_run, args.dry_run_marker)

    payload = dry_run.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {dry_run.result}")
        print(f"OK: {str(dry_run.ok).lower()}")
        print(f"DRY_RUN_KIND: {dry_run.dry_run_kind}")
        print(f"EXPECTED_BROWSER: {dry_run.expected_browser}")
        print(f"PLAN_KIND: {dry_run.plan_kind or ''}")
        print(f"PLAN_RESULT: {dry_run.plan_result or ''}")
        print(f"DRY_RUN_READY: {str(dry_run.dry_run_ready).lower()}")
        print(f"EXECUTOR_PLAN_READY: {str(dry_run.executor_plan_ready).lower()}")
        print(f"NO_SEND_VERIFIED: {str(dry_run.no_send_verified).lower()}")
        print(f"ATTACHMENT_VERIFIED: {str(dry_run.attachment_verified).lower()}")
        print("dry_run_performs_browser_action:false")
        print("dry_run_performs_chatgpt_submit:false")
        print("dry_run_reads_conversation_text:false")
        print("executor_dry_run_performed_live_action:false")
        print("browser_action_performed:false")
        print("chatgpt_submit_performed:false")
        print("send_allowed:false")
        print("raw_conversation_text_available:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print("conversation_text_logged:false")
        print("raw_conversation_text_logged:false")
        print(f"REASON: {dry_run.reason}")

    if dry_run.result in {
        PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED,
        PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_WRITTEN,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_MISSING,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_INVALID_JSON,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSUPPORTED_KIND,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_NOT_READY,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSAFE,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())