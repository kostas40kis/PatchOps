from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.chatgpt_uploader.report_resolver import resolve_report, write_resolver_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the U0.3 ChatGPT uploader report resolver smoke proof.")
    parser.add_argument("--output-dir", default="data/runtime/u0_03_chatgpt_uploader_report_resolver")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    sample_dir = output_dir / "sample_reports"
    sample_dir.mkdir(parents=True, exist_ok=True)
    sample_report = sample_dir / "u0_03_sample_patchops_report.txt"
    sample_report.write_text(
        "PATCHOPS RUN SUMMARY\n"
        "--------------------\n"
        "Mode               : apply\n"
        "Patch Name         : u0_03_sample\n"
        "ExitCode           : 0\n"
        "Result             : PASS\n",
        encoding="utf-8",
    )

    result = resolve_report(report_path=sample_report)
    outputs = write_resolver_outputs(result, output_dir)
    payload = result.to_payload()
    payload["output_paths"] = outputs
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
