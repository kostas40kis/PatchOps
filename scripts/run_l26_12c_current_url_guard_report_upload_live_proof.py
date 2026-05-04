from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_current_url_guard_report_upload_gate import assert_l26_12c_acceptance, run_l26_12c_current_url_guard_upload_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.12C current-URL guard report upload staging repair live proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--settle-seconds", type=float, default=10.0)
    parser.add_argument("--allow-report-upload", action="store_true")
    args = parser.parse_args()
    result = run_l26_12c_current_url_guard_upload_gate(output_dir=Path(args.output_dir), target_url=args.target_url, start_if_missing=args.start_if_missing, settle_seconds=args.settle_seconds, allow_report_upload=args.allow_report_upload)
    payload = result.to_payload()
    print("L26_12C_CURRENT_URL_GUARD_UPLOAD_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_12C_CURRENT_URL_GUARD_UPLOAD_JSON_END")
    assert_l26_12c_acceptance(result)
    print("L26_12C_ACCEPTANCE: PASS")
    print("current_url_matches_target:true")
    print("navigation_skipped_existing_target:true")
    print("navigation_attempted:false")
    print("composer_focus_verified:true")
    print("upload_menu_item_clicked:true")
    print("upload_staging_observed:true")
    print("chatgpt_enter_key_sent:false")
    print("send_submit_performed:false")
    print("chatgpt_prompt_submitted:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
