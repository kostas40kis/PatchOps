from __future__ import annotations

import json
from pathlib import Path

patch_root = Path(__file__).resolve().parent
project_root = patch_root.parents[3]

manifest = {
    "manifest_version": "1",
    "patch_name": "patch_134d_summary_integrity_workflow_hardening",
    "active_profile": "generic_python",
    "target_project_root": str(project_root),
    "files_to_write": [
        {
            "path": "docs/summary_integrity_workflow_hardening.md",
            "content_path": "content/docs/summary_integrity_workflow_hardening.md",
            "encoding": "utf-8",
        },
        {
            "path": "patchops/result_integrity.py",
            "content_path": "content/patchops/result_integrity.py",
            "encoding": "utf-8",
        },
        {
            "path": "patchops/reporting/renderer.py",
            "content_path": "content/patchops/reporting/renderer.py",
            "encoding": "utf-8",
        },
        {
            "path": "patchops/cli.py",
            "content_path": "content/patchops/cli.py",
            "encoding": "utf-8",
        },
        {
            "path": "patchops/handoff.py",
            "content_path": "content/patchops/handoff.py",
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_summary_integrity_workflow_current.py",
            "content_path": "content/tests/test_summary_integrity_workflow_current.py",
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "summary_integrity_workflow_current",
            "program": "py",
            "args": [
                "-m",
                "pytest",
                "-q",
                "tests/test_summary_integrity_current.py",
                "tests/test_summary_integrity_workflow_current.py",
            ],
            "working_directory": str(project_root),
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        }
    ],
    "report_preferences": {
        "report_dir": str(patch_root / "inner_reports"),
        "report_name_prefix": "patch_134d_summary_integrity_workflow_hardening",
        "write_to_desktop": True,
    },
    "tags": [
        "summary_integrity",
        "self_hosted",
        "workflow_hardening",
    ],
    "notes": "Patch 134D hardens workflow-facing summary surfaces so CLI and handoff fail closed when required command evidence contradicts stale success state.",
}

manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(str(manifest_path))
