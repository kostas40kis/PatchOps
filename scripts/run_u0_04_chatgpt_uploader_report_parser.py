from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.chatgpt_uploader.report_parser import parse_report_file, render_text_summary


SAMPLE_REPORT = """PATCHOPS RUN-PACKAGE OUTER REPORT
---------------------------------
Result              : PASS
Exit Code           : 0
ExitCode            : 0
Failure Category    :
FailureCategory     :

STDOUT
------
PATCHOPS RUN SUMMARY
--------------------
Mode               : apply
Patch Name         : u0_04_chatgpt_uploader_report_parser_smoke
ExitCode           : 0
Result             : PASS
"""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="U0.4 report parser smoke runner.")
    parser.add_argument("--report", help="Optional report path to parse. If omitted, a safe sample report is generated.")
    parser.add_argument("--output-dir", default="data/runtime/u0_04_chatgpt_uploader_report_parser")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.report:
        report_path = Path(args.report)
    else:
        report_path = output_dir / "sample_patchops_pass_report.txt"
        report_path.write_text(SAMPLE_REPORT, encoding="utf-8")

    parsed = parse_report_file(report_path)
    payload = parsed.to_payload()

    json_path = output_dir / "u0_04_report_parse_summary.json"
    text_path = output_dir / "u0_04_report_parse_summary.txt"

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    text_path.write_text(render_text_summary(parsed), encoding="utf-8")

    print(json.dumps({
        "ok": parsed.ok,
        "result": parsed.result,
        "exit_code": parsed.exit_code,
        "failure_layer": parsed.failure_layer,
        "input_report": str(report_path),
        "json_summary": str(json_path),
        "text_summary": str(text_path),
        "safety": {
            "webdriver_used": False,
            "selenium_used": False,
            "browser_dom_automation_used": False,
            "cloudflare_bypass_attempted": False,
            "captcha_bypass_attempted": False,
            "file_upload_attempted": False,
            "chatgpt_submit_performed": False,
            "conversation_text_logged": False,
            "random_page_click_performed": False,
        },
    }, indent=2, sort_keys=True))

    return 0 if parsed.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
