import json
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


def test_apply_manifest_runs_generic_python_powershell_profile_end_to_end(tmp_path: Path) -> None:
    wrapper_root = Path(__file__).resolve().parents[1]
    target_root = tmp_path / "target_repo"
    report_dir = tmp_path / "reports"
    target_root.mkdir()
    report_dir.mkdir()

    manifest_data = {
        "manifest_version": "1",
        "patch_name": "generic_python_powershell_apply_proof",
        "active_profile": "generic_python_powershell",
        "target_project_root": str(target_root).replace("\\", "/"),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "GENERIC_PYTHON_POWERSHELL_APPLY_RESULT.txt",
                "content": "generic python powershell apply proof\n",
                "content_path": None,
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "powershell_validation",
                "program": "powershell.exe",
                "args": ["-NoProfile", "-Command", "Write-Output 'powershell ok'"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "smoke_commands": [
            {
                "name": "python_smoke",
                "program": "python",
                "args": ["-c", "print('python smoke ok')"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir).replace("\\", "/"),
            "report_name_prefix": "generic_python_powershell_apply_proof",
            "write_to_desktop": False,
        },
        "tags": ["test", "generic_python_powershell", "apply_flow"],
        "notes": "Temporary manifest used by test_generic_python_powershell_apply_flow.",
    }

    manifest_path = tmp_path / "generic_python_powershell_apply_proof.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == "PASS"
    assert result.exit_code == 0
    assert result.report_path.exists()

    written_file = target_root / "GENERIC_PYTHON_POWERSHELL_APPLY_RESULT.txt"
    assert written_file.exists()
    assert written_file.read_text(encoding="utf-8") == "generic python powershell apply proof\n"

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "powershell ok" in report_text
    assert "python smoke ok" in report_text
    assert "SUMMARY" in report_text
    assert "ExitCode : 0" in report_text
    assert "Result   : PASS" in report_text
