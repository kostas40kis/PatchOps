from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_local_desktop_fullpath_upload_gate import assert_l26_12l_acceptance, run_l26_12l_local_desktop_fullpath_upload_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.12L local Desktop full-path picker upload live proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--allow-report-upload", action="store_true")
    args = parser.parse_args()
    result = run_l26_12l_local_desktop_fullpath_upload_gate(output_dir=Path(args.output_dir), report_path=Path(args.report_path), allow_report_upload=args.allow_report_upload)
    payload = result.to_payload()
    print("L26_12L_LOCAL_DESKTOP_FULLPATH_UPLOAD_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_12L_LOCAL_DESKTOP_FULLPATH_UPLOAD_JSON_END")
    assert_l26_12l_acceptance(result)
    print("L26_12L_ACCEPTANCE: PASS")
    print("local_desktop_report_path_used:true")
    print("picker_ctrl_l_used:false")
    print("safe_copy_full_path_had_lc_prefix:false")
    print("picker_full_path_entry_attempted:true")
    print("upload_staging_observed:true")
    print("chatgpt_submit_enter_sent:false")
    print("send_submit_performed:false")
    print("chatgpt_prompt_submitted:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
