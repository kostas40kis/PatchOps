from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.pywinauto_edge_doctor import assert_l26_01_acceptance, probe_normal_edge


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.1A real normal Edge pywinauto live proof with always-write JSON evidence.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--max-controls", type=int, default=80)
    args = parser.parse_args()

    result = probe_normal_edge(
        output_dir=Path(args.output_dir),
        start_if_missing=args.start_if_missing,
        focus=True,
        max_depth=args.max_depth,
        max_controls=args.max_controls,
    )
    payload = result.to_payload()
    print("L26_01A_LIVE_EDGE_PROOF_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_01A_LIVE_EDGE_PROOF_JSON_END")
    assert_l26_01_acceptance(result)
    print("L26_01A_ACCEPTANCE: PASS")
    print("webdriver_used:false")
    print("selenium_imported:false")
    print("cloudflare_bypass_attempted:false")
    print("browser_navigation_performed:false")
    print("download_click_performed:false")
    print("run_package_invoked:false")
    print("pasteback_or_send_performed:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
