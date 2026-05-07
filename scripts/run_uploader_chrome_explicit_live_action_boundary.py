from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_explicit_live_action_boundary import (  # noqa: E402
    BLOCKED_LIVE_BOUNDARY_CONFIRMATION_REQUIRED,
    BLOCKED_LIVE_BOUNDARY_NOT_READY,
    BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_INVALID_JSON,
    BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_MISSING,
    BLOCKED_LIVE_BOUNDARY_UNSAFE,
    BLOCKED_LIVE_BOUNDARY_UNSUPPORTED_KIND,
    DEFAULT_BOUNDARY_RELATIVE_PATH,
    DEFAULT_READY_CONTRACT_RELATIVE_PATH,
    PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED,
    PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_WRITTEN,
    REQUIRED_CONFIRMATION_TEXT,
    load_and_validate_ready_contract,
    write_live_action_boundary,
    write_live_action_boundary_marker,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create an explicit human-confirmed live-action boundary from the Chrome downstream ready contract. No browser action is performed.")
    parser.add_argument("--ready-contract-json", default=DEFAULT_READY_CONTRACT_RELATIVE_PATH)
    parser.add_argument("--boundary-json", default=DEFAULT_BOUNDARY_RELATIVE_PATH)
    parser.add_argument("--boundary-marker", default=None)
    parser.add_argument("--confirm-live-action-text", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    boundary = load_and_validate_ready_contract(args.ready_contract_json, confirmation_text=args.confirm_live_action_text)
    if args.boundary_json:
        write_live_action_boundary(boundary, args.boundary_json)
    if args.boundary_marker:
        write_live_action_boundary_marker(boundary, args.boundary_marker)

    payload = boundary.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {boundary.result}")
        print(f"OK: {str(boundary.ok).lower()}")
        print(f"BOUNDARY_KIND: {boundary.boundary_kind}")
        print(f"EXPECTED_BROWSER: {boundary.expected_browser}")
        print(f"READY_CONTRACT_KIND: {boundary.ready_contract_kind or ''}")
        print(f"READY_RESULT: {boundary.ready_result or ''}")
        print(f"CONFIRMATION_REQUIRED: {str(boundary.confirmation_required).lower()}")
        print(f"REQUIRED_CONFIRMATION_TEXT: {REQUIRED_CONFIRMATION_TEXT}")
        print(f"BOUNDARY_CONFIRMED: {str(boundary.boundary_confirmed).lower()}")
        print(f"LIVE_ACTION_ALLOWED: {str(boundary.live_action_allowed).lower()}")
        print("send_allowed:false")
        print("browser_action_performed:false")
        print("chatgpt_submit_performed:false")
        print("raw_conversation_text_available:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print("conversation_text_logged:false")
        print("raw_conversation_text_logged:false")
        print(f"REASON: {boundary.reason}")

    if boundary.result in {
        PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED,
        PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_WRITTEN,
        BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_MISSING,
        BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_INVALID_JSON,
        BLOCKED_LIVE_BOUNDARY_UNSUPPORTED_KIND,
        BLOCKED_LIVE_BOUNDARY_NOT_READY,
        BLOCKED_LIVE_BOUNDARY_UNSAFE,
        BLOCKED_LIVE_BOUNDARY_CONFIRMATION_REQUIRED,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())