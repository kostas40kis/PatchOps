from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_composer_focus_probe import assert_l26_07_acceptance, run_l26_07_focus_probe


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.7 ChatGPT composer focus-only live proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--settle-seconds", type=float, default=8.0)
    args = parser.parse_args()

    result = run_l26_07_focus_probe(output_dir=Path(args.output_dir), target_url=args.target_url, start_if_missing=args.start_if_missing, settle_seconds=args.settle_seconds)
    payload = result.to_payload()
    print("L26_07_COMPOSER_FOCUS_PROBE_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_07_COMPOSER_FOCUS_PROBE_JSON_END")
    assert_l26_07_acceptance(result)
    print("L26_07_ACCEPTANCE: PASS")
    print("composer_focus_attempted:true")
    print("focus_call_succeeded:true")
    print("composer_focus_verified:true")
    print("chatgpt_prompt_submitted:false")
    print("prompt_text_entered:false")
    print("keyboard_text_sent:false")
    print("clipboard_prompt_set:false")
    print("page_click_performed:false")
    print("download_click_performed:false")
    print("run_package_invoked:false")
    print("pasteback_or_send_performed:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
