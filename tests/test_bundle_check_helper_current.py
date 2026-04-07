from __future__ import annotations

import json
from pathlib import Path
import zipfile

from patchops.bundles import BundleCheckResult, check_bundle_archive, check_bundle_zip


def _write_bundle_zip(bundle_zip_path: Path, members: dict[str, str]) -> None:
    with zipfile.ZipFile(bundle_zip_path, "w") as archive:
        for relative_path, text in members.items():
            archive.writestr(relative_path, text)


def _bundle_meta(*, patch_name: str = "demo_bundle") -> str:
    return json.dumps(
        {
            "bundle_schema_version": 1,
            "patch_name": patch_name,
            "target_project": "patchops",
            "recommended_profile": "generic_python",
            "target_project_root": "C:/dev/patchops",
            "wrapper_project_root": "C:/dev/patchops",
            "content_root": "content",
            "manifest_path": "manifest.json",
            "launcher_path": "run_with_patchops.ps1",
        }
    )


def _manifest(*, content_path: str = "content/docs/note.md") -> str:
    return json.dumps(
        {
            "manifest_version": "1",
            "patch_name": "demo_bundle",
            "active_profile": "generic_python",
            "files_to_write": [
                {
                    "path": "docs/note.md",
                    "content_path": content_path,
                    "encoding": "utf-8",
                }
            ],
        }
    )


def test_check_bundle_zip_returns_valid_result_for_flat_archive(tmp_path: Path) -> None:
    bundle_zip_path = tmp_path / "demo_bundle.zip"
    _write_bundle_zip(
        bundle_zip_path,
        {
            "manifest.json": _manifest(),
            "bundle_meta.json": _bundle_meta(),
            "run_with_patchops.ps1": "& { py -m patchops.cli apply .\\manifest.json }",
            "content/docs/note.md": "demo note\n",
        },
    )

    result = check_bundle_zip(bundle_zip_path, tmp_path, timestamp_token="20260404_220500")

    assert isinstance(result, BundleCheckResult)
    assert result.is_valid is True
    assert result.validation.metadata is not None
    assert result.validation.metadata.patch_name == "demo_bundle"
    assert result.extraction.was_flat_archive is True
    assert result.extraction.run_root.name == "demo_bundle_20260404_220500"
    assert result.bundle_root == result.extraction.extracted_root


def test_check_bundle_zip_flags_missing_manifest_after_extraction(tmp_path: Path) -> None:
    bundle_zip_path = tmp_path / "broken_bundle.zip"
    _write_bundle_zip(
        bundle_zip_path,
        {
            "bundle_meta.json": _bundle_meta(patch_name="broken_bundle"),
            "run_with_patchops.ps1": "& { py -m patchops.cli apply .\\manifest.json }",
            "content/docs/note.md": "demo note\n",
        },
    )

    result = check_bundle_zip(bundle_zip_path, tmp_path, timestamp_token="20260404_220501")

    assert result.is_valid is False
    error_codes = {item.code for item in result.validation.errors}
    assert "manifest_missing" in error_codes


def test_check_bundle_zip_keeps_single_root_folder_archives_compatible(tmp_path: Path) -> None:
    bundle_zip_path = tmp_path / "single_root_bundle.zip"
    _write_bundle_zip(
        bundle_zip_path,
        {
            "single_root_bundle/manifest.json": _manifest(),
            "single_root_bundle/bundle_meta.json": _bundle_meta(patch_name="single_root_bundle"),
            "single_root_bundle/run_with_patchops.ps1": "& { py -m patchops.cli apply .\\manifest.json }",
            "single_root_bundle/content/docs/note.md": "demo note\n",
        },
    )

    result = check_bundle_archive(bundle_zip_path, tmp_path, timestamp_token="20260404_220502")

    assert result.is_valid is True
    assert result.extraction.was_flat_archive is False
    assert result.bundle_root.name == "single_root_bundle"


def test_check_bundle_zip_surfaces_missing_content_path_reference(tmp_path: Path) -> None:
    bundle_zip_path = tmp_path / "missing_content_ref_bundle.zip"
    _write_bundle_zip(
        bundle_zip_path,
        {
            "manifest.json": _manifest(content_path="content/docs/missing_note.md"),
            "bundle_meta.json": _bundle_meta(patch_name="missing_content_ref_bundle"),
            "run_with_patchops.ps1": "& { py -m patchops.cli apply .\\manifest.json }",
            "content/docs/note.md": "demo note\n",
        },
    )

    result = check_bundle_zip(bundle_zip_path, tmp_path, timestamp_token="20260404_220503")

    assert result.is_valid is False
    error_codes = {item.code for item in result.validation.errors}
    assert "content_path_missing" in error_codes
