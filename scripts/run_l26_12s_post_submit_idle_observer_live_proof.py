from __future__ import annotations
import argparse, json
from pathlib import Path
from patchops.edge_rpa.edge_l26_12s_post_submit_idle_observer import assert_acceptance, run_post_submit_idle_observer

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True)
    p.add_argument("--report-path", required=True)
    p.add_argument("--allow-report-upload", action="store_true")
    p.add_argument("--allow-chatgpt-submit", action="store_true")
    p.add_argument("--observe-seconds", type=int, default=45)
    a = p.parse_args()
    result = run_post_submit_idle_observer(Path(a.output_dir), Path(a.report_path), a.allow_report_upload, a.allow_chatgpt_submit, a.observe_seconds)
    print("L26_12S_POST_SUBMIT_IDLE_OBSERVER_JSON_START")
    print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    print("L26_12S_POST_SUBMIT_IDLE_OBSERVER_JSON_END")
    assert_acceptance(result)
    print("L26_12S_ACCEPTANCE: PASS")
    print("ready_for_next_probe:true")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
