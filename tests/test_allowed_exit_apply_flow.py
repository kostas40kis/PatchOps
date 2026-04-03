import json
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


def test_apply_manifest_allows_expected_non_zero_exit_code(tmp_path: Path) -> None:
    wrapper_root = Path(__file__).resolve().parents[1]
    target_root = tmp_path / "target_repo"
    report_dir = tmp_path / "reports"
    manifest_root = tmp_path / "manifest_root"

    target_root.mkdir()
    report_dir.mkdir()
    manifest_root.mkdir()

    manifest_data = {
        "manifest_version": "1",
        "patch_name": "allowed_exit_apply_proof",
        "active_profile": "generic_python",
        "target_project_root": str(target_root).replace("\\", "/"),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "ALLOWED_EXIT_APPLY_RESULT.txt",
                "content": "Allowed exit apply proof.\n",
                "content_path": None,
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "expected_non_zero",
                "program": "python",
                "args": ["-c", "import sys; print('expected non-zero'); sys.exit(3)"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0, 3],
            }
        ],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir).replace("\\", "/"),
            "report_name_prefix": "allowed_exit_apply_proof",
            "write_to_desktop": False,
        },
        "tags": ["test", "allowed_exit_codes", "apply_flow"],
        "notes": "Temporary manifest used by test_allowed_exit_apply_flow.",
    }

    manifest_path = manifest_root / "allowed_exit_apply_proof.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    written_file = target_root / "ALLOWED_EXIT_APPLY_RESULT.txt"
    assert result.result_label == "PASS"
    assert result.exit_code == 0
    assert written_file.exists()
    assert written_file.read_text(encoding="utf-8") == "Allowed exit apply proof.\n"
    assert result.report_path.exists()

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "expected_non_zero" in report_text
    assert "allowed_exit_apply_proof" in report_text
    assert "Result   : PASS" in report_text
