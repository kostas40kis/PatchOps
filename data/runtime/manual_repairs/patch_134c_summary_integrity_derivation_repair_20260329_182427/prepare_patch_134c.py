from __future__ import annotations

import json
from pathlib import Path

patch_root = Path(__file__).resolve().parent
project_root = patch_root.parents[3]

manifest = {
    "manifest_version": "1",
    "patch_name": "patch_134c_summary_integrity_derivation_repair",
    "active_profile": "generic_python",
    "target_project_root": str(project_root),
    "backup_files": [],
    "files_to_write": [
        {
            "path": "docs/project_status.md",
            "content_path": "content/docs/project_status.md",
            "encoding": "utf-8",
        },
        {
            "path": "docs/patch_ledger.md",
            "content_path": "content/docs/patch_ledger.md",
            "encoding": "utf-8",
        },
        {
            "path": "docs/summary_integrity_repair_stream.md",
            "content_path": "content/docs/summary_integrity_repair_stream.md",
            "encoding": "utf-8",
        },
        {
            "path": "patchops/reporting/renderer.py",
            "content_path": "content/patchops/reporting/renderer.py",
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_summary_integrity_current.py",
            "content_path": "content/tests/test_summary_integrity_current.py",
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "summary_integrity_current",
            "program": "py",
            "args": [
                "-m",
                "pytest",
                "-q",
                "tests/test_summary_integrity_current.py",
            ],
            "working_directory": str(project_root),
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
        "report_dir": str(patch_root / "inner_reports"),
        "report_name_prefix": "patch_134c_summary_integrity_derivation_repair",
        "write_to_desktop": True,
    },
    "tags": [
        "summary_integrity",
        "self_hosted",
        "derivation_repair",
    ],
    "notes": "Patch 134C repairs report-summary derivation so required validation/smoke failures cannot render PASS while tolerated non-zero exits remain allowed.",
}

manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(str(manifest_path))