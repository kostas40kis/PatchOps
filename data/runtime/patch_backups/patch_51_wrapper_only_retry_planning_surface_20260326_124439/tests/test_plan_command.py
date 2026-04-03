import json
import sys
from pathlib import Path

from patchops.cli import main


def test_plan_command_prints_apply_preview(tmp_path, capsys):
    project_root = tmp_path / "project"
    project_root.mkdir()

    manifest_path = tmp_path / "plan_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifest_version": "1",
                "patch_name": "plan_demo",
                "active_profile": "generic_python",
                "target_project_root": str(project_root),
                "files_to_write": [
                    {"path": "notes.txt", "content": "hello from plan\n"}
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
        ),
        encoding="utf-8",
    )

    exit_code = main(["plan", str(manifest_path), "--wrapper-root", str(tmp_path)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["mode"] == "apply"
    assert payload["active_profile"] == "generic_python"
    assert payload["manifest_path"] == str(manifest_path.resolve())
    assert payload["target_project_root"] == str(project_root.resolve())
    assert payload["target_files"] == [str((project_root / "notes.txt").resolve())]
    assert payload["backup_files"] == ["notes.txt"]
    assert payload["report_path_pattern"].endswith("generic_python_patch_plan_demo_<timestamp>.txt")
    assert payload["backup_root_pattern"] is not None
    assert payload["validation_commands"][0]["name"] == "python_version"


def test_plan_command_prints_verify_preview(tmp_path, capsys):
    project_root = tmp_path / "project"
    project_root.mkdir()

    manifest_path = tmp_path / "plan_verify_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifest_version": "1",
                "patch_name": "verify_demo",
                "active_profile": "generic_python",
                "target_project_root": str(project_root),
                "files_to_write": [
                    {"path": "notes.txt", "content": "verify target\n"}
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
        ),
        encoding="utf-8",
    )

    exit_code = main(["plan", str(manifest_path), "--mode", "verify", "--wrapper-root", str(tmp_path)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["mode"] == "verify"
    assert payload["backup_root_pattern"] is None
    assert payload["report_path_pattern"].endswith("generic_python_patch_verify_verify_demo_<timestamp>.txt")