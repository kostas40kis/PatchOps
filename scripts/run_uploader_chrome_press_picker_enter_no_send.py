from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_picker_enter_no_send import (  # noqa: E402
    BLOCKED_CANONICAL_REPORT_MISSING,
    BLOCKED_PATH_NOT_CANONICAL_REPORT,
    BLOCKED_PATH_NOT_WRITTEN,
    BLOCKED_PICKER_ENTER_CONFIRMATION_MISSING,
    BLOCKED_PICKER_HWND_MISSING,
    BLOCKED_PICKER_NOT_READY,
    FAIL_PATH_ENTER_FAILED,
    FAIL_PICKER_NOT_CLOSED_AFTER_ENTER,
    LIVE_CONFIRM_TEXT,
    PASS_CHROME_PICKER_ENTERED_NO_SEND,
    run_picker_enter_no_send,
    write_picker_enter_no_send_evidence,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Press Enter once inside a confirmed Windows picker after exact path entry. Stops before send and does not claim attachment verification.")
    parser.add_argument("--canonical-report", required=True)
    parser.add_argument("--picker-ready", action="store_true")
    parser.add_argument("--picker-hwnd", type=int, default=None)
    parser.add_argument("--path-written-before-enter", action="store_true")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--allow-picker-enter", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--mock-enter-success", action="store_true")
    parser.add_argument("--mock-picker-closed-after-enter", action="store_true")
    parser.add_argument("--wait-seconds", type=float, default=8.0)
    parser.add_argument("--poll-interval-seconds", type=float, default=0.25)
    parser.add_argument("--evidence-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    evidence = run_picker_enter_no_send(
        canonical_report_path=args.canonical_report,
        picker_ready=args.picker_ready,
        picker_hwnd=args.picker_hwnd,
        path_written_before_enter=args.path_written_before_enter,
        live_browser=args.live_browser,
        allow_picker_enter=args.allow_picker_enter,
        confirm_live_browser_text=args.confirm_live_browser_text,
        mock_enter_success=args.mock_enter_success,
        mock_picker_closed_after_enter=args.mock_picker_closed_after_enter,
        wait_seconds=args.wait_seconds,
        poll_interval_seconds=args.poll_interval_seconds,
    )

    if args.evidence_path:
        write_picker_enter_no_send_evidence(evidence, args.evidence_path)

    payload = evidence.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {evidence.result}")
        print(f"OK: {str(evidence.ok).lower()}")
        print(f"EXPECTED_BROWSER: {evidence.expected_browser}")
        print(f"PICKER_READY: {str(evidence.picker_ready).lower()}")
        print(f"PATH_WRITTEN_BEFORE_ENTER: {str(evidence.path_written_before_enter).lower()}")
        print(f"LIVE_BROWSER_USED: {str(evidence.live_browser_used).lower()}")
        print(f"REPORT_PATH_HASH: {evidence.report_path_hash or ''}")
        print(f"REPORT_BASENAME: {evidence.report_basename or ''}")
        print("enter_pressed:" + str(evidence.enter_pressed).lower())
        print("picker_closed_after_enter:" + str(evidence.picker_closed_after_enter).lower())
        print("file_upload_attempted:" + str(evidence.file_upload_attempted).lower())
        print("open_button_pressed:false")
        print("chatgpt_submit_performed:false")
        print("attachment_confirmed:false")
        print("raw_conversation_text_logged:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print(f"REASON: {evidence.reason}")

    if evidence.result in {
        PASS_CHROME_PICKER_ENTERED_NO_SEND,
        FAIL_PICKER_NOT_CLOSED_AFTER_ENTER,
        FAIL_PATH_ENTER_FAILED,
        BLOCKED_PICKER_NOT_READY,
        BLOCKED_PATH_NOT_WRITTEN,
        BLOCKED_PICKER_ENTER_CONFIRMATION_MISSING,
        BLOCKED_PICKER_HWND_MISSING,
        BLOCKED_CANONICAL_REPORT_MISSING,
        BLOCKED_PATH_NOT_CANONICAL_REPORT,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())