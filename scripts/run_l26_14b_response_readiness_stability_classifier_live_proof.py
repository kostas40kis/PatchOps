from __future__ import annotations
import argparse, json
from pathlib import Path
from patchops.edge_rpa.edge_l26_14b_response_readiness_stability_classifier import assert_acceptance, run_response_readiness_stability_classifier

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--short-live-root", required=True)
    p.add_argument("--latest-canonical-path", required=True)
    p.add_argument("--operator-report-path", required=True)
    p.add_argument("--inner-patchops-report-path", required=True)
    p.add_argument("--short-upload-dir", required=True)
    p.add_argument("--current-canonical-report-path", required=True)
    p.add_argument("--allow-report-upload", action="store_true")
    p.add_argument("--allow-chatgpt-submit", action="store_true")
    p.add_argument("--observe-seconds", type=int, default=35)
    p.add_argument("--probe-seconds", type=int, default=25)
    p.add_argument("--stability-delay-seconds", type=int, default=4)
    a = p.parse_args()
    result = run_response_readiness_stability_classifier(
        Path(a.short_live_root), Path(a.latest_canonical_path), Path(a.operator_report_path),
        Path(a.inner_patchops_report_path), Path(a.short_upload_dir), Path(a.current_canonical_report_path),
        a.allow_report_upload, a.allow_chatgpt_submit, a.observe_seconds, a.probe_seconds, a.stability_delay_seconds,
    )
    print("L26_14B_RESPONSE_READINESS_STABILITY_CLASSIFIER_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_14B_RESPONSE_READINESS_STABILITY_CLASSIFIER_JSON_END")
    assert_acceptance(result)
    print("L26_14B_ACCEPTANCE: PASS")
    print("response_ready_stable:true")
    print("candidate_click_performed:false")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
