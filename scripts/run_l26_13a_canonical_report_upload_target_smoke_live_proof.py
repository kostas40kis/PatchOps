from __future__ import annotations
import argparse, json
from pathlib import Path
from patchops.edge_rpa.edge_l26_13a_canonical_report_upload_target_smoke import assert_acceptance, run_canonical_report_upload_target_smoke

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--short-live-root", required=True)
    p.add_argument("--canonical-upload-source-path", required=True)
    p.add_argument("--operator-report-path", required=True)
    p.add_argument("--inner-patchops-report-path", required=True)
    p.add_argument("--short-upload-dir", required=True)
    p.add_argument("--allow-report-upload", action="store_true")
    p.add_argument("--allow-chatgpt-submit", action="store_true")
    p.add_argument("--observe-seconds", type=int, default=35)
    a = p.parse_args()
    result = run_canonical_report_upload_target_smoke(
        Path(a.short_live_root), Path(a.canonical_upload_source_path), Path(a.operator_report_path), Path(a.inner_patchops_report_path),
        Path(a.short_upload_dir), a.allow_report_upload, a.allow_chatgpt_submit, a.observe_seconds,
    )
    print("L26_13A_CANONICAL_REPORT_UPLOAD_TARGET_SMOKE_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_13A_CANONICAL_REPORT_UPLOAD_TARGET_SMOKE_JSON_END")
    assert_acceptance(result)
    print("L26_13A_ACCEPTANCE: PASS")
    print("uploaded_report_role:canonical_browser_evidence_report")
    print("raw_apply_report_uploaded_as_browser_target:false")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
