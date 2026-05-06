from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.chatgpt_uploader.pasteback_builder import build_pasteback, write_pasteback_outputs
from patchops.chatgpt_uploader.report_parser import parse_report_file


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
Patch Name         : u0_05_chatgpt_uploader_pasteback_builder_smoke
ExitCode           : 0
Result             : PASS
"""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="U0.5 PATCHOPS_LLM_PASTEBACK builder smoke runner.")
    parser.add_argument("--report", help="Optional PatchOps report txt file. If omitted, a safe sample PASS report is generated.")
    parser.add_argument("--output-dir", default="data/runtime/u0_05_chatgpt_uploader_pasteback_builder")
    parser.add_argument("--json", action="store_true", help="Print JSON summary instead of pasteback text.")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.report:
        report_path = Path(args.report)
    else:
        report_path = output_dir / "sample_patchops_pass_report.txt"
        report_path.write_text(SAMPLE_REPORT, encoding="utf-8")

    parsed = parse_report_file(report_path)
    message = build_pasteback(parsed)
    outputs = write_pasteback_outputs(message, args.output_dir)

    if args.json:
        print(json.dumps({**message.to_payload(), "outputs": outputs}, indent=2, sort_keys=True))
    else:
        print(message.text, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
