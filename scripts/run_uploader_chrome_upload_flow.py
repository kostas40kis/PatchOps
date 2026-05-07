from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.chrome_upload_orchestrator import (  # noqa: E402
    BLOCKED_UPLOAD_FLOW_ATTACHMENT,
    BLOCKED_UPLOAD_FLOW_SEND_GATE,
    BLOCKED_UPLOAD_FLOW_SUBMIT_ACTION,
    BLOCKED_UPLOAD_FLOW_SUBMIT_ADAPTER,
    PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT,
    PASS_CHROME_UPLOAD_FLOW_SUBMIT_MOCKED,
    PASS_CHROME_UPLOAD_FLOW_SUBMIT_PERFORMED,
    build_attachment_descriptor,
    run_chrome_upload_flow,
    write_chrome_upload_flow_evidence,
)


def _descriptor_from_arg(value: str):
    parts = value.split("|")
    while len(parts) < 6:
        parts.append("")
    return build_attachment_descriptor(
        basename=parts[0],
        visible=(parts[1] or "true").strip().lower() in {"1", "true", "yes", "visible"},
        stable=(parts[2] or "true").strip().lower() in {"1", "true", "yes", "stable"},
        remove_button_visible=(parts[3] or "true").strip().lower() in {"1", "true", "yes", "remove"},
        progress_visible=(parts[4] or "false").strip().lower() in {"1", "true", "yes", "progress"},
        error_visible=(parts[5] or "false").strip().lower() in {"1", "true", "yes", "error"},
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chrome-only upload flow orchestrator. Composes attachment, send-gate, submit-adapter, and optional gated submit evidence.")
    parser.add_argument("--canonical-report", required=True)
    parser.add_argument("--mock-attachment", action="append", default=[], help="Attachment descriptor: basename|visible|stable|remove_button_visible|progress_visible|error_visible")
    parser.add_argument("--upload-attempted-before-verification", action="store_true")
    parser.add_argument("--submit-action-requested", action="store_true")
    parser.add_argument("--submit-backend", default="ctrl_enter_once")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--submit-confirm-text", default=None)
    parser.add_argument("--target-hwnd", type=int, default=None)
    parser.add_argument("--allow-submit-action", action="store_true")
    parser.add_argument("--mock-submit-success", action="store_true")
    parser.add_argument("--flow-evidence-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    descriptors = [_descriptor_from_arg(item) for item in args.mock_attachment]
    evidence = run_chrome_upload_flow(
        canonical_report_path=args.canonical_report,
        upload_attempted_before_verification=args.upload_attempted_before_verification,
        attachment_descriptors=descriptors,
        submit_action_requested=args.submit_action_requested,
        submit_backend=args.submit_backend,
        live_browser=args.live_browser,
        submit_confirm_text=args.submit_confirm_text,
        target_hwnd=args.target_hwnd,
        allow_submit_action=args.allow_submit_action,
        mock_submit_success=args.mock_submit_success,
    )

    if args.flow_evidence_path:
        write_chrome_upload_flow_evidence(evidence, args.flow_evidence_path)

    payload = evidence.to_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"RESULT: {evidence.result}")
        print(f"OK: {str(evidence.ok).lower()}")
        print(f"EXPECTED_BROWSER: {evidence.expected_browser}")
        print(f"ATTACHMENT_RESULT: {evidence.attachment_result or ''}")
        print(f"SEND_GATE_RESULT: {evidence.send_gate_result or ''}")
        print(f"SUBMIT_ADAPTER_RESULT: {evidence.submit_adapter_result or ''}")
        print(f"SUBMIT_ACTION_RESULT: {evidence.submit_action_result or ''}")
        print(f"ATTACHMENT_CONFIRMED: {str(evidence.attachment_confirmed).lower()}")
        print(f"SEND_GATE_READY: {str(evidence.send_gate_ready).lower()}")
        print(f"SUBMIT_ADAPTER_READY: {str(evidence.submit_adapter_ready).lower()}")
        print(f"SUBMIT_ACTION_REQUESTED: {str(evidence.submit_action_requested).lower()}")
        print("submit_action_performed:" + str(evidence.submit_action_performed).lower())
        print("chatgpt_submit_performed:" + str(evidence.chatgpt_submit_performed).lower())
        print("send_button_pressed:false")
        print("raw_conversation_text_logged:false")
        print("conversation_text_logged:false")
        print("selenium_used:false")
        print("webdriver_used:false")
        print("browser_dom_automation_used:false")
        print(f"REASON: {evidence.reason}")

    if evidence.result in {
        PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT,
        PASS_CHROME_UPLOAD_FLOW_SUBMIT_MOCKED,
        PASS_CHROME_UPLOAD_FLOW_SUBMIT_PERFORMED,
        BLOCKED_UPLOAD_FLOW_ATTACHMENT,
        BLOCKED_UPLOAD_FLOW_SEND_GATE,
        BLOCKED_UPLOAD_FLOW_SUBMIT_ADAPTER,
        BLOCKED_UPLOAD_FLOW_SUBMIT_ACTION,
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())