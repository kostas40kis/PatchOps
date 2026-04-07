from __future__ import annotations

import json
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_manifest(manifest_path: Path, manifest_data: dict) -> Path:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def _base_manifest(tmp_path: Path, patch_name: str) -> dict:
    target_root = tmp_path / "target_repo"
    report_dir = tmp_path / "reports"
    target_root.mkdir()
    report_dir.mkdir()

    return {
        "manifest_version": "1",
        "patch_name": patch_name,
        "active_profile": "generic_python",
        "target_project_root": str(target_root).replace("\\", "/"),
        "backup_files": [],
        "files_to_write": [],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir).replace("\\", "/"),
            "report_name_prefix": patch_name,
            "write_to_desktop": False,
        },
        "tags": ["test", "required_vs_tolerated", "report_truth"],
        "notes": "Temporary manifest used by the current required-versus-tolerated proof tests.",
    }


def test_required_command_failure_outside_allowed_exit_codes_renders_fail(tmp_path: Path) -> None:
    wrapper_root = PROJECT_ROOT
    manifest_data = _base_manifest(tmp_path, "required_failure_report_proof")
    manifest_data["validation_commands"] = [
        {
            "name": "required_fail",
            "program": "python",
            "args": ["-c", "import sys; print('required fail'); sys.exit(1)"],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        }
    ]

    manifest_path = _write_manifest(tmp_path / "required_failure_report_proof.json", manifest_data)
    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == "FAIL"
    assert result.exit_code == 1
    assert result.report_path.exists()

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "NAME    : required_fail" in report_text
    assert "ExitCode : 1" in report_text
    assert "Result   : FAIL" in report_text


def test_tolerated_non_zero_exit_still_renders_pass(tmp_path: Path) -> None:
    wrapper_root = PROJECT_ROOT
    manifest_data = _base_manifest(tmp_path, "tolerated_failure_report_proof")
    manifest_data["validation_commands"] = [
        {
            "name": "tolerated_non_zero",
            "program": "python",
            "args": ["-c", "import sys; print('tolerated non-zero'); sys.exit(3)"],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0, 3],
        }
    ]

    manifest_path = _write_manifest(tmp_path / "tolerated_failure_report_proof.json", manifest_data)
    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == "PASS"
    assert result.exit_code == 0
    assert result.report_path.exists()

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "NAME    : tolerated_non_zero" in report_text
    assert "ExitCode : 0" in report_text
    assert "Result   : PASS" in report_text


def test_first_required_failure_remains_sticky_even_if_later_required_command_succeeds(tmp_path: Path) -> None:
    wrapper_root = PROJECT_ROOT
    manifest_data = _base_manifest(tmp_path, "sticky_required_failure_report_proof")
    manifest_data["validation_commands"] = [
        {
            "name": "first_required_failure",
            "program": "python",
            "args": ["-c", "import sys; print('first required failure'); sys.exit(5)"],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        },
        {
            "name": "later_required_success",
            "program": "python",
            "args": ["-c", "print('later required success')"],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        },
    ]

    manifest_path = _write_manifest(tmp_path / "sticky_required_failure_report_proof.json", manifest_data)
    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == "FAIL"
    assert result.exit_code == 5
    assert result.report_path.exists()

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "NAME    : first_required_failure" in report_text
    assert "Result   : FAIL" in report_text
    assert "ExitCode : 5" in report_text
