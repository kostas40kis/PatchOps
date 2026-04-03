from __future__ import annotations

import json
import sys
from pathlib import Path

project_root = Path(sys.argv[1]).resolve()

required_handoff_files = [
    "handoff/current_handoff.md",
    "handoff/current_handoff.json",
    "handoff/latest_report_copy.txt",
    "handoff/latest_report_index.json",
    "handoff/next_prompt.txt",
]

for relative_path in required_handoff_files:
    path = project_root / relative_path
    if not path.exists():
        raise SystemExit(f"Missing required handoff artifact: {path}")
    if path.stat().st_size == 0:
        raise SystemExit(f"Empty required handoff artifact: {path}")

handoff_json = json.loads((project_root / "handoff/current_handoff.json").read_text(encoding="utf-8"))
if not isinstance(handoff_json, dict) or not handoff_json:
    raise SystemExit("handoff/current_handoff.json did not contain a non-empty JSON object.")

latest_report_copy = (project_root / "handoff/latest_report_copy.txt").read_text(encoding="utf-8")
if "PASS" not in latest_report_copy:
    raise SystemExit("handoff/latest_report_copy.txt did not contain PASS evidence.")

marker_requirements = {
    "docs/project_status.md": [
        "PATCHOPS_PATCH134O_STATUS:START",
        "PATCHOPS_PATCH134P_STATUS:START",
    ],
    "docs/patch_ledger.md": [
        "PATCHOPS_PATCH134O_LEDGER:START",
        "PATCHOPS_PATCH134P_LEDGER:START",
    ],
    "docs/summary_integrity_repair_stream.md": [
        "## Patch 134O - exact-current repair manifest authoring fix",
        "## Patch 134P - final proof and handoff refresh retry",
        "## Closure statement",
    ],
}

for relative_path, markers in marker_requirements.items():
    text = (project_root / relative_path).read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"Missing marker '{marker}' in {relative_path}")

print("handoff artifacts and summary-integrity closure docs validated successfully")