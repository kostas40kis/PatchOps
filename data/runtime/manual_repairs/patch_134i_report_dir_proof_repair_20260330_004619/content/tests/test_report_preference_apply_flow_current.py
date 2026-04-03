import sys
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


def test_apply_manifest_creates_missing_custom_report_dir(tmp_path: Path) -> None:
    wrapper_root = Path(__file__).resolve().parents[1]
    target_root = tmp_path / "target_repo"
    report_dir = tmp_path / "reports" / "nested"
    target_root.mkdir()

    manifest_path = tmp_path / "missing_report_dir_apply.json"
    manifest_path.write_text(
        """{
  "manifest_version": "1",
  "patch_name": "missing_report_dir_apply",
  "active_profile": "generic_python",
  "target_project_root": "%s",
  "backup_files": [],
  "files_to_write": [
    {
      "path": "REPORT_DIR_CURRENT.txt",
      "content": "report dir current proof\n",
      "content_path": null,
      "encoding": "utf-8"
    }
  ],
  "validation_commands": [
    {
      "name": "python_version",
      "program": "%s",
      "args": ["--version"],
      "working_directory": ".",
      "use_profile_runtime": false,
      "allowed_exit_codes": [0]
    }
  ],
  "smoke_commands": [],
  "audit_commands": [],
  "cleanup_commands": [],
  "archive_commands": [],
  "failure_policy": {},
  "report_preferences": {
    "report_dir": "%s",
    "report_name_prefix": "report_dir_current",
    "write_to_desktop": false
  },
  "tags": ["test", "report_preferences", "current"],
  "notes": "Temporary manifest used by test_apply_manifest_creates_missing_custom_report_dir."
}
""" % (
            str(target_root).replace("\", "/"),
            sys.executable.replace("\", "/"),
            str(report_dir).replace("\", "/"),
        ),
        encoding="utf-8",
    )

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.exit_code == 0
    assert result.result_label == "PASS"
    assert report_dir.exists()
    assert result.report_path.exists()
    assert result.report_path.parent == report_dir
    assert (target_root / "REPORT_DIR_CURRENT.txt").read_text(encoding="utf-8") == "report dir current proof\n"
