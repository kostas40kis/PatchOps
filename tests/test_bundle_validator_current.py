from __future__ import annotations

import json
from pathlib import Path

from patchops.bundles.validator import BundleValidationResult, validate_extracted_bundle_dir


def _write_standard_bundle_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "content" / "docs").mkdir(parents=True, exist_ok=True)
    (root / "content" / "docs" / "example.md").write_text("# example\n", encoding="utf-8")
    (root / "run_with_patchops.ps1").write_text("& {\n    \"ok\"\n}\n", encoding="utf-8")
    (root / "bundle_meta.json").write_text(
        json.dumps(
            {
                "bundle_schema_version": 1,
                "patch_name": "patch_06_bundle_validator_core",
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
                "patch_name": "patch_06_bundle_validator_core",
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
                    "report_name_prefix": "patch_06_bundle_validator_core",
                    "write_to_desktop": True,
                },
            }
        ),
        encoding="utf-8",
    )


def test_validate_extracted_bundle_dir_accepts_valid_bundle(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)

    result = validate_extracted_bundle_dir(tmp_path)

    assert isinstance(result, BundleValidationResult)
    assert result.is_valid is True
    assert result.errors == ()
    assert result.metadata is not None
    assert result.metadata.patch_name == "patch_06_bundle_validator_core"


def test_validate_extracted_bundle_dir_reports_missing_required_entries(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "manifest.json").write_text("{}", encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)
    codes = {message.code for message in result.errors}

    assert result.is_valid is False
    assert "bundle_meta_missing" in codes
    assert "content_root_missing" in codes
    assert "launcher_missing" in codes


def test_validate_extracted_bundle_dir_reports_duplicate_nested_root(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    nested = tmp_path / tmp_path.name
    nested.mkdir(parents=True, exist_ok=True)
    (nested / "manifest.json").write_text("{}", encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)
    codes = {message.code for message in result.errors}

    assert "duplicate_nested_root" in codes


def test_validate_extracted_bundle_dir_reports_missing_content_path_reference(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    manifest["files_to_write"][0]["content_path"] = "content/docs/missing.md"
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)
    codes = {message.code for message in result.errors}

    assert result.is_valid is False
    assert "content_path_missing" in codes


def test_validate_extracted_bundle_dir_reports_missing_content_subdirectory(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    manifest["files_to_write"][0]["content_path"] = "content/tests/test_missing_stage.py"
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)
    codes = {message.code for message in result.errors}

    assert result.is_valid is False
    assert "content_subdirectory_missing" in codes
    assert "content_path_missing" in codes


def test_validate_extracted_bundle_dir_reports_invalid_python_helper_syntax(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    (tmp_path / "prepare_patch.py").write_text("def broken(:\n    pass\n", encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)
    codes = {message.code for message in result.errors}

    assert result.is_valid is False
    assert "helper_python_syntax_invalid" in codes


def test_validate_extracted_bundle_dir_accepts_legacy_launcher_path_from_metadata(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    (tmp_path / "run_with_patchops.ps1").unlink()
    legacy_launcher = tmp_path / "launchers" / "apply_with_patchops.ps1"
    legacy_launcher.parent.mkdir(parents=True, exist_ok=True)
    legacy_launcher.write_text("param([string]$WrapperRepoRoot)\nWrite-Output 'legacy'\n", encoding="utf-8")

    metadata = json.loads((tmp_path / "bundle_meta.json").read_text(encoding="utf-8"))
    metadata["launcher_path"] = "launchers/apply_with_patchops.ps1"
    (tmp_path / "bundle_meta.json").write_text(json.dumps(metadata), encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)

    assert result.is_valid is True
    assert result.errors == ()
