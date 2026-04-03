from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


def test_apply_manifest_overwrite_flow_reports_backup_behavior(tmp_path: Path) -> None:
    wrapper_root = Path(__file__).resolve().parents[1]
    target_root = tmp_path / "target_repo"
    report_dir = tmp_path / "reports"
    target_root.mkdir()
    report_dir.mkdir()

    target_file = target_root / "BACKUP_TARGET.txt"
    target_file.write_text("original content\n", encoding="utf-8")

    manifest_path = tmp_path / "backup_apply_proof.json"
    manifest_path.write_text(
        """{
  "manifest_version": "1",
  "patch_name": "backup_apply_proof",
  "active_profile": "generic_python",
  "target_project_root": "%s",
  "backup_files": [
    "BACKUP_TARGET.txt"
  ],
  "files_to_write": [
    {
      "path": "BACKUP_TARGET.txt",
      "content": "replacement content\\n",
      "content_path": null,
      "encoding": "utf-8"
    }
  ],
  "validation_commands": [
    {
      "name": "python_version",
      "program": "python",
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
    "report_name_prefix": "backup_apply_proof",
    "write_to_desktop": false
  },
  "tags": ["test", "backup", "apply_flow"],
  "notes": "Temporary manifest used by test_backup_apply_flow."
}
""" % (
            str(target_root).replace("\\", "/"),
            str(report_dir).replace("\\", "/"),
        ),
        encoding="utf-8",
    )

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == "PASS"
    assert result.exit_code == 0
    assert result.report_path.exists()

    assert target_file.read_text(encoding="utf-8") == "replacement content\n"

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "BACKUP" in report_text
    assert "BACKUP_TARGET.txt" in report_text
    assert "SUMMARY" in report_text
    assert "ExitCode : 0" in report_text
    assert "Result   : PASS" in report_text
