from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_prompt_paste_gate import assert_l26_09_acceptance, run_l26_09_prompt_paste_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.9 ChatGPT prompt-builder paste gate live proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--settle-seconds", type=float, default=8.0)
    parser.add_argument("--allow-paste", action="store_true")
    args = parser.parse_args()

    result = run_l26_09_prompt_paste_gate(output_dir=Path(args.output_dir), target_url=args.target_url, start_if_missing=args.start_if_missing, settle_seconds=args.settle_seconds, allow_paste=args.allow_paste)
    payload = result.to_payload()
    print("L26_09_PROMPT_PASTE_GATE_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_09_PROMPT_PASTE_GATE_JSON_END")
    assert_l26_09_acceptance(result)
    print("L26_09_ACCEPTANCE: PASS")
    print("prompt_pasted:true")
    print("prompt_observed_by_copyback:true")
    print("copyback_hash_matches_prompt:true")
    print("prompt_cleared:true")
    print("prompt_text_logged:false")
    print("enter_key_sent:false")
    print("send_submit_performed:false")
    print("chatgpt_prompt_submitted:false")
    print("page_click_performed:false")
    print("download_click_performed:false")
    print("run_package_invoked:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
