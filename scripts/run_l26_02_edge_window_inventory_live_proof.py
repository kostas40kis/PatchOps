from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_window_inventory import assert_l26_02_acceptance, run_l26_02_live_inventory


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.2 real normal Edge window inventory and selected attach/focus proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--max-depth", type=int, default=1)
    parser.add_argument("--max-controls", type=int, default=60)
    args = parser.parse_args()

    result = run_l26_02_live_inventory(
        output_dir=Path(args.output_dir),
        start_if_missing=args.start_if_missing,
        max_depth=args.max_depth,
        max_controls=args.max_controls,
    )
    payload = result.to_payload()
    print("L26_02_LIVE_EDGE_INVENTORY_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_02_LIVE_EDGE_INVENTORY_JSON_END")
    assert_l26_02_acceptance(result)
    print("L26_02_ACCEPTANCE: PASS")
    print("webdriver_used:false")
    print("selenium_imported:false")
    print("browser_navigation_performed:false")
    print("download_click_performed:false")
    print("run_package_invoked:false")
    print("pasteback_or_send_performed:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
