from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_navigation_proof import assert_l26_04_acceptance, run_l26_04_navigation_proof


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.4 controlled normal Edge navigation proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--settle-seconds", type=float, default=8.0)
    args = parser.parse_args()

    result = run_l26_04_navigation_proof(
        output_dir=Path(args.output_dir),
        target_url=args.target_url,
        start_if_missing=args.start_if_missing,
        settle_seconds=args.settle_seconds,
    )
    payload = result.to_payload()
    print("L26_04_LIVE_EDGE_NAVIGATION_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_04_LIVE_EDGE_NAVIGATION_JSON_END")
    assert_l26_04_acceptance(result)
    print("L26_04_ACCEPTANCE: PASS")
    print("ctrl_l_sent:true")
    print("url_pasted_by_patchops:true")
    print("enter_sent:true")
    print("normal_edge_navigation:true")
    print("page_load_state_observed:true")
    print("cloudflare_bypass_attempted:false")
    print("chatgpt_prompt_submitted:false")
    print("download_click_performed:false")
    print("run_package_invoked:false")
    print("pasteback_or_send_performed:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
