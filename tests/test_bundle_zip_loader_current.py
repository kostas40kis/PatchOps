from __future__ import annotations

from pathlib import Path
import zipfile

from patchops.bundles.zip_loader import (
    BUNDLE_RUN_ROOT_RELATIVE,
    EXTRACTED_BUNDLE_DIR_NAME,
    build_bundle_run_root,
    extract_bundle_zip,
    sanitize_bundle_name_from_zip,
)


def _write_zip(zip_path: Path, members: dict[str, str]) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w") as archive:
        for name, content in members.items():
            archive.writestr(name, content)


def test_sanitize_bundle_name_from_zip_is_stable() -> None:
    bundle_zip = Path("patch 07:bundle?.zip")
    assert sanitize_bundle_name_from_zip(bundle_zip) == "patch_07_bundle"


def test_build_bundle_run_root_uses_deterministic_runtime_location(tmp_path: Path) -> None:
    bundle_zip = tmp_path / "example_bundle.zip"
    run_root = build_bundle_run_root(tmp_path, bundle_zip, timestamp_token="20260404_221500")

    assert run_root == tmp_path / BUNDLE_RUN_ROOT_RELATIVE / "example_bundle_20260404_221500"


def test_extract_bundle_zip_supports_flat_archive_export(tmp_path: Path) -> None:
    bundle_zip = tmp_path / "flat_bundle.zip"
    _write_zip(
        bundle_zip,
        {
            "manifest.json": "{}",
            "bundle_meta.json": "{}",
            "README.txt": "bundle",
            "run_with_patchops.ps1": "& { Write-Host ok }",
            "content/docs/note.md": "ok\n",
        },
    )

    result = extract_bundle_zip(bundle_zip, tmp_path, timestamp_token="20260404_221501")

    assert result.was_flat_archive is True
    assert result.bundle_root == result.extracted_root
    assert result.bundle_root.name == EXTRACTED_BUNDLE_DIR_NAME
    assert (result.bundle_root / "manifest.json").exists()
    assert (result.bundle_root / "run_with_patchops.ps1").exists()
    assert (result.bundle_root / "content" / "docs" / "note.md").exists()


def test_extract_bundle_zip_supports_legacy_single_root_folder_archives(tmp_path: Path) -> None:
    bundle_zip = tmp_path / "legacy_bundle.zip"
    _write_zip(
        bundle_zip,
        {
            "legacy_bundle/manifest.json": "{}",
            "legacy_bundle/bundle_meta.json": "{}",
            "legacy_bundle/README.txt": "bundle",
            "legacy_bundle/run_with_patchops.ps1": "& { Write-Host ok }",
            "legacy_bundle/content/tests/test_note.py": "def test_ok():\n    assert True\n",
        },
    )

    result = extract_bundle_zip(bundle_zip, tmp_path, timestamp_token="20260404_221502")

    assert result.was_flat_archive is False
    assert result.bundle_root == result.extracted_root / "legacy_bundle"
    assert (result.bundle_root / "manifest.json").exists()
    assert (result.bundle_root / "run_with_patchops.ps1").exists()


def test_extract_bundle_zip_rejects_unsafe_members(tmp_path: Path) -> None:
    bundle_zip = tmp_path / "unsafe_bundle.zip"
    _write_zip(
        bundle_zip,
        {
            "../escape.txt": "bad",
            "manifest.json": "{}",
        },
    )

    try:
        extract_bundle_zip(bundle_zip, tmp_path, timestamp_token="20260404_221503")
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected unsafe member rejection")

    assert "Unsafe bundle zip member" in message
