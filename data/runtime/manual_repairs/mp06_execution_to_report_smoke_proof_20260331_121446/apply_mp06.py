from pathlib import Path
from textwrap import dedent

project_root = Path(r"C:\dev\patchops")
target_path = project_root / "tests" / "test_execution_to_report_smoke_current.py"

content = dedent(
    """
    from __future__ import annotations

    import json
    import sys
    from pathlib import Path

    from patchops.workflows.apply_patch import apply_manifest
    from patchops.workflows.verify_only import verify_only


    def _write_manifest(path: Path, payload: dict) -> Path:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path


    def test_apply_manifest_carries_execution_output_into_report(tmp_path: Path) -> None:
        wrapper_root = Path(__file__).resolve().parents[1]
        target_root = tmp_path / "target_repo"
        report_dir = tmp_path / "reports"
        target_root.mkdir()
        report_dir.mkdir()

        manifest = {
            "manifest_version": "1",
            "patch_name": "execution_to_report_apply_proof",
            "active_profile": "generic_python",
            "target_project_root": str(target_root).replace("\\", "/"),
            "backup_files": [],
            "files_to_write": [
                {
                    "path": "EXECUTION_TO_REPORT_APPLY_RESULT.txt",
                    "content": "execution to report apply proof\\n",
                    "content_path": None,
                    "encoding": "utf-8",
                }
            ],
            "validation_commands": [
                {
                    "name": "validation_probe",
                    "program": sys.executable,
                    "args": [
                        "-c",
                        "import sys; print('apply smoke stdout'); print('apply smoke stderr', file=sys.stderr)",
                    ],
                    "working_directory": ".",
                    "use_profile_runtime": False,
                    "allowed_exit_codes": [0],
                }
            ],
            "smoke_commands": [],
            "audit_commands": [],
            "cleanup_commands": [],
            "archive_commands": [],
            "failure_policy": {},
            "report_preferences": {
                "report_dir": str(report_dir).replace("\\", "/"),
                "report_name_prefix": "execution_to_report_apply_proof",
                "write_to_desktop": False,
            },
            "tags": ["test", "execution", "report", "apply_flow"],
            "notes": "Temporary manifest used by test_execution_to_report_smoke_current.",
        }

        manifest_path = _write_manifest(tmp_path / "execution_to_report_apply_proof.json", manifest)
        result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

        assert result.result_label == "PASS"
        assert result.exit_code == 0
        assert result.report_path.exists()
        assert (target_root / "EXECUTION_TO_REPORT_APPLY_RESULT.txt").exists()

        report_text = result.report_path.read_text(encoding="utf-8")
        assert "VALIDATION COMMANDS" in report_text
        assert "FULL OUTPUT" in report_text
        assert "NAME    : validation_probe" in report_text
        assert "EXIT    : 0" in report_text
        assert "[validation_probe][stdout]" in report_text
        assert "[validation_probe][stderr]" in report_text
        assert "apply smoke stdout" in report_text
        assert "apply smoke stderr" in report_text
        assert "ExitCode : 0" in report_text
        assert "Result   : PASS" in report_text


    def test_verify_only_carries_execution_output_into_report(tmp_path: Path) -> None:
        wrapper_root = Path(__file__).resolve().parents[1]
        target_root = tmp_path / "target_repo"
        report_dir = tmp_path / "reports"
        target_root.mkdir()
        report_dir.mkdir()

        manifest = {
            "manifest_version": "1",
            "patch_name": "execution_to_report_verify_proof",
            "active_profile": "generic_python",
            "target_project_root": str(target_root).replace("\\", "/"),
            "backup_files": [],
            "files_to_write": [],
            "validation_commands": [
                {
                    "name": "verify_probe",
                    "program": sys.executable,
                    "args": [
                        "-c",
                        "import sys; print('verify smoke stdout'); print('verify smoke stderr', file=sys.stderr)",
                    ],
                    "working_directory": ".",
                    "use_profile_runtime": False,
                    "allowed_exit_codes": [0],
                }
            ],
            "smoke_commands": [],
            "audit_commands": [],
            "cleanup_commands": [],
            "archive_commands": [],
            "failure_policy": {},
            "report_preferences": {
                "report_dir": str(report_dir).replace("\\", "/"),
                "report_name_prefix": "execution_to_report_verify_proof",
                "write_to_desktop": False,
            },
            "tags": ["test", "execution", "report", "verify_only"],
            "notes": "Temporary manifest used by test_execution_to_report_smoke_current.",
        }

        manifest_path = _write_manifest(tmp_path / "execution_to_report_verify_proof.json", manifest)
        result = verify_only(manifest_path, wrapper_project_root=wrapper_root)

        assert result.result_label == "PASS"
        assert result.exit_code == 0
        assert result.report_path.exists()

        report_text = result.report_path.read_text(encoding="utf-8")
        assert "VALIDATION COMMANDS" in report_text
        assert "FULL OUTPUT" in report_text
        assert "NAME    : verify_probe" in report_text
        assert "EXIT    : 0" in report_text
        assert "[verify_probe][stdout]" in report_text
        assert "[verify_probe][stderr]" in report_text
        assert "verify smoke stdout" in report_text
        assert "verify smoke stderr" in report_text
        assert "ExitCode : 0" in report_text
        assert "Result   : PASS" in report_text
    """
).lstrip()

target_path.write_text(content, encoding="utf-8")
print(str(target_path))