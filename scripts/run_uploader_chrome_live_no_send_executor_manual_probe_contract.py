from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_live_no_send_executor_manual_probe_contract import (  # noqa: E402
    BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_INVALID_JSON,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_MISSING,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_NOT_READY,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSAFE,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSUPPORTED_KIND,
    DEFAULT_CONTRACT_RELATIVE_PATH,
    DEFAULT_DRY_RUN_RELATIVE_PATH,
    DEFAULT_MARKER_RELATIVE_PATH,
    PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_VALIDATED,
    PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_WRITTEN,
    load_and_validate_executor_dry_run,
    write_manual_probe_contract,
    write_manual_probe_contract_marker,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a no-action manual-probe contract from the Chrome live no-send executor dry run.")
    parser.add_argument("--dry-run-json", default=DEFAULT_DRY_RUN_RELATIVE_PATH)
    parser.add_argument("--contract-json", default=DEFAULT_CONTRACT_RELATIVE_PATH)
    parser.add_argument("--contract-marker", default=DEFAULT_MARKER_RELATIVE_PATH)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    contract = load_and_validate_executor_dry_run(args.dry_run_json)
    if args.contract_json:
        write_manual_probe_contract(contract, args.contract_json)
    if args.contract_marker:
        write_manual_probe_contract_marker(contract, args.contract_marker)

    payload = contract.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {contract.result}")
        print(f"OK: {str(contract.ok).lower()}")
        print(f"CONTRACT_KIND: {contract.contract_kind}")
        print(f"EXPECTED_BROWSER: {contract.expected_browser}")
        print(f"DRY_RUN_KIND: {contract.dry_run_kind or ''}")
        print(f"DRY_RUN_RESULT: {contract.dry_run_result or ''}")
        print(f"MANUAL_PROBE_CONTRACT_READY: {str(contract.manual_probe_contract_ready).lower()}")
        print(f"CONFIRMATION_TEXT: {contract.confirmation_text}")
        print("manual_probe_contract_performs_browser_action:false")
        print("manual_probe_contract_performs_chatgpt_submit:false")
        print("manual_probe_contract_reads_conversation_text:false")
        print("manual_probe_contract_performed_live_action:false")
        print("browser_action_performed:false")
        print("chatgpt_submit_performed:false")
        print("send_allowed:false")
        print("raw_conversation_text_available:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print("conversation_text_logged:false")
        print("raw_conversation_text_logged:false")
        print(f"REASON: {contract.reason}")

    if contract.result in {
        PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_VALIDATED,
        PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_WRITTEN,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_MISSING,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_INVALID_JSON,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSUPPORTED_KIND,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_NOT_READY,
        BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSAFE,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())