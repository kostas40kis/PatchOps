from __future__ import annotations

import json
import sys
from pathlib import Path

patch_root = Path(sys.argv[1]).resolve()
repo_root = patch_root.parents[3]
content_root = patch_root / "content"
(content_root / "docs").mkdir(parents=True, exist_ok=True)


def append_block_if_missing(path: Path, marker: str, block: str) -> str:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return text
    text = text.rstrip() + "\n\n" + block.rstrip() + "\n"
    return text

project_status_path = repo_root / "docs" / "project_status.md"
patch_ledger_path = repo_root / "docs" / "patch_ledger.md"
stream_path = repo_root / "docs" / "summary_integrity_repair_stream.md"

project_status_block = """## Summary-integrity repair stream status â€” March 30, 2026

The summary-integrity repair stream is now closed through `p134z_final_proof_handoff_refresh`.

What is fixed:
- required command failure no longer renders `PASS` in the summary-facing surfaces,
- workflow-facing surfaces fail closed instead of trusting stale success state,
- Windows-hostile long self-hosted custom `report_dir` shapes now fall back cleanly before hostile mkdir/write behavior can break the run,
- the maintained proof layer is green again.

Current posture:
- the repo remains in maintenance / finalization posture,
- the summary-integrity stream is complete unless new evidence reopens it,
- future work should be narrow maintenance only.
"""

patch_ledger_block = """## Patch 134Z â€” final proof / handoff refresh after report-path fallback repair

- reran the maintained summary-integrity proof layer from the new green report-path frontier,
- kept the repair stream narrow,
- treated the report-path work as separate from the original summary-integrity contradiction,
- refreshed handoff surfaces from the new green current report,
- closed the summary-integrity repair stream conservatively.
"""

stream_block = """## Final proof / closure after 134Y and 134Z

The stream finished in two truthful steps:

1. `p134y_report_dir_pre_mkdir_fallback_fix` repaired the last live Windows-hostile report-dir blocker by delaying custom report_dir creation until a safe candidate path was selected.
2. `p134z_final_proof_handoff_refresh` reran the maintained proof layer from that green report-path frontier and refreshed handoff from the resulting green report.

Final interpretation:
- the original summary-integrity contradiction remains fixed,
- tolerated explicit nonzero exits remain allowed,
- workflow-facing surfaces fail closed,
- the Windows-hostile custom report-path issue is repaired,
- the stream is complete unless new contrary evidence appears.
"""

project_status_text = append_block_if_missing(project_status_path, "## Summary-integrity repair stream status â€” March 30, 2026", project_status_block)
patch_ledger_text = append_block_if_missing(patch_ledger_path, "## Patch 134Z â€” final proof / handoff refresh after report-path fallback repair", patch_ledger_block)
stream_text = append_block_if_missing(stream_path, "## Final proof / closure after 134Y and 134Z", stream_block)

(content_root / "docs" / "project_status.md").write_text(project_status_text, encoding="utf-8")
(content_root / "docs" / "patch_ledger.md").write_text(patch_ledger_text, encoding="utf-8")
(content_root / "docs" / "summary_integrity_repair_stream.md").write_text(stream_text, encoding="utf-8")

manifest = {
    "manifest_version": "1",
    "patch_name": "p134z_final_proof_handoff_refresh",
    "active_profile": "generic_python",
    "target_project_root": "C:/dev/patchops",
    "backup_files": [
        "docs/project_status.md",
        "docs/patch_ledger.md",
        "docs/summary_integrity_repair_stream.md",
        "handoff/current_handoff.md",
        "handoff/current_handoff.json",
        "handoff/latest_report_copy.txt",
        "handoff/latest_report_index.json",
        "handoff/next_prompt.txt",
    ],
    "files_to_write": [
        {
            "path": "docs/project_status.md",
            "content": None,
            "content_path": "content/docs/project_status.md",
            "encoding": "utf-8",
        },
        {
            "path": "docs/patch_ledger.md",
            "content": None,
            "content_path": "content/docs/patch_ledger.md",
            "encoding": "utf-8",
        },
        {
            "path": "docs/summary_integrity_repair_stream.md",
            "content": None,
            "content_path": "content/docs/summary_integrity_repair_stream.md",
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "summary_integrity_final_proof_pytest",
            "program": "py",
            "args": [
                "-m",
                "pytest",
                "-q",
                "tests/test_summary_integrity_current.py",
                "tests/test_summary_integrity_workflow_current.py",
                "tests/test_report_preference_apply_flow.py",
                "tests/test_report_preference_apply_flow_current.py",
                "tests/test_report_preference_examples.py",
                "tests/test_apply_report_write_current.py",
                "tests/test_report_path_current.py",
            ],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        }
    ],
    "smoke_commands": [],
    "audit_commands": [],
    "cleanup_commands": [],
    "archive_commands": [],
    "failure_policy": {},
    "report_preferences": {
        "report_dir": str((patch_root / "inner_reports")).replace("\\", "/"),
        "report_name_prefix": "p134z",
        "write_to_desktop": False,
    },
    "tags": [
        "self_hosted",
        "summary_integrity",
        "final_proof",
        "handoff_refresh",
    ],
    "notes": "Patch 134Z reruns the maintained summary-integrity proof layer after 134Y and refreshes handoff from the new green current report.",
}

manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(str(manifest_path))