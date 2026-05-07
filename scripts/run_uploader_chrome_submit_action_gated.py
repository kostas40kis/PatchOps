from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_submit_action import (  # noqa: E402
    BLOCKED_LIVE_SUBMIT_CONFIRMATION_MISSING,
    BLOCKED_SUBMIT_ADAPTER_NOT_READY,
    BLOCKED_SUBMIT_BACKEND_UNSUPPORTED,
    BLOCKED_SUBMIT_HWND_MISSING,
    FAIL_SUBMIT_KEYPRESS_FAILED,
    LIVE_CONFIRM_TEXT,
    PASS_CHROME_SUBMIT_ACTION_MOCKED,
    PASS_CHROME_SUBMIT_ACTION_PERFORMED,
    SUBMIT_BACKEND_CTRL_ENTER,
    run_chrome_submit_action,
    write_chrome_submit_action_evidence,
)


def _load_adapter(path: str | None, inline_json: str | None) -> dict[str, object]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    if inline_json:
        value = json.loads(inline_json)
        if isinstance(value, dict):
            return value
    return {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Perform one explicitly gated Chrome submit keypress. No DOM/WebDriver automation and no conversation text logging.")
    parser.add_argument("--submit-adapter-decision", default=None)
    parser.add_argument("--submit-adapter-decision-json", default=None)
    parser.add_argument("--submit-backend", default=SUBMIT_BACKEND_CTRL_ENTER)
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--target-hwnd", type=int, default=None)
    parser.add_argument("--allow-submit-action", action="store_true")
    parser.add_argument("--mock-submit-success", action="store_true")
    parser.add_argument("--evidence-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    adapter = _load_adapter(args.submit_adapter_decision, args.submit_adapter_decision_json)
    evidence = run_chrome_submit_action(
        submit_adapter_decision=adapter,
        submit_backend=args.submit_backend,
        live_browser=args.live_browser,
        confirm_live_browser_text=args.confirm_live_browser_text,
        target_hwnd=args.target_hwnd,
        allow_submit_action=args.allow_submit_action,
        mock_submit_success=args.mock_submit_success,
    )

    if args.evidence_path:
        write_chrome_submit_action_evidence(evidence, args.evidence_path)

    payload = evidence.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {evidence.result}")
        print(f"OK: {str(evidence.ok).lower()}")
        print(f"EXPECTED_BROWSER: {evidence.expected_browser}")
        print(f"SUBMIT_ADAPTER_RESULT: {evidence.submit_adapter_result or ''}")
        print(f"SUBMIT_ADAPTER_READY: {str(evidence.submit_adapter_ready).lower()}")
        print(f"ATTACHMENT_CONFIRMED: {str(evidence.attachment_confirmed).lower()}")
        print(f"SUBMIT_BACKEND: {evidence.submit_backend}")
        print(f"KEYPRESS_ATTEMPTED: {str(evidence.keypress_attempted).lower()}")
        print("send_button_pressed:false")
        print("submit_action_performed:" + str(evidence.submit_action_performed).lower())
        print("chatgpt_submit_performed:" + str(evidence.chatgpt_submit_performed).lower())
        print("raw_conversation_text_logged:false")
        print("conversation_text_logged:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print(f"REASON: {evidence.reason}")

    if evidence.result in {
        PASS_CHROME_SUBMIT_ACTION_PERFORMED,
        PASS_CHROME_SUBMIT_ACTION_MOCKED,
        BLOCKED_SUBMIT_ADAPTER_NOT_READY,
        BLOCKED_LIVE_SUBMIT_CONFIRMATION_MISSING,
        BLOCKED_SUBMIT_HWND_MISSING,
        BLOCKED_SUBMIT_BACKEND_UNSUPPORTED,
        FAIL_SUBMIT_KEYPRESS_FAILED,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())