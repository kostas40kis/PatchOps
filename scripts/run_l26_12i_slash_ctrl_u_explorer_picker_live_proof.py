from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_slash_ctrl_u_explorer_picker_gate import assert_l26_12i_acceptance, run_l26_12i_slash_ctrl_u_explorer_picker_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.12I slash-primed Ctrl+U Explorer picker live proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--settle-seconds", type=float, default=10.0)
    parser.add_argument("--allow-report-upload", action="store_true")
    args = parser.parse_args()
    result = run_l26_12i_slash_ctrl_u_explorer_picker_gate(output_dir=Path(args.output_dir), target_url=args.target_url, start_if_missing=args.start_if_missing, settle_seconds=args.settle_seconds, allow_report_upload=args.allow_report_upload)
    payload = result.to_payload()
    print("L26_12I_SLASH_CTRL_U_EXPLORER_PICKER_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_12I_SLASH_CTRL_U_EXPLORER_PICKER_JSON_END")
    assert_l26_12i_acceptance(result)
    print("L26_12I_ACCEPTANCE: PASS")
    print("slash_typed_in_composer:true")
    print("ctrl_u_shortcut_sent:true")
    print("picker_window_detected:true")
    print("upload_staging_observed:true")
    print("chatgpt_submit_enter_sent:false")
    print("send_submit_performed:false")
    print("chatgpt_prompt_submitted:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
