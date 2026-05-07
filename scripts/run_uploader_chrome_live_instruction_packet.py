from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_live_instruction_packet import (  # noqa: E402
    BLOCKED_LIVE_INSTRUCTION_BOUNDARY_INVALID_JSON,
    BLOCKED_LIVE_INSTRUCTION_BOUNDARY_MISSING,
    BLOCKED_LIVE_INSTRUCTION_BOUNDARY_NOT_CONFIRMED,
    BLOCKED_LIVE_INSTRUCTION_UNSAFE,
    BLOCKED_LIVE_INSTRUCTION_UNSUPPORTED_KIND,
    DEFAULT_BOUNDARY_RELATIVE_PATH,
    DEFAULT_PACKET_RELATIVE_PATH,
    PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED,
    PASS_CHROME_LIVE_INSTRUCTION_PACKET_WRITTEN,
    load_and_validate_boundary,
    write_instruction_packet,
    write_instruction_packet_marker,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a no-action Chrome live instruction packet from a confirmed explicit live-action boundary.")
    parser.add_argument("--boundary-json", default=DEFAULT_BOUNDARY_RELATIVE_PATH)
    parser.add_argument("--packet-json", default=DEFAULT_PACKET_RELATIVE_PATH)
    parser.add_argument("--packet-marker", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    packet = load_and_validate_boundary(args.boundary_json)
    if args.packet_json:
        write_instruction_packet(packet, args.packet_json)
    if args.packet_marker:
        write_instruction_packet_marker(packet, args.packet_marker)

    payload = packet.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {packet.result}")
        print(f"OK: {str(packet.ok).lower()}")
        print(f"PACKET_KIND: {packet.packet_kind}")
        print(f"EXPECTED_BROWSER: {packet.expected_browser}")
        print(f"BOUNDARY_KIND: {packet.boundary_kind or ''}")
        print(f"BOUNDARY_RESULT: {packet.boundary_result or ''}")
        print(f"BOUNDARY_CONFIRMED: {str(packet.boundary_confirmed).lower()}")
        print(f"LIVE_ACTION_ALLOWED_BY_BOUNDARY: {str(packet.live_action_allowed_by_boundary).lower()}")
        print("packet_performs_browser_action:false")
        print("packet_performs_chatgpt_submit:false")
        print("packet_reads_conversation_text:false")
        print("send_allowed:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print("conversation_text_logged:false")
        print("raw_conversation_text_logged:false")
        print(f"REASON: {packet.reason}")

    if packet.result in {
        PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED,
        PASS_CHROME_LIVE_INSTRUCTION_PACKET_WRITTEN,
        BLOCKED_LIVE_INSTRUCTION_BOUNDARY_MISSING,
        BLOCKED_LIVE_INSTRUCTION_BOUNDARY_INVALID_JSON,
        BLOCKED_LIVE_INSTRUCTION_UNSUPPORTED_KIND,
        BLOCKED_LIVE_INSTRUCTION_BOUNDARY_NOT_CONFIRMED,
        BLOCKED_LIVE_INSTRUCTION_UNSAFE,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())