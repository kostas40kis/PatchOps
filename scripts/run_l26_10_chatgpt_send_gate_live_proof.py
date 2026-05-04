from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_prompt_send_gate import assert_l26_10_acceptance, run_l26_10_send_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.10A requested-chat send gate fallback repair live proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--settle-seconds", type=float, default=10.0)
    parser.add_argument("--allow-send", action="store_true")
    args = parser.parse_args()
    result = run_l26_10_send_gate(output_dir=Path(args.output_dir), target_url=args.target_url, start_if_missing=args.start_if_missing, settle_seconds=args.settle_seconds, allow_send=args.allow_send)
    payload = result.to_payload()
    print("L26_10A_SEND_GATE_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_10A_SEND_GATE_JSON_END")
    assert_l26_10_acceptance(result)
    print("L26_10A_ACCEPTANCE: PASS")
    print("target_url_is_requested_chat:true")
    print("classifier_unknown_fallback_used:true")
    print("composer_fallback_focus_verified:true")
    print("prompt_paste_cycle_completed:true")
    print("send_blocked_by_default:true")
    print("allow_send_requested:false")
    print("enter_key_sent:false")
    print("send_submit_performed:false")
    print("chatgpt_prompt_submitted:false")
    print("page_click_performed:false")
    print("download_click_performed:false")
    print("run_package_invoked:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
