from __future__ import annotations
import argparse, json
from pathlib import Path
from patchops.edge_rpa.edge_l26_14g_seeded_picker_bridge_canonical_cycle import assert_acceptance, run_seeded_picker_bridge_canonical_cycle

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--short-live-root", required=True)
    p.add_argument("--latest-canonical-path", required=True)
    p.add_argument("--operator-report-path", required=True)
    p.add_argument("--inner-patchops-report-path", required=True)
    p.add_argument("--primary-bridge-dir", required=True)
    p.add_argument("--bridge-dir", action="append", default=[])
    p.add_argument("--current-canonical-report-path", required=True)
    p.add_argument("--allow-report-upload", action="store_true")
    p.add_argument("--allow-chatgpt-submit", action="store_true")
    p.add_argument("--observe-seconds", type=int, default=35)
    p.add_argument("--probe-seconds", type=int, default=25)
    p.add_argument("--stability-delay-seconds", type=int, default=4)
    p.add_argument("--attachment-verify-seconds", type=int, default=18)
    a = p.parse_args()
    result = run_seeded_picker_bridge_canonical_cycle(
        Path(a.short_live_root), Path(a.latest_canonical_path), Path(a.operator_report_path), Path(a.inner_patchops_report_path),
        Path(a.primary_bridge_dir), [Path(x) for x in a.bridge_dir], Path(a.current_canonical_report_path),
        a.allow_report_upload, a.allow_chatgpt_submit, a.observe_seconds, a.probe_seconds, a.stability_delay_seconds, a.attachment_verify_seconds,
    )
    print("L26_14G_SEEDED_PICKER_BRIDGE_CANONICAL_CYCLE_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_14G_SEEDED_PICKER_BRIDGE_CANONICAL_CYCLE_JSON_END")
    assert_acceptance(result)
    print("L26_14G_ACCEPTANCE: PASS")
    print("visible_attachment_gate_passed:true")
    print("latest_canonical_matches_current:true")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
