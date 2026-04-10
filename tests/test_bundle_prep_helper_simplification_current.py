from __future__ import annotations

import json
from pathlib import Path

from patchops.bundles.validator import validate_extracted_bundle_dir


def _write_standard_bundle_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "content" / "docs").mkdir(parents=True, exist_ok=True)
    (root / "content" / "docs" / "example.md").write_text("# example\n", encoding="utf-8")
    (root / "run_with_patchops.ps1").write_text(
        "param([string]$WrapperRepoRoot)\nWrite-Output 'ok'\n",
        encoding="utf-8",
    )
    (root / "bundle_meta.json").write_text(
        json.dumps(
            {
                "bundle_schema_version": 1,
                "patch_name": "p38a_bundle_prep_helper_simplification_syntax_repair",
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
                "patch_name": "p38a_bundle_prep_helper_simplification_syntax_repair",
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
                    "report_name_prefix": "p38a_bundle_prep_helper_simplification_syntax_repair",
                    "write_to_desktop": True,
                },
            }
        ),
        encoding="utf-8",
    )


def test_validate_extracted_bundle_dir_accepts_single_language_pure_python_prep_helper(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    helper_path = tmp_path / "prepare_patch.py"
    helper_path.write_text("def build_patch() -> str:\n    return 'ok'\n", encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)

    assert result.is_valid is True
    assert result.errors == ()


def test_validate_extracted_bundle_dir_rejects_mixed_language_prep_helpers(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    (tmp_path / "prepare_patch.py").write_text("def build_patch() -> str:\n    return 'ok'\n", encoding="utf-8")
    (tmp_path / "prepare_patch.ps1").write_text("param([string]$Value)\nWrite-Output $Value\n", encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)
    codes = {message.code for message in result.errors}

    assert result.is_valid is False
    assert "mixed_prep_helper_languages_forbidden" in codes
    assert "powershell_prep_helper_forbidden" in codes


def test_validate_extracted_bundle_dir_rejects_multiple_python_prep_helpers(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    (tmp_path / "prepare_patch.py").write_text("def build_patch() -> str:\n    return 'ok'\n", encoding="utf-8")
    (tmp_path / "prepare_more.py").write_text("def build_more() -> str:\n    return 'ok'\n", encoding="utf-8")

    result = validate_extracted_bundle_dir(tmp_path)
    codes = {message.code for message in result.errors}

    assert result.is_valid is False
    assert "multiple_python_prep_helpers_forbidden" in codes


def test_validate_extracted_bundle_dir_rejects_python_prep_helper_with_powershell_syntax(tmp_path: Path) -> None:
    _write_standard_bundle_root(tmp_path)
    helper_path = tmp_path / "prepare_patch.py"
    helper_path.write_text(
        "def build_patch():\n"
        "    script = \"Write-Host 'bad'\"\n"
        "    return script\n",
        encoding="utf-8",
    )

    result = validate_extracted_bundle_dir(tmp_path)
    codes = {message.code for message in result.errors}

    assert result.is_valid is False
    assert "python_prep_helper_contains_powershell_syntax" in codes
