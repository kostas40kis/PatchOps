from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_l26_12o_upload_only_gate import assert_acceptance, run_upload_only


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--allow-report-upload", action="store_true")
    args = parser.parse_args()
    result = run_upload_only(Path(args.output_dir), Path(args.report_path), args.allow_report_upload)
    print("L26_12O_UPLOAD_ONLY_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_12O_UPLOAD_ONLY_JSON_END")
    assert_acceptance(result)
    print("L26_12O_ACCEPTANCE: PASS")
    print("upload_staging_observed:true")
    print("slash_leftover_tolerated:true")
    print("cleanup_attempted:false")
    print("chatgpt_submit_enter_sent:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
