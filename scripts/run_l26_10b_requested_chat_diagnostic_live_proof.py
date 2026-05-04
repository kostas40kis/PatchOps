from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_requested_chat_diagnostic import assert_l26_10b_acceptance, run_l26_10b_requested_chat_diagnostic


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.10B requested-chat targeting diagnostic repair live proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--settle-seconds", type=float, default=12.0)
    parser.add_argument("--max-depth", type=int, default=16)
    parser.add_argument("--max-controls", type=int, default=1400)
    args = parser.parse_args()
    result = run_l26_10b_requested_chat_diagnostic(
        output_dir=Path(args.output_dir),
        target_url=args.target_url,
        start_if_missing=args.start_if_missing,
        settle_seconds=args.settle_seconds,
        max_depth=args.max_depth,
        max_controls=args.max_controls,
    )
    payload = result.to_payload()
    print("L26_10B_REQUESTED_CHAT_DIAGNOSTIC_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_10B_REQUESTED_CHAT_DIAGNOSTIC_JSON_END")
    assert_l26_10b_acceptance(result)
    print("L26_10B_ACCEPTANCE: PASS")
    print("target_url_is_requested_chat:true")
    print("diagnostic_completed:true")
    print(f"diagnostic_classification:{result.diagnostic_classification}")
    print(f"recommended_next_patch:{result.recommended_next_patch}")
    print("report_upload_attempted:false")
    print("file_attach_attempted:false")
    print("prompt_pasted:false")
    print("enter_key_sent:false")
    print("chatgpt_prompt_submitted:false")
    print("page_click_performed:false")
    print("download_click_performed:false")
    print("run_package_invoked:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
