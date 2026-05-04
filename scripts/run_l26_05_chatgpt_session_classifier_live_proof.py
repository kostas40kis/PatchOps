from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops.edge_rpa.edge_session_classifier import assert_l26_05_acceptance, run_l26_05_session_classifier


def main() -> int:
    parser = argparse.ArgumentParser(description="L26.5 ChatGPT accessibility/session classifier proof.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--start-if-missing", action="store_true")
    parser.add_argument("--max-depth", type=int, default=5)
    parser.add_argument("--max-controls", type=int, default=220)
    args = parser.parse_args()

    result = run_l26_05_session_classifier(
        output_dir=Path(args.output_dir),
        start_if_missing=args.start_if_missing,
        max_depth=args.max_depth,
        max_controls=args.max_controls,
    )
    payload = result.to_payload()
    print("L26_05_LIVE_CHATGPT_SESSION_CLASSIFIER_JSON_START")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("L26_05_LIVE_CHATGPT_SESSION_CLASSIFIER_JSON_END")
    assert_l26_05_acceptance(result)
    print("L26_05_ACCEPTANCE: PASS")
    print(f"classification:{result.classification}")
    print("chatgpt_session_classified:true")
    print("cloudflare_bypass_attempted:false")
    print("browser_navigation_performed:false")
    print("chatgpt_prompt_submitted:false")
    print("download_click_performed:false")
    print("run_package_invoked:false")
    print("pasteback_or_send_performed:false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
