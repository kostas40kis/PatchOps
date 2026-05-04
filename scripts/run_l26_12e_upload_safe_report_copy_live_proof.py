from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_upload_safe_report_copy_gate import assert_l26_12e_acceptance, run_l26_12e_upload_safe_copy_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.12E upload-safe report copy strict menu repair live proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--settle-seconds", type=float, default=10.0)
    parser.add_argument("--allow-report-upload", action="store_true")
    args = parser.parse_args()
    result = run_l26_12e_upload_safe_copy_gate(output_dir=Path(args.output_dir), target_url=args.target_url, start_if_missing=args.start_if_missing, settle_seconds=args.settle_seconds, allow_report_upload=args.allow_report_upload)
    payload = result.to_payload()
    print("L26_12E_UPLOAD_SAFE_COPY_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_12E_UPLOAD_SAFE_COPY_JSON_END")
    assert_l26_12e_acceptance(result)
    print("L26_12E_ACCEPTANCE: PASS")
    print("upload_safe_copy_created:true")
    print("upload_safe_copy_closed:true")
    print("safe_copy_outside_onedrive:true")
    print("onedrive_status_candidate_rejected:true")
    print("file_picker_opened:true")
    print("upload_staging_observed:true")
    print("chatgpt_enter_key_sent:false")
    print("send_submit_performed:false")
    print("chatgpt_prompt_submitted:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
