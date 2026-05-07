from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_downstream_ready_contract import (  # noqa: E402
    BLOCKED_DOWNSTREAM_READY_CONSUMED_INVALID_JSON,
    BLOCKED_DOWNSTREAM_READY_CONSUMED_MISSING,
    BLOCKED_DOWNSTREAM_READY_NOT_ACCEPTED,
    BLOCKED_DOWNSTREAM_READY_UNSAFE,
    BLOCKED_DOWNSTREAM_READY_UNSUPPORTED_KIND,
    DEFAULT_CONSUMED_RELATIVE_PATH,
    DEFAULT_READY_CONTRACT_RELATIVE_PATH,
    PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED,
    PASS_CHROME_DOWNSTREAM_READY_CONTRACT_WRITTEN,
    load_and_validate_consumed,
    write_ready_contract,
    write_ready_contract_marker,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a downstream planning-ready contract from the Chrome no-send consumed handoff. No browser action is performed.")
    parser.add_argument("--consumed-json", default=DEFAULT_CONSUMED_RELATIVE_PATH)
    parser.add_argument("--ready-contract-json", default=DEFAULT_READY_CONTRACT_RELATIVE_PATH)
    parser.add_argument("--ready-contract-marker", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    contract = load_and_validate_consumed(args.consumed_json)
    if args.ready_contract_json:
        write_ready_contract(contract, args.ready_contract_json)
    if args.ready_contract_marker:
        write_ready_contract_marker(contract, args.ready_contract_marker)

    payload = contract.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {contract.result}")
        print(f"OK: {str(contract.ok).lower()}")
        print(f"READY_CONTRACT_KIND: {contract.ready_contract_kind}")
        print(f"EXPECTED_BROWSER: {contract.expected_browser}")
        print(f"CONSUMED_KIND: {contract.consumed_kind or ''}")
        print(f"CONSUMED_RESULT: {contract.consumed_result or ''}")
        print(f"ACCEPTANCE_RESULT: {contract.acceptance_result or ''}")
        print(f"NO_SEND_VERIFIED: {str(contract.no_send_verified).lower()}")
        print(f"ATTACHMENT_VERIFIED: {str(contract.attachment_verified).lower()}")
        print(f"SAFE_FOR_DOWNSTREAM_PLANNING: {str(contract.safe_for_downstream_planning).lower()}")
        print("read_only_contract:true")
        print("browser_action_performed:false")
        print("chatgpt_submit_performed:false")
        print("raw_conversation_text_available:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print("conversation_text_logged:false")
        print("raw_conversation_text_logged:false")
        print(f"REASON: {contract.reason}")

    if contract.result in {
        PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED,
        PASS_CHROME_DOWNSTREAM_READY_CONTRACT_WRITTEN,
        BLOCKED_DOWNSTREAM_READY_CONSUMED_MISSING,
        BLOCKED_DOWNSTREAM_READY_CONSUMED_INVALID_JSON,
        BLOCKED_DOWNSTREAM_READY_UNSUPPORTED_KIND,
        BLOCKED_DOWNSTREAM_READY_NOT_ACCEPTED,
        BLOCKED_DOWNSTREAM_READY_UNSAFE,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())