from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_evidence_bundle import (  # noqa: E402
    BLOCKED_EVIDENCE_BUNDLE_INVALID_JSON,
    BLOCKED_EVIDENCE_BUNDLE_MISSING,
    BLOCKED_EVIDENCE_BUNDLE_UNRECOGNIZED_RESULT,
    BLOCKED_EVIDENCE_BUNDLE_UNSAFE,
    PASS_EVIDENCE_BUNDLE_SUMMARY_WRITTEN,
    PASS_EVIDENCE_BUNDLE_VALIDATED,
    load_and_validate_flow_evidence,
    write_evidence_bundle,
    write_evidence_summary_text,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Chrome upload flow evidence and write a compact operator-safe summary.")
    parser.add_argument("--flow-evidence", required=True)
    parser.add_argument("--bundle-json", default=None)
    parser.add_argument("--summary-txt", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    bundle = load_and_validate_flow_evidence(args.flow_evidence)

    if args.bundle_json:
        write_evidence_bundle(bundle, args.bundle_json)
    if args.summary_txt:
        write_evidence_summary_text(bundle, args.summary_txt)

    payload = bundle.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {bundle.result}")
        print(f"OK: {str(bundle.ok).lower()}")
        print(f"FLOW_RESULT: {bundle.flow_result or ''}")
        print(f"FLOW_OK: {str(bundle.flow_ok).lower()}")
        print(f"EVIDENCE_BASENAME: {bundle.evidence_basename or ''}")
        print(f"EVIDENCE_SHA256: {bundle.evidence_path_hash or ''}")
        print(f"CANONICAL_REPORT: {bundle.canonical_report_basename or ''}")
        print(f"ATTACHMENT_CONFIRMED: {str(bundle.attachment_confirmed).lower()}")
        print(f"SEND_GATE_READY: {str(bundle.send_gate_ready).lower()}")
        print(f"SUBMIT_ADAPTER_READY: {str(bundle.submit_adapter_ready).lower()}")
        print(f"SUBMIT_ACTION_PERFORMED: {str(bundle.submit_action_performed).lower()}")
        print(f"CHATGPT_SUBMIT_PERFORMED: {str(bundle.chatgpt_submit_performed).lower()}")
        print("raw_conversation_text_logged:false")
        print("conversation_text_logged:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print(f"REASON: {bundle.reason}")

    if bundle.result in {
        PASS_EVIDENCE_BUNDLE_VALIDATED,
        PASS_EVIDENCE_BUNDLE_SUMMARY_WRITTEN,
        BLOCKED_EVIDENCE_BUNDLE_INVALID_JSON,
        BLOCKED_EVIDENCE_BUNDLE_MISSING,
        BLOCKED_EVIDENCE_BUNDLE_UNSAFE,
        BLOCKED_EVIDENCE_BUNDLE_UNRECOGNIZED_RESULT,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())