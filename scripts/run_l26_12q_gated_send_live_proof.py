from __future__ import annotations
import argparse, json
from pathlib import Path
from patchops.edge_rpa.edge_l26_12q_gated_send_gate import assert_acceptance, run_gated_send

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True)
    p.add_argument("--report-path", required=True)
    p.add_argument("--allow-report-upload", action="store_true")
    p.add_argument("--allow-chatgpt-submit", action="store_true")
    a = p.parse_args()
    result = run_gated_send(Path(a.output_dir), Path(a.report_path), a.allow_report_upload, a.allow_chatgpt_submit)
    print("L26_12Q_GATED_SEND_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_12Q_GATED_SEND_JSON_END")
    assert_acceptance(result)
    print("L26_12Q_ACCEPTANCE: PASS")
    print("chatgpt_submit_performed:true")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
