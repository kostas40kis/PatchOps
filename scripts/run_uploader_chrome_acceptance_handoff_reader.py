from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_acceptance_handoff_reader import (  # noqa: E402
    BLOCKED_HANDOFF_READER_INVALID_JSON,
    BLOCKED_HANDOFF_READER_MISSING,
    BLOCKED_HANDOFF_READER_NOT_ACCEPTED,
    BLOCKED_HANDOFF_READER_UNSAFE,
    BLOCKED_HANDOFF_READER_UNSUPPORTED_KIND,
    DEFAULT_CONSUMED_RELATIVE_PATH,
    DEFAULT_HANDOFF_RELATIVE_PATH,
    PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER,
    PASS_CHROME_ACCEPTANCE_HANDOFF_READER_WRITTEN,
    load_and_validate_handoff,
    write_consumed_handoff,
    write_consumed_handoff_marker,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read and validate the downstream Chrome no-send uploader acceptance handoff without opening a browser.")
    parser.add_argument("--handoff-json", default=DEFAULT_HANDOFF_RELATIVE_PATH)
    parser.add_argument("--consumed-json", default=DEFAULT_CONSUMED_RELATIVE_PATH)
    parser.add_argument("--consumed-marker", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = load_and_validate_handoff(args.handoff_json)
    if args.consumed_json:
        write_consumed_handoff(result, args.consumed_json)
    if args.consumed_marker:
        write_consumed_handoff_marker(result, args.consumed_marker)

    payload = result.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {result.result}")
        print(f"OK: {str(result.ok).lower()}")
        print(f"CONSUMED_KIND: {result.consumed_kind}")
        print(f"HANDOFF_KIND: {result.handoff_kind or ''}")
        print(f"EXPECTED_BROWSER: {result.expected_browser}")
        print(f"ACCEPTANCE_RESULT: {result.acceptance_result or ''}")
        print(f"ATTEMPT_COUNT: {result.attempt_count}")
        print(f"PASS_COUNT: {result.pass_count}")
        print(f"NO_SEND_VERIFIED: {str(result.no_send_verified).lower()}")
        print(f"ATTACHMENT_VERIFIED: {str(result.attachment_verified).lower()}")
        print(f"DOWNSTREAM_CONTRACT_ACCEPTED: {str(result.downstream_contract_accepted).lower()}")
        print("browser_opened_by_reader:false")
        print("no_browser_action_performed:true")
        print("chatgpt_submit_performed:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print("conversation_text_logged:false")
        print("raw_conversation_text_logged:false")
        print(f"REASON: {result.reason}")

    if result.result in {
        PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER,
        PASS_CHROME_ACCEPTANCE_HANDOFF_READER_WRITTEN,
        BLOCKED_HANDOFF_READER_MISSING,
        BLOCKED_HANDOFF_READER_INVALID_JSON,
        BLOCKED_HANDOFF_READER_UNSUPPORTED_KIND,
        BLOCKED_HANDOFF_READER_NOT_ACCEPTED,
        BLOCKED_HANDOFF_READER_UNSAFE,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())