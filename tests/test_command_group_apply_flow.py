from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


def _write_manifest(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


import json


def test_apply_manifest_runs_smoke_and_audit_commands_and_reports_them(tmp_path: Path) -> None:
    wrapper_root = Path(__file__).resolve().parents[1]
    target_root = tmp_path / "target_repo"
    report_dir = tmp_path / "reports"
    target_root.mkdir()
    report_dir.mkdir()

    manifest_data = {
        "manifest_version": "1",
        "patch_name": "smoke_audit_apply_proof",
        "active_profile": "generic_python",
        "target_project_root": str(target_root).replace("\\", "/"),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "SMOKE_AUDIT_APPLY_RESULT.txt",
                "content": "command-group apply proof\n",
                "content_path": None,
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "validation_ok",
                "program": "python",
                "args": ["-c", "print('validation ok')"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "smoke_commands": [
            {
                "name": "smoke_ok",
                "program": "python",
                "args": ["-c", "print('smoke ok')"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "audit_commands": [
            {
                "name": "audit_ok",
                "program": "python",
                "args": ["-c", "print('audit ok')"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir).replace("\\", "/"),
            "report_name_prefix": "smoke_audit_apply_proof",
            "write_to_desktop": False,
        },
        "tags": ["test", "command_groups", "smoke_audit"],
        "notes": "Temporary manifest used by test_command_group_apply_flow.",
    }
    manifest_path = _write_manifest(tmp_path / "smoke_audit_apply_proof.json", manifest_data)

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == "PASS"
    assert result.exit_code == 0
    assert result.report_path.exists()

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "SMOKE COMMAND" in report_text
    assert "AUDIT COMMAND" in report_text
    assert "smoke ok" in report_text
    assert "audit ok" in report_text


def test_apply_manifest_runs_cleanup_and_archive_commands_and_reports_them(tmp_path: Path) -> None:
    wrapper_root = Path(__file__).resolve().parents[1]
    target_root = tmp_path / "target_repo"
    report_dir = tmp_path / "reports"
    target_root.mkdir()
    report_dir.mkdir()

    manifest_data = {
        "manifest_version": "1",
        "patch_name": "cleanup_archive_apply_proof",
        "active_profile": "generic_python",
        "target_project_root": str(target_root).replace("\\", "/"),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "CLEANUP_ARCHIVE_APPLY_RESULT.txt",
                "content": "command-group apply proof\n",
                "content_path": None,
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "validation_ok",
                "program": "python",
                "args": ["-c", "print('validation ok')"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [
            {
                "name": "cleanup_ok",
                "program": "python",
                "args": ["-c", "print('cleanup ok')"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "archive_commands": [
            {
                "name": "archive_ok",
                "program": "python",
                "args": ["-c", "print('archive ok')"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir).replace("\\", "/"),
            "report_name_prefix": "cleanup_archive_apply_proof",
            "write_to_desktop": False,
        },
        "tags": ["test", "command_groups", "cleanup_archive"],
        "notes": "Temporary manifest used by test_command_group_apply_flow.",
    }
    manifest_path = _write_manifest(tmp_path / "cleanup_archive_apply_proof.json", manifest_data)

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == "PASS"
    assert result.exit_code == 0
    assert result.report_path.exists()

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "CLEANUP COMMAND" in report_text
    assert "ARCHIVE COMMAND" in report_text
    assert "cleanup ok" in report_text
    assert "archive ok" in report_text
