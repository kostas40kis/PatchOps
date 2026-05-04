from __future__ import annotations
import argparse, json
from pathlib import Path
from patchops.edge_rpa.edge_l26_12t_single_patchops_report_upload import assert_acceptance, run_single_patchops_report_upload

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True)
    p.add_argument("--inner-patchops-report-path", required=True)
    p.add_argument("--operator-report-path", required=True)
    p.add_argument("--allow-report-upload", action="store_true")
    p.add_argument("--allow-chatgpt-submit", action="store_true")
    p.add_argument("--observe-seconds", type=int, default=45)
    a = p.parse_args()
    result = run_single_patchops_report_upload(
        Path(a.output_dir),
        Path(a.inner_patchops_report_path),
        Path(a.operator_report_path),
        a.allow_report_upload,
        a.allow_chatgpt_submit,
        a.observe_seconds,
    )
    print("L26_12T_SINGLE_PATCHOPS_REPORT_UPLOAD_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_12T_SINGLE_PATCHOPS_REPORT_UPLOAD_JSON_END")
    assert_acceptance(result)
    print("L26_12T_ACCEPTANCE: PASS")
    print("uploaded_report_role:inner_patchops_apply_report")
    print("uploaded_report_count:1")
    print("operator_report_uploaded:false")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
