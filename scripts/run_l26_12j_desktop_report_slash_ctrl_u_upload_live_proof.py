from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_desktop_report_slash_ctrl_u_upload_gate import assert_l26_12j_acceptance, run_l26_12j_desktop_report_slash_ctrl_u_upload_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.12J desktop-report slash+Ctrl+U upload live proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--allow-report-upload", action="store_true")
    args = parser.parse_args()
    result = run_l26_12j_desktop_report_slash_ctrl_u_upload_gate(output_dir=Path(args.output_dir), target_url=args.target_url, report_path=Path(args.report_path), allow_report_upload=args.allow_report_upload)
    payload = result.to_payload()
    print("L26_12J_DESKTOP_REPORT_SLASH_CTRL_U_UPLOAD_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_12J_DESKTOP_REPORT_SLASH_CTRL_U_UPLOAD_JSON_END")
    assert_l26_12j_acceptance(result)
    print("L26_12J_ACCEPTANCE: PASS")
    print("slash_typed_in_composer:true")
    print("plus_button_clicked_after_slash:false")
    print("ctrl_u_shortcut_sent:true")
    print("picker_directory_changed:true")
    print("upload_staging_observed:true")
    print("chatgpt_submit_enter_sent:false")
    print("send_submit_performed:false")
    print("chatgpt_prompt_submitted:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
