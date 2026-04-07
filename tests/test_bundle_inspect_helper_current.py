from __future__ import annotations

import json
from pathlib import Path
import zipfile

from patchops.bundles import BundleInspectResult, inspect_bundle_archive, inspect_bundle_zip


REQUIRED_ROOT_FILES = (
    "bundle_meta.json",
    "manifest.json",
    "run_with_patchops.ps1",
)


def _build_bundle_zip(tmp_path: Path, *, patch_name: str = "patch_09_demo") -> Path:
    bundle_root = tmp_path / patch_name
    content_root = bundle_root / "content"
    docs_root = content_root / "docs"
    tests_root = content_root / "tests"
    docs_root.mkdir(parents=True)
    tests_root.mkdir(parents=True)

    (bundle_root / "run_with_patchops.ps1").write_text("& { py -m patchops.cli apply .\\manifest.json }\n", encoding="utf-8")
    (docs_root / "note.md").write_text("# note\n", encoding="utf-8")
    (tests_root / "test_note_current.py").write_text("def test_note():\n    assert True\n", encoding="utf-8")

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
                "target_path": "docs\\note.md",
                "content_path": "content/docs/note.md",
            },
            {
                "target_path": "tests\\test_note_current.py",
                "content_path": "content/tests/test_note_current.py",
            },
        ],
        "validation_commands": [
            {
                "name": "demo_contract",
                "command": ["py", "-m", "pytest", "-q", "tests/test_note_current.py"],
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


def test_bundle_inspect_helper_exports_are_available() -> None:
    assert BundleInspectResult is not None
    assert inspect_bundle_zip is not None
    assert inspect_bundle_archive is inspect_bundle_zip


def test_inspect_bundle_zip_returns_targets_and_validation_command_names(tmp_path: Path) -> None:
    zip_path = _build_bundle_zip(tmp_path)
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()

    result = inspect_bundle_zip(zip_path, wrapper_root, timestamp_token="20260404_222600")

    assert result.is_valid is True
    assert result.resolved_layout is not None
    assert result.metadata is not None
    assert result.metadata.patch_name == "patch_09_demo"
    assert result.target_paths == ("docs\\note.md", "tests\\test_note_current.py")
    assert result.validation_command_names == ("demo_contract",)
    assert result.resolved_layout.manifest_path.exists()
    for root_name in REQUIRED_ROOT_FILES:
        assert (result.bundle_root / root_name).exists()


def test_inspect_bundle_zip_returns_empty_manifest_details_when_validation_fails(tmp_path: Path) -> None:
    zip_path = _build_bundle_zip(tmp_path, patch_name="patch_09_invalid")
    broken_dir = tmp_path / "broken_bundle"
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(broken_dir)
    (broken_dir / "manifest.json").unlink()

    broken_zip = tmp_path / "patch_09_invalid_broken.zip"
    with zipfile.ZipFile(broken_zip, "w") as archive:
        for path in broken_dir.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(broken_dir))

    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()

    result = inspect_bundle_zip(broken_zip, wrapper_root, timestamp_token="20260404_222601")

    assert result.is_valid is False
    assert result.resolved_layout is None
    assert result.target_paths == ()
    assert result.validation_command_names == ()
    assert result.check.validation.errors
