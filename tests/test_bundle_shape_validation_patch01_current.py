from __future__ import annotations

from pathlib import Path
import zipfile

from patchops.bundles.shape_validation import (
    validate_bundle_directory,
    validate_bundle_path,
    validate_bundle_zip,
)


def _canonical_zip_members(root_name: str = "demo_bundle") -> dict[str, str]:
    return {
        f"{root_name}/manifest.json": '{"patch_name": "demo"}\n',
        f"{root_name}/bundle_meta.json": '{"bundle_schema_version": 1, "bundle_mode": "apply"}\n',
        f"{root_name}/README.txt": "demo\n",
        f"{root_name}/content/example.txt": "hello\n",
        f"{root_name}/run_with_patchops.ps1": "Write-Host ok\n",
    }


def _legacy_zip_members(root_name: str = "demo_bundle") -> dict[str, str]:
    return {
        f"{root_name}/manifest.json": '{"patch_name": "demo"}\n',
        f"{root_name}/bundle_meta.json": '{"bundle_schema_version": 1, "bundle_mode": "apply"}\n',
        f"{root_name}/content/example.txt": "hello\n",
        f"{root_name}/launchers/apply_with_patchops.ps1": "Write-Host ok\n",
    }


def _write_zip(tmp_path: Path, members: dict[str, str], zip_name: str = "bundle.zip") -> Path:
    zip_path = tmp_path / zip_name
    with zipfile.ZipFile(zip_path, "w") as archive:
        for member_name, content in members.items():
            archive.writestr(member_name, content)
    return zip_path


def test_validate_bundle_zip_accepts_canonical_root_single_launcher_shape(tmp_path: Path) -> None:
    zip_path = _write_zip(tmp_path, _canonical_zip_members())
    result = validate_bundle_zip(zip_path)

    assert result.ok is True
    assert result.issue_count == 0
    assert result.root_folder_name == "demo_bundle"
    assert result.manifest_path == "demo_bundle/manifest.json"
    assert result.bundle_meta_path == "demo_bundle/bundle_meta.json"
    assert result.content_root_path == "demo_bundle/content"
    assert result.launcher_paths == ["demo_bundle/run_with_patchops.ps1"]


def test_validate_bundle_directory_accepts_canonical_root_single_launcher_shape(tmp_path: Path) -> None:
    bundle_root = tmp_path / "demo_bundle"
    (bundle_root / "content").mkdir(parents=True)
    (bundle_root / "content" / "example.txt").write_text("hello\n", encoding="utf-8")
    (bundle_root / "manifest.json").write_text('{"patch_name": "demo"}\n', encoding="utf-8")
    (bundle_root / "bundle_meta.json").write_text('{"bundle_schema_version": 1, "bundle_mode": "apply"}\n', encoding="utf-8")
    (bundle_root / "run_with_patchops.ps1").write_text("Write-Host ok\n", encoding="utf-8")

    result = validate_bundle_directory(bundle_root)

    assert result.ok is True
    assert result.issue_count == 0
    assert result.root_folder_name == "demo_bundle"
    assert result.launcher_paths == ["run_with_patchops.ps1"]


def test_validate_bundle_zip_keeps_legacy_launchers_tolerated_for_compatibility(tmp_path: Path) -> None:
    zip_path = _write_zip(tmp_path, _legacy_zip_members())
    result = validate_bundle_zip(zip_path)

    assert result.ok is True
    assert result.issue_count == 0
    assert result.launcher_paths == ["demo_bundle/launchers/apply_with_patchops.ps1"]


def test_validate_bundle_zip_flags_wrong_launcher_location(tmp_path: Path) -> None:
    members = _canonical_zip_members()
    del members["demo_bundle/run_with_patchops.ps1"]
    members["demo_bundle/scripts/run_with_patchops.ps1"] = "Write-Host bad\n"
    zip_path = _write_zip(tmp_path, members)

    result = validate_bundle_zip(zip_path)

    assert result.ok is False
    assert any(issue.code == "wrong_launcher_location" for issue in result.issues)


def test_validate_bundle_directory_flags_wrong_launcher_location(tmp_path: Path) -> None:
    bundle_root = tmp_path / "demo_bundle"
    (bundle_root / "content").mkdir(parents=True)
    (bundle_root / "content" / "example.txt").write_text("hello\n", encoding="utf-8")
    (bundle_root / "manifest.json").write_text('{"patch_name": "demo"}\n', encoding="utf-8")
    (bundle_root / "bundle_meta.json").write_text('{"bundle_schema_version": 1, "bundle_mode": "apply"}\n', encoding="utf-8")
    (bundle_root / "scripts").mkdir(parents=True)
    (bundle_root / "scripts" / "run_with_patchops.ps1").write_text("Write-Host bad\n", encoding="utf-8")

    result = validate_bundle_directory(bundle_root)

    assert result.ok is False
    assert any(issue.code == "wrong_launcher_location" for issue in result.issues)


def test_validate_bundle_path_dispatches_for_canonical_root_launcher_shape(tmp_path: Path) -> None:
    zip_path = _write_zip(tmp_path, _canonical_zip_members())
    zip_result = validate_bundle_path(zip_path)

    bundle_root = tmp_path / "dir_bundle"
    (bundle_root / "content").mkdir(parents=True)
    (bundle_root / "content" / "example.txt").write_text("hello\n", encoding="utf-8")
    (bundle_root / "manifest.json").write_text('{"patch_name": "demo"}\n', encoding="utf-8")
    (bundle_root / "bundle_meta.json").write_text('{"bundle_schema_version": 1, "bundle_mode": "apply"}\n', encoding="utf-8")
    (bundle_root / "run_with_patchops.ps1").write_text("Write-Host ok\n", encoding="utf-8")
    dir_result = validate_bundle_path(bundle_root)

    assert zip_result.source_kind == "zip"
    assert dir_result.source_kind == "directory"
    assert zip_result.ok is True
    assert dir_result.ok is True
