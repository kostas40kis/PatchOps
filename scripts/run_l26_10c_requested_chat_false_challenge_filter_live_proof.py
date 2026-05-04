from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_requested_chat_false_challenge_filter import assert_l26_10c_acceptance, run_l26_10c_false_challenge_filter_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.10C requested-chat false-positive challenge filter send-disabled proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--settle-seconds", type=float, default=10.0)
    parser.add_argument("--allow-send", action="store_true")
    args = parser.parse_args()
    result = run_l26_10c_false_challenge_filter_gate(output_dir=Path(args.output_dir), target_url=args.target_url, start_if_missing=args.start_if_missing, settle_seconds=args.settle_seconds, allow_send=args.allow_send)
    payload = result.to_payload()
    print("L26_10C_FALSE_CHALLENGE_FILTER_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_10C_FALSE_CHALLENGE_FILTER_JSON_END")
    assert_l26_10c_acceptance(result)
    print("L26_10C_ACCEPTANCE: PASS")
    print("transcript_challenge_terms_filtered:true")
    print("real_challenge_indicator_found:false")
    print("requested_chat_accessible_by_composer:true")
    print("prompt_paste_cycle_completed:true")
    print("send_blocked_by_default:true")
    print("report_upload_attempted:false")
    print("file_attach_attempted:false")
    print("enter_key_sent:false")
    print("send_submit_performed:false")
    print("chatgpt_prompt_submitted:false")
    print("page_click_performed:false")
    print("download_click_performed:false")
    print("run_package_invoked:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
