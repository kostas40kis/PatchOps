from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_composer_dry_run_text_gate import assert_l26_08_acceptance, run_l26_08_dry_run_text_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.8 ChatGPT composer dry-run text gate live proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--settle-seconds", type=float, default=8.0)
    args = parser.parse_args()

    result = run_l26_08_dry_run_text_gate(output_dir=Path(args.output_dir), target_url=args.target_url, start_if_missing=args.start_if_missing, settle_seconds=args.settle_seconds)
    payload = result.to_payload()
    print("L26_08_DRY_RUN_TEXT_GATE_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_08_DRY_RUN_TEXT_GATE_JSON_END")
    assert_l26_08_acceptance(result)
    print("L26_08_ACCEPTANCE: PASS")
    print("dry_run_text_observed:true")
    print("dry_run_text_cleared:true")
    print("enter_key_sent:false")
    print("chatgpt_prompt_submitted:false")
    print("page_click_performed:false")
    print("download_click_performed:false")
    print("run_package_invoked:false")
    print("pasteback_or_send_performed:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
