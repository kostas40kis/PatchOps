from __future__ import annotations

import json
from pathlib import Path

patch_root = Path(__file__).resolve().parent
manifest_path = patch_root / "patch_manifest.json"
reports_root = patch_root / "inner_reports"

manifest = {
    "manifest_version": "1",
    "patch_name": "patch_134b_summary_integrity_authoring_unblocker",
    "active_profile": "generic_python",
    "target_project_root": r"C:\dev\patchops",
    "files_to_write": [
        {
            "path": "docs/project_status.md",
            "content_path": r"content\docs\project_status.md",
            "encoding": "utf-8",
        },
        {
            "path": "docs/patch_ledger.md",
            "content_path": r"content\docs\patch_ledger.md",
            "encoding": "utf-8",
        },
        {
            "path": "docs/summary_integrity_repair_stream.md",
            "content_path": r"content\docs\summary_integrity_repair_stream.md",
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_self_hosted_manual_repair_authoring_current.py",
            "content_path": r"content\tests\test_self_hosted_manual_repair_authoring_current.py",
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "self_hosted_manual_repair_authoring_current",
            "program": "py",
            "args": [
                "-m",
                "pytest",
                "-q",
                "tests/test_self_hosted_manual_repair_authoring_current.py",
            ],
            "working_directory": r"C:\dev\patchops",
        }
    ],
    "report_preferences": {
        "report_dir": str(reports_root),
        "report_name_prefix": "patch_134b_summary_integrity_authoring_unblocker",
    },
    "tags": [
        "summary_integrity",
        "self_hosted",
        "authoring_unblocker",
    ],
    "notes": "Patch 134B narrows the summary-integrity authoring unblocker and proves manifest-local relative content_path handling for self-hosted manual-repair patches.",
}

manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(str(manifest_path))