from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_report_upload_staging_gate import assert_l26_12_acceptance, run_l26_12_report_upload_staging_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.12 report upload staging gate live proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--settle-seconds", type=float, default=10.0)
    parser.add_argument("--allow-report-upload", action="store_true")
    args = parser.parse_args()
    result = run_l26_12_report_upload_staging_gate(output_dir=Path(args.output_dir), target_url=args.target_url, start_if_missing=args.start_if_missing, settle_seconds=args.settle_seconds, allow_report_upload=args.allow_report_upload)
    payload = result.to_payload()
    print("L26_12_REPORT_UPLOAD_STAGING_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_12_REPORT_UPLOAD_STAGING_JSON_END")
    assert_l26_12_acceptance(result)
    print("L26_12_ACCEPTANCE: PASS")
    print("report_upload_attempted:true")
    print("file_attach_attempted:true")
    print("attach_button_clicked:true")
    print("file_picker_opened:true")
    print("upload_staging_observed:true")
    print("enter_key_sent:false")
    print("send_submit_performed:false")
    print("chatgpt_prompt_submitted:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
