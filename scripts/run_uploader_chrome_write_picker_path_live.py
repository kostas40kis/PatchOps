from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_picker_path_entry import (  # noqa: E402
    BLOCKED_CANONICAL_REPORT_MISSING,
    BLOCKED_PATH_ENTRY_CONFIRMATION_MISSING,
    BLOCKED_PATH_NOT_CANONICAL_REPORT,
    BLOCKED_PICKER_EDIT_FIELD_NOT_FOUND,
    BLOCKED_PICKER_NOT_READY,
    LIVE_CONFIRM_TEXT,
    PASS_PICKER_PATH_ENTRY_PLAN_READY,
    PASS_PICKER_PATH_WRITTEN_NO_OPEN,
    run_picker_path_entry,
    write_picker_path_entry_evidence,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write canonical PatchOps report path into an already-open Chrome picker. Stops before Open/Enter, upload, or send.")
    parser.add_argument("--canonical-report", required=True)
    parser.add_argument("--picker-ready", action="store_true")
    parser.add_argument("--picker-hwnd", type=int, default=None)
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--allow-picker-path-write", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--mock-write-success", action="store_true")
    parser.add_argument("--evidence-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    evidence = run_picker_path_entry(
        canonical_report_path=args.canonical_report,
        picker_ready=args.picker_ready,
        picker_hwnd=args.picker_hwnd,
        live_browser=args.live_browser,
        confirm_live_browser_text=args.confirm_live_browser_text,
        allow_picker_path_write=args.allow_picker_path_write,
        mock_write_success=args.mock_write_success,
    )

    if args.evidence_path:
        write_picker_path_entry_evidence(evidence, args.evidence_path)

    payload = evidence.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {evidence.result}")
        print(f"OK: {str(evidence.ok).lower()}")
        print(f"EXPECTED_BROWSER: {evidence.expected_browser}")
        print(f"PICKER_READY: {str(evidence.picker_ready).lower()}")
        print(f"LIVE_BROWSER_USED: {str(evidence.live_browser_used).lower()}")
        print(f"PATH_HASH_WRITTEN: {evidence.path_hash_written or ''}")
        print(f"BASENAME_WRITTEN: {evidence.basename_written or ''}")
        print("file_path_written:" + str(evidence.file_path_written).lower())
        print("open_button_pressed:false")
        print("enter_pressed:false")
        print("file_selected:false")
        print("file_upload_attempted:false")
        print("chatgpt_submit_performed:false")
        print("raw_conversation_text_logged:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print(f"REASON: {evidence.reason}")

    if evidence.result in {
        PASS_PICKER_PATH_ENTRY_PLAN_READY,
        PASS_PICKER_PATH_WRITTEN_NO_OPEN,
        BLOCKED_CANONICAL_REPORT_MISSING,
        BLOCKED_PATH_NOT_CANONICAL_REPORT,
        BLOCKED_PICKER_NOT_READY,
        BLOCKED_PATH_ENTRY_CONFIRMATION_MISSING,
        BLOCKED_PICKER_EDIT_FIELD_NOT_FOUND,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())