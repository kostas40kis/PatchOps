import json
import sys
from pathlib import Path

from patchops.workflows.verify_only import verify_only


def test_verify_only_runs_without_rewriting(tmp_path: Path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "example.txt").write_text("hello", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"
    manifest = {
        "manifest_version": "1",
        "patch_name": "verify",
        "active_profile": "generic_python",
        "target_project_root": str(project_root),
        "files_to_write": [{"path": "example.txt", "content": "ignored in verify"}],
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
    result = verify_only(manifest_path, wrapper_project_root=tmp_path)
    assert result.exit_code == 0
    assert result.result_label == "PASS"
