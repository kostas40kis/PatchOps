from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_acceptance_handoff import (  # noqa: E402
    BLOCKED_ACCEPTANCE_HANDOFF_INVALID_JSON,
    BLOCKED_ACCEPTANCE_HANDOFF_MISSING,
    BLOCKED_ACCEPTANCE_HANDOFF_UNSAFE,
    BLOCKED_ACCEPTANCE_NOT_PASSED,
    DEFAULT_HANDOFF_RELATIVE_PATH,
    PASS_CHROME_ACCEPTANCE_HANDOFF_VALIDATED,
    PASS_CHROME_ACCEPTANCE_HANDOFF_WRITTEN,
    load_and_validate_acceptance,
    write_acceptance_handoff,
    write_acceptance_handoff_marker,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish a downstream-safe handoff from Chrome no-send repeatability acceptance evidence.")
    parser.add_argument("--acceptance-json", required=True)
    parser.add_argument("--handoff-json", default=DEFAULT_HANDOFF_RELATIVE_PATH)
    parser.add_argument("--handoff-marker", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    handoff = load_and_validate_acceptance(args.acceptance_json)
    if args.handoff_json:
        write_acceptance_handoff(handoff, args.handoff_json)
    if args.handoff_marker:
        write_acceptance_handoff_marker(handoff, args.handoff_marker)

    payload = handoff.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {handoff.result}")
        print(f"OK: {str(handoff.ok).lower()}")
        print(f"HANDOFF_KIND: {handoff.handoff_kind}")
        print(f"EXPECTED_BROWSER: {handoff.expected_browser}")
        print(f"ACCEPTANCE_RESULT: {handoff.acceptance_result or ''}")
        print(f"ATTEMPT_COUNT: {handoff.attempt_count}")
        print(f"PASS_COUNT: {handoff.pass_count}")
        print(f"NO_SEND_VERIFIED: {str(handoff.no_send_verified).lower()}")
        print(f"ATTACHMENT_VERIFIED: {str(handoff.attachment_verified).lower()}")
        print("chatgpt_submit_performed:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print("conversation_text_logged:false")
        print("raw_conversation_text_logged:false")
        print(f"REASON: {handoff.reason}")

    if handoff.result in {
        PASS_CHROME_ACCEPTANCE_HANDOFF_VALIDATED,
        PASS_CHROME_ACCEPTANCE_HANDOFF_WRITTEN,
        BLOCKED_ACCEPTANCE_HANDOFF_MISSING,
        BLOCKED_ACCEPTANCE_HANDOFF_INVALID_JSON,
        BLOCKED_ACCEPTANCE_NOT_PASSED,
        BLOCKED_ACCEPTANCE_HANDOFF_UNSAFE,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())