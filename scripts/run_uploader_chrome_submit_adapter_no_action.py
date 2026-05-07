from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_submit_adapter import (  # noqa: E402
    BLOCKED_FORBIDDEN_SUBMIT_BACKEND,
    BLOCKED_SEND_GATE_NOT_READY,
    BLOCKED_SUBMIT_ACTION_NOT_IMPLEMENTED,
    BLOCKED_SUBMIT_CONFIRMATION_MISSING,
    LIVE_CONFIRM_TEXT,
    PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION,
    PASS_CHROME_SUBMIT_READY_NO_ACTION,
    SAFE_DRY_RUN_BACKEND,
    evaluate_chrome_submit_adapter,
    write_chrome_submit_adapter_decision,
)


def _load_gate(path: str | None, inline_json: str | None) -> dict[str, object]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    if inline_json:
        value = json.loads(inline_json)
        if isinstance(value, dict):
            return value
    return {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chrome submit adapter boundary. Emits readiness/dry-run evidence only; does not press Send.")
    parser.add_argument("--send-gate-decision", default=None)
    parser.add_argument("--send-gate-decision-json", default=None)
    parser.add_argument("--submit-backend", default=SAFE_DRY_RUN_BACKEND)
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--allow-submit-action", action="store_true")
    parser.add_argument("--decision-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    gate = _load_gate(args.send_gate_decision, args.send_gate_decision_json)
    decision = evaluate_chrome_submit_adapter(
        send_gate_decision=gate,
        submit_backend=args.submit_backend,
        live_browser=args.live_browser,
        confirm_live_browser_text=args.confirm_live_browser_text,
        allow_submit_action=args.allow_submit_action,
    )

    if args.decision_path:
        write_chrome_submit_adapter_decision(decision, args.decision_path)

    payload = decision.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {decision.result}")
        print(f"OK: {str(decision.ok).lower()}")
        print(f"EXPECTED_BROWSER: {decision.expected_browser}")
        print(f"SEND_GATE_RESULT: {decision.send_gate_result or ''}")
        print(f"SEND_GATE_READY: {str(decision.send_gate_ready).lower()}")
        print(f"ATTACHMENT_CONFIRMED: {str(decision.attachment_confirmed).lower()}")
        print(f"SUBMIT_BACKEND: {decision.submit_backend}")
        print("submit_action_allowed:false")
        print("send_button_pressed:false")
        print("submit_action_performed:false")
        print("chatgpt_submit_performed:false")
        print("raw_conversation_text_logged:false")
        print("conversation_text_logged:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print(f"REASON: {decision.reason}")

    if decision.result in {
        PASS_CHROME_SUBMIT_READY_NO_ACTION,
        PASS_CHROME_SUBMIT_DRY_RUN_NO_ACTION,
        BLOCKED_SEND_GATE_NOT_READY,
        BLOCKED_SUBMIT_CONFIRMATION_MISSING,
        BLOCKED_SUBMIT_ACTION_NOT_IMPLEMENTED,
        BLOCKED_FORBIDDEN_SUBMIT_BACKEND,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())