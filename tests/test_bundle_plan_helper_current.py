from __future__ import annotations

import json
from pathlib import Path
import zipfile

from patchops.bundles import BundlePlanResult, plan_bundle_archive, plan_bundle_zip


def _build_bundle_zip(tmp_path: Path, *, patch_name: str = "patch_10_demo") -> Path:
    bundle_root = tmp_path / patch_name
    content_root = bundle_root / "content"
    docs_root = content_root / "docs"
    tests_root = content_root / "tests"
    docs_root.mkdir(parents=True)
    tests_root.mkdir(parents=True)

    (bundle_root / "run_with_patchops.ps1").write_text(
        "& { py -m patchops.cli apply .\\manifest.json }\n",
        encoding="utf-8",
    )
    (docs_root / "note.md").write_text("# note\n", encoding="utf-8")
    (tests_root / "test_note_current.py").write_text(
        "def test_note():\n    assert True\n",
        encoding="utf-8",
    )

    metadata = {
        "bundle_schema_version": 1,
        "patch_name": patch_name,
        "target_project": "patchops",
        "recommended_profile": "generic_python",
        "target_project_root": "C:\\dev\\patchops",
        "wrapper_project_root": "C:\\dev\\patchops",
        "content_root": "content",
        "manifest_path": "manifest.json",
        "launcher_path": "run_with_patchops.ps1",
    }
    (bundle_root / "bundle_meta.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "manifest_version": 1,
        "patch_name": patch_name,
        "active_profile": "generic_python",
        "target_project_root": "C:\\dev\\patchops",
        "files_to_write": [
            {
                "path": "docs\\note.md",
                "content_path": "content/docs/note.md",
            },
            {
                "path": "tests\\test_note_current.py",
                "content_path": "content/tests/test_note_current.py",
            },
        ],
        "validation_commands": [
            {
                "name": "demo_contract",
                "program": "py",
                "args": ["-m", "pytest", "-q", "tests/test_note_current.py"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
    }
    (bundle_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    zip_path = tmp_path / f"{patch_name}.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in bundle_root.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(bundle_root))
    return zip_path


def test_bundle_plan_helper_exports_are_available() -> None:
    assert BundlePlanResult is not None
    assert plan_bundle_zip is not None
    assert plan_bundle_archive is plan_bundle_zip


def test_plan_bundle_zip_returns_reviewable_bundle_plan(tmp_path: Path) -> None:
    zip_path = _build_bundle_zip(tmp_path)
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()

    result = plan_bundle_zip(zip_path, wrapper_root, timestamp_token="20260404_224900")

    assert result.is_valid is True
    assert result.metadata is not None
    assert result.metadata.patch_name == "patch_10_demo"
    assert result.write_targets == ("docs\\note.md", "tests\\test_note_current.py")
    assert result.backup_targets == result.write_targets
    assert result.validation_command_names == ("demo_contract",)
    assert result.resolved_profile == "generic_python"
    assert result.target_project_root == "C:\\dev\\patchops"
    assert result.report_path_preview is not None
    assert result.report_path_preview.endswith("patch_10_demo_bundle_plan.txt")


def test_plan_bundle_zip_returns_empty_plan_when_bundle_is_invalid(tmp_path: Path) -> None:
    zip_path = _build_bundle_zip(tmp_path, patch_name="patch_10_invalid")
    broken_dir = tmp_path / "broken_bundle"
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(broken_dir)
    (broken_dir / "manifest.json").unlink()

    broken_zip = tmp_path / "patch_10_invalid_broken.zip"
    with zipfile.ZipFile(broken_zip, "w") as archive:
        for path in broken_dir.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(broken_dir))

    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()

    result = plan_bundle_zip(broken_zip, wrapper_root, timestamp_token="20260404_224901")

    assert result.is_valid is False
    assert result.write_targets == ()
    assert result.backup_targets == ()
    assert result.validation_command_names == ()
    assert result.resolved_profile is None
    assert result.target_project_root is None
    assert result.report_path_preview is None
