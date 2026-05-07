from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_picker_trigger import (  # noqa: E402
    BLOCKED_AMBIGUOUS_PICKER,
    BLOCKED_LIVE_BROWSER_CONFIRMATION_MISSING,
    BLOCKED_PICKER_ERROR_MODAL,
    LIVE_CONFIRM_TEXT,
    PASS_NO_PICKER,
    PASS_ONE_PICKER_DETECTED,
    build_picker_candidate,
    run_chrome_picker_detector,
    write_chrome_picker_evidence,
)


def _mock_picker_from_arg(value: str, expected_chrome_hwnd: int | None):
    parts = value.split("|")
    while len(parts) < 5:
        parts.append("")
    handle = int(parts[0] or "0")
    owner_handle = int(parts[1]) if parts[1] else None
    visible = (parts[2] or "true").strip().lower() in {"1", "true", "yes", "visible"}
    enabled = (parts[3] or "true").strip().lower() in {"1", "true", "yes", "enabled"}
    title_hash = parts[4] or "mock-title-sha256"
    return build_picker_candidate(
        handle=handle,
        owner_handle=owner_handle,
        visible=visible,
        enabled=enabled,
        title_sha256=title_hash,
        expected_chrome_hwnd=expected_chrome_hwnd,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Detect Chrome-context Windows file picker state. No path write, no upload, no send.")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--expected-chrome-hwnd", type=int, default=None)
    parser.add_argument("--mock-picker", action="append", default=[], help="Local test picker: handle|owner_handle|visible|enabled|title_hash")
    parser.add_argument("--mock-error-modal", action="append", default=[], help="Local test error modal: handle|owner_handle|visible|enabled|title_hash")
    parser.add_argument("--wait-seconds", type=float, default=0.0)
    parser.add_argument("--poll-interval-seconds", type=float, default=0.5)
    parser.add_argument("--evidence-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    pickers = [_mock_picker_from_arg(item, args.expected_chrome_hwnd) for item in args.mock_picker]
    errors = [_mock_picker_from_arg(item, args.expected_chrome_hwnd) for item in args.mock_error_modal]

    evidence = run_chrome_picker_detector(
        live_browser=args.live_browser,
        confirm_live_browser_text=args.confirm_live_browser_text,
        expected_chrome_hwnd=args.expected_chrome_hwnd,
        picker_candidates=pickers,
        error_modal_candidates=errors,
        wait_seconds=args.wait_seconds,
        poll_interval_seconds=args.poll_interval_seconds,
    )

    if args.evidence_path:
        write_chrome_picker_evidence(evidence, args.evidence_path)

    payload = evidence.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {evidence.result}")
        print(f"OK: {str(evidence.ok).lower()}")
        print(f"EXPECTED_BROWSER: {evidence.expected_browser}")
        print(f"LIVE_BROWSER_USED: {str(evidence.live_browser_used).lower()}")
        print(f"PICKER_DETECTED: {str(evidence.picker_detected).lower()}")
        print(f"PICKER_COUNT: {evidence.picker_count}")
        print(f"AMBIGUOUS: {str(evidence.ambiguous).lower()}")
        print(f"ERROR_MODAL_DETECTED: {str(evidence.error_modal_detected).lower()}")
        print(f"ERROR_MODAL_COUNT: {evidence.error_modal_count}")
        print(f"PICKER_OWNED_BY_EXPECTED_CHROME_FLOW: {evidence.picker_owned_by_expected_chrome_flow}")
        print("raw_conversation_text_logged:false")
        print("conversation_text_logged:false")
        print("file_path_written:false")
        print("open_button_pressed:false")
        print("file_upload_attempted:false")
        print("chatgpt_submit_performed:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")

    if evidence.result in {
        PASS_NO_PICKER,
        PASS_ONE_PICKER_DETECTED,
        BLOCKED_AMBIGUOUS_PICKER,
        BLOCKED_PICKER_ERROR_MODAL,
        BLOCKED_LIVE_BROWSER_CONFIRMATION_MISSING,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())