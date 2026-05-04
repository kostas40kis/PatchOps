from __future__ import annotations
import argparse, json
from pathlib import Path
from patchops.edge_rpa.edge_l26_12r_gated_submit_fallback_gate import assert_acceptance, run_gated_submit_fallback

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True)
    p.add_argument("--report-path", required=True)
    p.add_argument("--allow-report-upload", action="store_true")
    p.add_argument("--allow-chatgpt-submit", action="store_true")
    a = p.parse_args()
    result = run_gated_submit_fallback(Path(a.output_dir), Path(a.report_path), a.allow_report_upload, a.allow_chatgpt_submit)
    print("L26_12R_GATED_SUBMIT_FALLBACK_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_12R_GATED_SUBMIT_FALLBACK_JSON_END")
    assert_acceptance(result)
    print("L26_12R_ACCEPTANCE: PASS")
    print("chatgpt_submit_performed:true")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
