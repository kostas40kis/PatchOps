from __future__ import annotations

import json
from pathlib import Path

from patchops.bundles.validator import validate_extracted_bundle_dir


def _write_standard_bundle_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "content" / "docs").mkdir(parents=True, exist_ok=True)
    (root / "content" / "docs" / "example.md").write_text("# example\n", encoding="utf-8")
    (root / "run_with_patchops.ps1").write_text("param([string]$WrapperRepoRoot)\nWrite-Output 'ok'\n", encoding="utf-8")
    (root / "bundle_meta.json").write_text(
        json.dumps(
            {
                "bundle_schema_version": 1,
                "patch_name": "patch_33_generated_helper_syntax_gate",
                "target_project": "patchops",
                "recommended_profile": "generic_python",
                "target_project_root": r"C:\dev\patchops",
                "wrapper_project_root": r"C:\dev\patchops",
                "content_root": "content",
                "manifest_path": "manifest.json",
                "launcher_path": "run_with_patchops.ps1",
            }
        ),
        encoding="utf-8",
    )
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "manifest_version": "1",
                "patch_name": "patch_33_generated_helper_syntax_gate",
                "active_profile": "generic_python",
                "target_project_root": "C:/dev/patchops",
                "files_to_write": [
                    {
                        "path": "docs/example.md",
                        "content": None,
                        "content_path": "content/docs/example.md",
                        "encoding": "utf-8",
                    }
                ],
                "validation_commands": [],
                "smoke_commands": [],
                "audit_commands": [],
                "cleanup_commands": [],
                "archive_commands": [],
                "failure_policy": {},
                "report_preferences": {
                    "report_dir": None,
                    "report_name_prefix": "patch_33_generated_helper_syntax_gate",
                    "write_to_desktop": True,
                },
            }
        ),
        encoding="utf-8",
    )


def test_validate_extracted_bundle_dir_reports_invalid_generated_python_helper(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    helper_path = tmp_path / "content" / "generated" / "prepare_patch.py"
    helper_path.parent.mkdir(parents=True, exist_ok=True)
    helper_path.write_text("def broken(:\n    pass\n", encoding="utf-8")

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    manifest["files_to_write"].append(
        {
            "path": "generated/prepare_patch.py",
            "content": None,
            "content_path": "content/generated/prepare_patch.py",
            "encoding": "utf-8",
        }
    )
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)
    codes = {message.code for message in result.errors}

    assert result.is_valid is False
    assert "generated_python_syntax_invalid" in codes


def test_validate_extracted_bundle_dir_reports_invalid_generated_test_file(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    test_path = tmp_path / "content" / "tests" / "test_generated_surface.py"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text("def test_generated():\nassert True\n", encoding="utf-8")

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    manifest["files_to_write"].append(
        {
            "path": "tests/test_generated_surface.py",
            "content": None,
            "content_path": "content/tests/test_generated_surface.py",
            "encoding": "utf-8",
        }
    )
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)
    codes = {message.code for message in result.errors}

    assert result.is_valid is False
    assert "generated_python_syntax_invalid" in codes


def test_validate_extracted_bundle_dir_accepts_clean_generated_python_helper(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    helper_path = tmp_path / "content" / "generated" / "prepare_patch.py"
    helper_path.parent.mkdir(parents=True, exist_ok=True)
    helper_path.write_text("def helper() -> str:\n    return 'ok'\n", encoding="utf-8")

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    manifest["files_to_write"].append(
        {
            "path": "generated/prepare_patch.py",
            "content": None,
            "content_path": "content/generated/prepare_patch.py",
            "encoding": "utf-8",
        }
    )
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)

    assert result.is_valid is True
    assert result.errors == ()


def test_validate_extracted_bundle_dir_reports_unsafe_generated_powershell_shape(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    ps1_path = tmp_path / "content" / "helpers" / "generated_runner.ps1"
    ps1_path.parent.mkdir(parents=True, exist_ok=True)
    ps1_path.write_text("& {\n    [CmdletBinding()]\n    param([string]$Value)\n    Write-Output $Value\n}\n", encoding="utf-8")

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    manifest["files_to_write"].append(
        {
            "path": "helpers/generated_runner.ps1",
            "content": None,
            "content_path": "content/helpers/generated_runner.ps1",
            "encoding": "utf-8",
        }
    )
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)
    codes = {message.code for message in result.errors}

    assert result.is_valid is False
    assert "generated_powershell_shape_invalid" in codes
