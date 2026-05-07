from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_live_no_send_preflight_contract import (  # noqa: E402
    BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_INVALID_JSON,
    BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_MISSING,
    BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_NOT_READY,
    BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSAFE,
    BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSUPPORTED_KIND,
    DEFAULT_CONTRACT_RELATIVE_PATH,
    DEFAULT_PACKET_RELATIVE_PATH,
    PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED,
    PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_WRITTEN,
    load_and_validate_instruction_packet,
    write_preflight_contract,
    write_preflight_contract_marker,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a Chrome live no-send preflight contract from the no-action live instruction packet. No browser action is performed.")
    parser.add_argument("--packet-json", default=DEFAULT_PACKET_RELATIVE_PATH)
    parser.add_argument("--contract-json", default=DEFAULT_CONTRACT_RELATIVE_PATH)
    parser.add_argument("--contract-marker", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    contract = load_and_validate_instruction_packet(args.packet_json)
    if args.contract_json:
        write_preflight_contract(contract, args.contract_json)
    if args.contract_marker:
        write_preflight_contract_marker(contract, args.contract_marker)

    payload = contract.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {contract.result}")
        print(f"OK: {str(contract.ok).lower()}")
        print(f"CONTRACT_KIND: {contract.contract_kind}")
        print(f"EXPECTED_BROWSER: {contract.expected_browser}")
        print(f"PACKET_KIND: {contract.packet_kind or ''}")
        print(f"PACKET_RESULT: {contract.packet_result or ''}")
        print(f"PREFLIGHT_CONTRACT_READY: {str(contract.preflight_contract_ready).lower()}")
        print(f"NO_SEND_VERIFIED: {str(contract.no_send_verified).lower()}")
        print(f"ATTACHMENT_VERIFIED: {str(contract.attachment_verified).lower()}")
        print("packet_performs_browser_action:false")
        print("packet_performs_chatgpt_submit:false")
        print("packet_reads_conversation_text:false")
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
        PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED,
        PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_WRITTEN,
        BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_MISSING,
        BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_INVALID_JSON,
        BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSUPPORTED_KIND,
        BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_NOT_READY,
        BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSAFE,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())