from __future__ import annotations
import argparse, json
from pathlib import Path
from patchops.edge_rpa.edge_l26_14j_upload_primitive_diagnostic_freeze import assert_acceptance, run_upload_primitive_diagnostic_freeze

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--short-live-root", required=True)
    p.add_argument("--latest-canonical-path", required=True)
    p.add_argument("--desktop-path", required=True)
    p.add_argument("--upload-bridge-dir", required=True)
    p.add_argument("--upload-probe-seconds", type=int, default=30)
    p.add_argument("--picker-wait-seconds", type=int, default=12)
    a = p.parse_args()
    result = run_upload_primitive_diagnostic_freeze(
        Path(a.short_live_root), Path(a.latest_canonical_path), Path(a.desktop_path), Path(a.upload_bridge_dir),
        a.upload_probe_seconds, a.picker_wait_seconds,
    )
    print("L26_14J_UPLOAD_PRIMITIVE_DIAGNOSTIC_FREEZE_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_14J_UPLOAD_PRIMITIVE_DIAGNOSTIC_FREEZE_JSON_END")
    assert_acceptance(result)
    print("L26_14J_ACCEPTANCE: PASS")
    print("upload_primitive_reliable:true")
    print("chatgpt_submit_performed:false")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
