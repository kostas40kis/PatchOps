from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_attachment_verifier import (  # noqa: E402
    BLOCKED_ATTACHMENT_AMBIGUOUS,
    BLOCKED_ATTACHMENT_NOT_FOUND,
    BLOCKED_ATTACHMENT_VERIFICATION_CONFIRMATION_MISSING,
    BLOCKED_LIVE_ATTACHMENT_VERIFICATION_UNSUPPORTED,
    BLOCKED_UPLOAD_NOT_ATTEMPTED,
    LIVE_CONFIRM_TEXT,
    PASS_ATTACHMENT_CONFIRMED_NO_SEND,
    PASS_ATTACHMENT_VERIFICATION_WAITING,
    build_attachment_candidate,
    verify_attachment_no_send,
    write_attachment_verification_evidence,
)
from patchops.chatgpt_uploader.chrome_picker_path_entry import (  # noqa: E402
    BLOCKED_CANONICAL_REPORT_MISSING,
    BLOCKED_PATH_NOT_CANONICAL_REPORT,
)


def _descriptor_from_arg(value: str):
    parts = value.split("|")
    while len(parts) < 6:
        parts.append("")
    return build_attachment_candidate(
        basename=parts[0],
        visible=(parts[1] or "true").strip().lower() in {"1", "true", "yes", "visible"},
        stable=(parts[2] or "true").strip().lower() in {"1", "true", "yes", "stable"},
        remove_button_visible=(parts[3] or "true").strip().lower() in {"1", "true", "yes", "remove"},
        progress_visible=(parts[4] or "false").strip().lower() in {"1", "true", "yes", "progress"},
        error_visible=(parts[5] or "false").strip().lower() in {"1", "true", "yes", "error"},
        source="cli_descriptor",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify canonical report attachment evidence while keeping ChatGPT send blocked.")
    parser.add_argument("--canonical-report", required=True)
    parser.add_argument("--upload-attempted-before-verification", action="store_true")
    parser.add_argument("--mock-attachment", action="append", default=[], help="Attachment descriptor: basename|visible|stable|remove_button_visible|progress_visible|error_visible")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--evidence-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    descriptors = [_descriptor_from_arg(item) for item in args.mock_attachment]
    evidence = verify_attachment_no_send(
        canonical_report_path=args.canonical_report,
        upload_attempted_before_verification=args.upload_attempted_before_verification,
        attachment_descriptors=descriptors,
        live_browser=args.live_browser,
        confirm_live_browser_text=args.confirm_live_browser_text,
    )

    if args.evidence_path:
        write_attachment_verification_evidence(evidence, args.evidence_path)

    payload = evidence.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {evidence.result}")
        print(f"OK: {str(evidence.ok).lower()}")
        print(f"EXPECTED_BROWSER: {evidence.expected_browser}")
        print(f"LIVE_BROWSER_USED: {str(evidence.live_browser_used).lower()}")
        print(f"UPLOAD_ATTEMPTED_BEFORE_VERIFICATION: {str(evidence.upload_attempted_before_verification).lower()}")
        print(f"EXPECTED_BASENAME: {evidence.expected_basename or ''}")
        print(f"EXPECTED_BASENAME_SHA256: {evidence.expected_basename_sha256 or ''}")
        print(f"CANDIDATE_COUNT: {evidence.candidate_count}")
        print(f"MATCHING_CANDIDATE_COUNT: {evidence.matching_candidate_count}")
        print("attachment_confirmed:" + str(evidence.attachment_confirmed).lower())
        print("send_allowed:false")
        print("chatgpt_submit_performed:false")
        print("raw_conversation_text_logged:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print(f"REASON: {evidence.reason}")

    if evidence.result in {
        PASS_ATTACHMENT_CONFIRMED_NO_SEND,
        PASS_ATTACHMENT_VERIFICATION_WAITING,
        BLOCKED_ATTACHMENT_NOT_FOUND,
        BLOCKED_ATTACHMENT_AMBIGUOUS,
        BLOCKED_UPLOAD_NOT_ATTEMPTED,
        BLOCKED_ATTACHMENT_VERIFICATION_CONFIRMATION_MISSING,
        BLOCKED_LIVE_ATTACHMENT_VERIFICATION_UNSUPPORTED,
        BLOCKED_CANONICAL_REPORT_MISSING,
        BLOCKED_PATH_NOT_CANONICAL_REPORT,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())