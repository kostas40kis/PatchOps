import sys
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


def test_apply_manifest_respects_custom_report_dir_and_prefix(tmp_path: Path) -> None:
    wrapper_root = Path(__file__).resolve().parents[1]
    target_root = tmp_path / "target_repo"
    report_dir = tmp_path / "custom_reports"
    target_root.mkdir()
    report_dir.mkdir()

    manifest_path = tmp_path / "report_preference_apply_proof.json"
    manifest_path.write_text(
        """{
  "manifest_version": "1",
  "patch_name": "report_preference_apply_proof",
  "active_profile": "generic_python",
  "target_project_root": "%s",
  "backup_files": [],
  "files_to_write": [
    {
      "path": "REPORT_PREFERENCE_APPLY_RESULT.txt",
      "content": "report preference apply proof\\n",
      "content_path": null,
      "encoding": "utf-8"
    }
  ],
  "validation_commands": [
    {
      "name": "python_version",
      "program": "C:/Users/kostas/AppData/Local/Programs/Python/Python312/python.exe",
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
    "report_name_prefix": "custom_report_pref_demo",
    "write_to_desktop": false
  },
  "tags": ["test", "report_preferences", "apply_flow"],
  "notes": "Temporary manifest used by test_report_preference_apply_flow."
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
    assert result.report_path.parent == report_dir
    assert result.report_path.name.startswith("custom_report_pref_demo")

    written_file = target_root / "REPORT_PREFERENCE_APPLY_RESULT.txt"
    assert written_file.exists()
    assert written_file.read_text(encoding="utf-8") == "report preference apply proof\n"

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "SUMMARY" in report_text
    assert "ExitCode : 0" in report_text
    assert "Result   : PASS" in report_text
    assert "custom_report_pref_demo" in report_text
