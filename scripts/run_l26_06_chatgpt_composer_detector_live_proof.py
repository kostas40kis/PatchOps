from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_composer_detector import assert_l26_06_acceptance, run_l26_06_composer_detector


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.6B in-page ChatGPT composer detector repair live proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--settle-seconds", type=float, default=8.0)
    parser.add_argument("--max-depth", type=int, default=14)
    parser.add_argument("--max-controls", type=int, default=900)
    args = parser.parse_args()

    result = run_l26_06_composer_detector(output_dir=Path(args.output_dir), target_url=args.target_url, start_if_missing=args.start_if_missing, settle_seconds=args.settle_seconds, max_depth=args.max_depth, max_controls=args.max_controls)
    payload = result.to_payload()
    print("L26_06B_IN_PAGE_COMPOSER_DETECTOR_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_06B_IN_PAGE_COMPOSER_DETECTOR_JSON_END")
    assert_l26_06_acceptance(result)
    print("L26_06B_ACCEPTANCE: PASS")
    print("browser_chrome_candidates_filtered:true")
    print(f"browser_chrome_candidate_count:{result.browser_chrome_candidate_count}")
    print(f"in_page_candidate_count:{result.in_page_candidate_count}")
    print(f"prompt_input_candidate_found:{str(result.prompt_input_candidate_found).lower()}")
    print(f"send_button_candidate_found:{str(result.send_button_candidate_found).lower()}")
    print("chatgpt_prompt_submitted:false")
    print("prompt_text_entered:false")
    print("page_click_performed:false")
    print("download_click_performed:false")
    print("run_package_invoked:false")
    print("pasteback_or_send_performed:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
