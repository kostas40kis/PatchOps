from pathlib import Path
import json
import sys
import tempfile

from patchops.workflows.apply_patch import apply_manifest

root = Path(sys.argv[1]).resolve()
apply_text = (root / "patchops" / "workflows" / "apply_patch.py").read_text(encoding="utf-8")
test_text = (root / "tests" / "test_report_preference_apply_flow.py").read_text(encoding="utf-8")
current_test_text = (root / "tests" / "test_report_preference_apply_flow_current.py").read_text(encoding="utf-8")
stream_text = (root / "docs" / "summary_integrity_repair_stream.md").read_text(encoding="utf-8")

assert "report_path.parent.mkdir(parents=True, exist_ok=True)" in apply_text
assert "sys.executable" in test_text
assert "sys.executable" in current_test_text
assert "PATCHOPS_PATCH134I_REPORT_DIR_PROOF" in stream_text

with tempfile.TemporaryDirectory() as temp_dir_raw:
    temp_dir = Path(temp_dir_raw)
    target_root = temp_dir / "target"
    report_dir = temp_dir / "reports" / "nested"
    target_root.mkdir()

    manifest = {
        "manifest_version": "1",
        "patch_name": "report_dir_direct_validation",
        "active_profile": "generic_python",
        "target_project_root": str(target_root),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "DIRECT_REPORT_DIR_OK.txt",
                "content": "direct report dir validation\n",
                "content_path": None,
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "python_version",
                "program": sys.executable,
                "args": ["--version"],
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
            "report_dir": str(report_dir),
            "report_name_prefix": "direct_report_dir_validation",
            "write_to_desktop": False,
        },
        "tags": ["test", "report_preferences", "direct"],
        "notes": "Temporary manifest used by validate_patch_134i.py.",
    }

    manifest_path = temp_dir / "direct_report_dir_validation.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    result = apply_manifest(manifest_path, wrapper_project_root=root)

    assert result.exit_code == 0
    assert result.result_label == "PASS"
    assert report_dir.exists()
    assert result.report_path.exists()
    assert result.report_path.parent == report_dir
    assert (target_root / "DIRECT_REPORT_DIR_OK.txt").read_text(encoding="utf-8") == "direct report dir validation\n"

print("patch_134i validation passed")
