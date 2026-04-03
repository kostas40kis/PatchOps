from __future__ import annotations

import json
import sys
from pathlib import Path

PATCH_NAME = "patch_134g_summary_integrity_final_proof_and_handoff_refresh"

def main() -> int:
    project_root = Path(sys.argv[1]).resolve()
    handoff_root = project_root / "handoff"

    required = [
        handoff_root / "current_handoff.md",
        handoff_root / "current_handoff.json",
        handoff_root / "latest_report_copy.txt",
        handoff_root / "latest_report_index.json",
        handoff_root / "next_prompt.txt",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("missing handoff artifacts: " + ", ".join(missing))

    latest_report_text = (handoff_root / "latest_report_copy.txt").read_text(encoding="utf-8")
    current_handoff_json_text = (handoff_root / "current_handoff.json").read_text(encoding="utf-8")
    current_handoff_md = (handoff_root / "current_handoff.md").read_text(encoding="utf-8")
    next_prompt = (handoff_root / "next_prompt.txt").read_text(encoding="utf-8")
    latest_index = json.loads((handoff_root / "latest_report_index.json").read_text(encoding="utf-8"))

    assert PATCH_NAME in latest_report_text
    assert PATCH_NAME in current_handoff_json_text or PATCH_NAME in current_handoff_md
    assert "current_handoff.md" in next_prompt
    assert latest_index.get("failure_class") in {None, "(none)", "", "none"} or str(latest_index.get("failure_class")).lower() in {"(none)", "none", ""}
    print("patch_134g export validation passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())