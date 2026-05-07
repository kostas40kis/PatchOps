from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_send_gate import (  # noqa: E402
    BLOCKED_ATTACHMENT_NOT_CONFIRMED,
    BLOCKED_SEND_ACTION_NOT_IMPLEMENTED,
    BLOCKED_SEND_CONFIRMATION_MISSING,
    LIVE_CONFIRM_TEXT,
    PASS_SEND_READY_NO_SUBMIT,
    evaluate_send_gate_no_submit,
    write_send_gate_decision,
)
from patchops.chatgpt_uploader.chrome_picker_path_entry import (  # noqa: E402
    BLOCKED_CANONICAL_REPORT_MISSING,
    BLOCKED_PATH_NOT_CANONICAL_REPORT,
)


def _load_attachment_evidence(path: str | None, inline_json: str | None) -> dict[str, object]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    if inline_json:
        value = json.loads(inline_json)
        if isinstance(value, dict):
            return value
    return {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Chrome upload send-readiness while keeping actual ChatGPT submit blocked.")
    parser.add_argument("--canonical-report", required=True)
    parser.add_argument("--attachment-evidence", default=None)
    parser.add_argument("--attachment-evidence-json", default=None)
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--allow-submit", action="store_true")
    parser.add_argument("--decision-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    attachment_evidence = _load_attachment_evidence(args.attachment_evidence, args.attachment_evidence_json)
    decision = evaluate_send_gate_no_submit(
        canonical_report_path=args.canonical_report,
        attachment_evidence=attachment_evidence,
        live_browser=args.live_browser,
        confirm_live_browser_text=args.confirm_live_browser_text,
        allow_submit=args.allow_submit,
    )

    if args.decision_path:
        write_send_gate_decision(decision, args.decision_path)

    payload = decision.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {decision.result}")
        print(f"OK: {str(decision.ok).lower()}")
        print(f"EXPECTED_BROWSER: {decision.expected_browser}")
        print(f"ATTACHMENT_CONFIRMED: {str(decision.attachment_confirmed).lower()}")
        print(f"EXPECTED_BASENAME: {decision.expected_basename or ''}")
        print(f"EXPECTED_BASENAME_SHA256: {decision.expected_basename_sha256 or ''}")
        print("submit_action_allowed:false")
        print("send_button_pressed:false")
        print("chatgpt_submit_performed:false")
        print("raw_conversation_text_logged:false")
        print("conversation_text_logged:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print(f"REASON: {decision.reason}")

    if decision.result in {
        PASS_SEND_READY_NO_SUBMIT,
        BLOCKED_ATTACHMENT_NOT_CONFIRMED,
        BLOCKED_SEND_CONFIRMATION_MISSING,
        BLOCKED_SEND_ACTION_NOT_IMPLEMENTED,
        BLOCKED_CANONICAL_REPORT_MISSING,
        BLOCKED_PATH_NOT_CANONICAL_REPORT,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())