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
                "working_directory": "."
            }
        ],
        "report_preferences": {"report_dir": str(tmp_path)}
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
                "working_directory": "."
            }
        ],
        "report_preferences": {"report_dir": str(tmp_path)}
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