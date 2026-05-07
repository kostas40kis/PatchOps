from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_picker_trigger import (  # noqa: E402
    BLOCKED_CHROME_TARGET_NOT_READY,
    BLOCKED_LIVE_BROWSER_CONFIRMATION_MISSING,
    BLOCKED_UNSAFE_TRIGGER,
    FAIL_CHROME_PICKER_NOT_OPENED,
    LIVE_CONFIRM_TEXT,
    PASS_CHROME_PICKER_OPENED_NO_UPLOAD,
    PASS_ONE_PICKER_DETECTED,
    SAFE_TRIGGER_NAME,
    build_picker_candidate,
    evaluate_chrome_picker_detection,
    run_chrome_picker_trigger,
    write_chrome_picker_trigger_evidence,
)


def _mock_picker_evidence(expected_chrome_hwnd: int | None):
    picker = build_picker_candidate(handle=501, owner_handle=expected_chrome_hwnd, expected_chrome_hwnd=expected_chrome_hwnd)
    return evaluate_chrome_picker_detection([picker], expected_chrome_hwnd=expected_chrome_hwnd)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chrome canonical picker trigger. Stops before path write, Open/Enter file selection, upload, or send.")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--expected-chrome-hwnd", type=int, default=None)
    parser.add_argument("--preflight-ready", action="store_true")
    parser.add_argument("--trigger-backend", default=SAFE_TRIGGER_NAME)
    parser.add_argument("--mock-picker-after-trigger", action="store_true")
    parser.add_argument("--wait-seconds", type=float, default=4.0)
    parser.add_argument("--poll-interval-seconds", type=float, default=0.5)
    parser.add_argument("--evidence-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    post_trigger = _mock_picker_evidence(args.expected_chrome_hwnd) if args.mock_picker_after_trigger else None
    evidence = run_chrome_picker_trigger(
        trigger_backend=args.trigger_backend,
        preflight_ready=args.preflight_ready,
        expected_chrome_hwnd=args.expected_chrome_hwnd,
        live_browser=args.live_browser,
        confirm_live_browser_text=args.confirm_live_browser_text,
        post_trigger_picker_evidence=post_trigger,
        wait_seconds=args.wait_seconds,
        poll_interval_seconds=args.poll_interval_seconds,
    )

    if args.evidence_path:
        write_chrome_picker_trigger_evidence(evidence, args.evidence_path)

    payload = evidence.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {evidence.result}")
        print(f"OK: {str(evidence.ok).lower()}")
        print(f"EXPECTED_BROWSER: {evidence.expected_browser}")
        print(f"LIVE_BROWSER_USED: {str(evidence.live_browser_used).lower()}")
        print(f"PREFLIGHT_READY: {str(evidence.preflight_ready).lower()}")
        print(f"TRIGGER_NAME: {evidence.trigger_plan.get('trigger_name')}")
        print(f"PICKER_DETECTED_AFTER_TRIGGER: {str(evidence.picker_detected_after_trigger).lower()}")
        print(f"PICKER_RESULT_AFTER_TRIGGER: {evidence.picker_result_after_trigger or ''}")
        print("file_path_written:false")
        print("open_button_pressed:false")
        print("file_upload_attempted:false")
        print("chatgpt_submit_performed:false")
        print("raw_conversation_text_logged:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print(f"REASON: {evidence.reason}")

    if evidence.result in {
        PASS_CHROME_PICKER_OPENED_NO_UPLOAD,
        FAIL_CHROME_PICKER_NOT_OPENED,
        BLOCKED_UNSAFE_TRIGGER,
        BLOCKED_CHROME_TARGET_NOT_READY,
        BLOCKED_LIVE_BROWSER_CONFIRMATION_MISSING,
        PASS_ONE_PICKER_DETECTED,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())