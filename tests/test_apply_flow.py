import json
import sys
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


def test_apply_manifest_writes_file_and_report(tmp_path: Path):
    project_root = tmp_path / "project"
    project_root.mkdir()

    manifest_path = tmp_path / "apply_manifest.json"
    manifest = {
        "manifest_version": "1",
        "patch_name": "apply_demo",
        "active_profile": "generic_python",
        "target_project_root": str(project_root),
        "files_to_write": [
            {"path": "notes.txt", "content": "hello from patchops\n"}
        ],
        "validation_commands": [
            {
                "name": "python_version",
                "program": sys.executable,
                "args": ["--version"],
                "working_directory": ".",
            }
        ],
        "report_preferences": {"report_dir": str(tmp_path)},
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=tmp_path)

    assert result.exit_code == 0
    assert result.result_label == "PASS"
    assert (project_root / "notes.txt").read_text(encoding="utf-8") == "hello from patchops\n"
    report_text = result.report_path.read_text(encoding="utf-8")
    assert "SUMMARY" in report_text
    assert "ExitCode : 0" in report_text
    assert f"Manifest Path        : {manifest_path.resolve()}" in report_text
    assert str(project_root / "notes.txt") in report_text


def test_apply_manifest_backs_up_existing_file_and_reports_it(tmp_path: Path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    existing_path = project_root / "notes.txt"
    existing_path.write_text("old content\n", encoding="utf-8")

    manifest_path = tmp_path / "apply_with_backup_manifest.json"
    manifest = {
        "manifest_version": "1",
        "patch_name": "apply_backup_demo",
        "active_profile": "generic_python",
        "target_project_root": str(project_root),
        "files_to_write": [
            {"path": "notes.txt", "content": "new content\n"}
        ],
        "validation_commands": [
            {
                "name": "python_version",
                "program": sys.executable,
                "args": ["--version"],
                "working_directory": ".",
            }
        ],
        "report_preferences": {"report_dir": str(tmp_path)},
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=tmp_path)

    assert result.exit_code == 0
    assert existing_path.read_text(encoding="utf-8") == "new content\n"
    matching_records = [record for record in result.backup_records if record.source == existing_path]
    assert matching_records
    backup_record = matching_records[0]
    assert backup_record.existed is True
    assert backup_record.destination is not None
    assert backup_record.destination.exists()
    assert backup_record.destination.read_text(encoding="utf-8") == "old content\n"

    report_text = result.report_path.read_text(encoding="utf-8")
    assert f"BACKUP : {existing_path}" in report_text
    assert str(backup_record.destination) in report_text
    assert "Result   : PASS" in report_text


def test_apply_manifest_reports_failure_with_summary(tmp_path: Path):
    project_root = tmp_path / "project"
    project_root.mkdir()

    manifest_path = tmp_path / "apply_failure_manifest.json"
    manifest = {
        "manifest_version": "1",
        "patch_name": "apply_failure",
        "active_profile": "generic_python",
        "target_project_root": str(project_root),
        "files_to_write": [
            {"path": "notes.txt", "content": "hello from patchops\n"}
        ],
        "validation_commands": [
            {
                "name": "fail_me",
                "program": sys.executable,
                "args": ["-c", "import sys; sys.exit(7)"],
                "working_directory": ".",
            }
        ],
        "report_preferences": {"report_dir": str(tmp_path)},
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=tmp_path)

    assert result.exit_code == 7
    assert result.result_label == "FAIL"
    report_text = result.report_path.read_text(encoding="utf-8")
    assert "FAILURE DETAILS" in report_text
    assert "Category : target_project_failure" in report_text
    assert "ExitCode : 7" in report_text
    assert "Result   : FAIL" in report_text