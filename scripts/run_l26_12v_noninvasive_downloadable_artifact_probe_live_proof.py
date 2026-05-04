from __future__ import annotations
import argparse, json
from pathlib import Path
from patchops.edge_rpa.edge_l26_12v_noninvasive_downloadable_artifact_probe import assert_acceptance, run_noninvasive_artifact_probe

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True)
    p.add_argument("--inner-patchops-report-path", required=True)
    p.add_argument("--operator-report-path", required=True)
    p.add_argument("--short-upload-dir", required=True)
    p.add_argument("--allow-report-upload", action="store_true")
    p.add_argument("--allow-chatgpt-submit", action="store_true")
    p.add_argument("--observe-seconds", type=int, default=45)
    p.add_argument("--probe-seconds", type=int, default=20)
    a = p.parse_args()
    result = run_noninvasive_artifact_probe(
        Path(a.output_dir), Path(a.inner_patchops_report_path), Path(a.operator_report_path), Path(a.short_upload_dir),
        a.allow_report_upload, a.allow_chatgpt_submit, a.observe_seconds, a.probe_seconds,
    )
    print("L26_12V_NONINVASIVE_DOWNLOADABLE_ARTIFACT_PROBE_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_12V_NONINVASIVE_DOWNLOADABLE_ARTIFACT_PROBE_JSON_END")
    assert_acceptance(result)
    print("L26_12V_ACCEPTANCE: PASS")
    print("artifact_probe_completed:true")
    print("download_click_performed:false")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
