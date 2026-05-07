from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_repeatability_acceptance import (  # noqa: E402
    BLOCKED_ACCEPTANCE_FORBIDDEN_FLAGS,
    BLOCKED_ACCEPTANCE_INVALID_BUNDLE,
    BLOCKED_ACCEPTANCE_MISSING_BUNDLE,
    BLOCKED_ACCEPTANCE_NOT_ENOUGH_ATTEMPTS,
    BLOCKED_ACCEPTANCE_SUBMIT_DETECTED,
    BLOCKED_ACCEPTANCE_TOO_FEW_PASSES,
    DEFAULT_MIN_ATTEMPTS,
    DEFAULT_MIN_PASSES,
    PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND,
    collect_bundle_paths,
    evaluate_repeatability_acceptance,
    load_bundle_attempts,
    write_acceptance_json,
    write_acceptance_marker,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chrome-only repeatability acceptance gate for no-send upload evidence bundles.")
    parser.add_argument("--evidence-bundle", action="append", default=[], help="Path to a chrome_evidence_bundle JSON file. Provide at least five, or use --evidence-dir.")
    parser.add_argument("--evidence-dir", default=None, help="Directory containing chrome_evidence_bundle JSON files.")
    parser.add_argument("--min-attempts", type=int, default=DEFAULT_MIN_ATTEMPTS)
    parser.add_argument("--min-passes", type=int, default=DEFAULT_MIN_PASSES)
    parser.add_argument("--acceptance-json", default=None)
    parser.add_argument("--acceptance-marker", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    paths = collect_bundle_paths(explicit_paths=args.evidence_bundle, evidence_dir=args.evidence_dir)
    attempts = load_bundle_attempts(paths)
    acceptance = evaluate_repeatability_acceptance(attempts, min_attempts=args.min_attempts, min_passes=args.min_passes)

    if args.acceptance_json:
        write_acceptance_json(acceptance, args.acceptance_json)
    if args.acceptance_marker:
        write_acceptance_marker(acceptance, args.acceptance_marker)

    payload = acceptance.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {acceptance.result}")
        print(f"OK: {str(acceptance.ok).lower()}")
        print(f"EXPECTED_BROWSER: {acceptance.expected_browser}")
        print(f"ATTEMPT_COUNT: {acceptance.attempt_count}")
        print(f"MIN_ATTEMPTS: {acceptance.min_attempts}")
        print(f"PASS_COUNT: {acceptance.pass_count}")
        print(f"MIN_PASSES: {acceptance.min_passes}")
        print(f"FAILED_ATTEMPT_COUNT: {acceptance.failed_attempt_count}")
        print(f"CHATGPT_SUBMIT_DETECTED: {str(acceptance.chatgpt_submit_detected).lower()}")
        print(f"FORBIDDEN_TRUE_FLAGS: {','.join(acceptance.forbidden_true_flags)}")
        print("chrome_executable_found:" + str(acceptance.chrome_executable_found).lower())
        print("chrome_target_ready:" + str(acceptance.chrome_target_ready).lower())
        print("canonical_report_found:" + str(acceptance.canonical_report_found).lower())
        print("picker_opened:" + str(acceptance.picker_opened).lower())
        print("exact_path_written:" + str(acceptance.exact_path_written).lower())
        print("file_upload_attempted:" + str(acceptance.file_upload_attempted).lower())
        print("attachment_verified:" + str(acceptance.attachment_verified).lower())
        print("chatgpt_submit_performed:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print("cloudflare_bypass_attempted:false")
        print("captcha_bypass_attempted:false")
        print("conversation_text_logged:false")
        print("raw_conversation_text_logged:false")
        print("random_page_click_performed:false")
        print(f"REASON: {acceptance.reason}")

    if acceptance.result in {
        PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND,
        BLOCKED_ACCEPTANCE_NOT_ENOUGH_ATTEMPTS,
        BLOCKED_ACCEPTANCE_TOO_FEW_PASSES,
        BLOCKED_ACCEPTANCE_FORBIDDEN_FLAGS,
        BLOCKED_ACCEPTANCE_SUBMIT_DETECTED,
        BLOCKED_ACCEPTANCE_INVALID_BUNDLE,
        BLOCKED_ACCEPTANCE_MISSING_BUNDLE,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())