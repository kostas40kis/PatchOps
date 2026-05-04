from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_l26_12m_upload_gate import assert_acceptance, run_upload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--allow-report-upload", action="store_true")
    args = parser.parse_args()
    result = run_upload(Path(args.output_dir), Path(args.report_path), args.allow_report_upload)
    print("L26_12M_UPLOAD_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_12M_UPLOAD_JSON_END")
    assert_acceptance(result)
    print("L26_12M_ACCEPTANCE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
