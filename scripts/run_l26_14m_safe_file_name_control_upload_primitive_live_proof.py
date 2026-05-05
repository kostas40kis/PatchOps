from __future__ import annotations
import argparse, json
from pathlib import Path
from patchops.edge_rpa.edge_l26_14m_safe_file_name_control_upload_primitive import assert_acceptance, run_safe_file_name_control_upload_primitive

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--short-live-root", required=True)
    p.add_argument("--latest-canonical-path", required=True)
    p.add_argument("--desktop-path", required=True)
    p.add_argument("--upload-bridge-dir", required=True)
    p.add_argument("--dialog-open-seconds", type=int, default=15)
    p.add_argument("--attachment-probe-seconds", type=int, default=40)
    a = p.parse_args()
    result = run_safe_file_name_control_upload_primitive(
        Path(a.short_live_root), Path(a.latest_canonical_path), Path(a.desktop_path), Path(a.upload_bridge_dir),
        a.dialog_open_seconds, a.attachment_probe_seconds,
    )
    print("L26_14M_SAFE_FILE_NAME_CONTROL_UPLOAD_PRIMITIVE_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_14M_SAFE_FILE_NAME_CONTROL_UPLOAD_PRIMITIVE_JSON_END")
    assert_acceptance(result)
    print("L26_14M_ACCEPTANCE: PASS")
    print("upload_primitive_reliable:true")
    print("global_ctrl_a_sent:false")
    print("chatgpt_submit_performed:false")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
