from __future__ import annotations
import argparse, json
from pathlib import Path
from patchops.edge_rpa.edge_l26_13d_stable_latest_canonical_second_cycle import assert_acceptance, run_stable_latest_canonical_second_cycle

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
    a = p.parse_args()
    result = run_stable_latest_canonical_second_cycle(
        Path(a.short_live_root), Path(a.latest_canonical_path), Path(a.operator_report_path),
        Path(a.inner_patchops_report_path), Path(a.short_upload_dir), Path(a.current_canonical_report_path),
        a.allow_report_upload, a.allow_chatgpt_submit, a.observe_seconds,
    )
    print("L26_13D_STABLE_LATEST_CANONICAL_SECOND_CYCLE_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_13D_STABLE_LATEST_CANONICAL_SECOND_CYCLE_JSON_END")
    assert_acceptance(result)
    print("L26_13D_ACCEPTANCE: PASS")
    print("second_cycle_confirmed:true")
    print("latest_hash_changed_after_publish:true")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
