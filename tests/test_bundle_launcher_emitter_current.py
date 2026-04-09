from __future__ import annotations

from pathlib import Path

from patchops.bundles.launcher_emitter import (
    METADATA_DRIVEN_LAUNCHER_MODE,
    ROOT_BUNDLE_LAUNCHER_NAME,
    emit_root_bundle_launcher,
    render_root_bundle_launcher,
    resolve_root_bundle_launcher_path,
)
from patchops.bundles.launcher_self_check import check_launcher_path


def test_render_root_bundle_launcher_preserves_saved_script_file_shape() -> None:
    script = render_root_bundle_launcher()

    assert script.startswith("param(")
    assert not script.startswith("& {")
    assert "[string]$WrapperRepoRoot" in script
    assert "$bundleRoot = Split-Path -Parent $PSCommandPath" in script
    assert '$bundleMetaPath = Join-Path $bundleRoot "bundle_meta.json"' in script
    assert 'throw ("bundle_meta.json not found: {0}" -f $bundleMetaPath)' in script
    assert "py -m patchops.cli bundle-entry $bundleRoot --wrapper-root $WrapperRepoRoot" in script
    assert "exit $LASTEXITCODE" in script
    assert "py -m patchops.cli apply $manifestPath" not in script
    assert "py -m patchops.cli verify $manifestPath" not in script
    assert script.endswith("\n")
    assert "\r" not in script
    assert not script.lstrip().startswith(("/", "\\"))


def test_emit_root_bundle_launcher_writes_canonical_filename_and_round_trips_through_self_check(tmp_path: Path) -> None:
    result = emit_root_bundle_launcher(tmp_path / "starter_bundle")

    assert result.launcher_path.name == ROOT_BUNDLE_LAUNCHER_NAME
    assert result.launcher_path.exists()
    assert result.mode == METADATA_DRIVEN_LAUNCHER_MODE
    assert result.ok is True
    assert result.issue_count == 0
    assert result.issues == ()

    launcher_text = result.launcher_path.read_text(encoding="utf-8")
    assert launcher_text.startswith("param(")
    assert "py -m patchops.cli bundle-entry $bundleRoot --wrapper-root $WrapperRepoRoot" in launcher_text
    assert '$bundleMetaPath = Join-Path $bundleRoot "bundle_meta.json"' in launcher_text
    assert "bundle_meta.json not found" in launcher_text
    assert "exit $LASTEXITCODE" in launcher_text
    assert "py -m patchops.cli verify $manifestPath" not in launcher_text
    assert "py -m patchops.cli apply $manifestPath" not in launcher_text

    payload = check_launcher_path(result.launcher_path)
    assert payload["ok"] is True
    assert payload["issue_count"] == 0
    assert payload["issues"] == []


def test_emit_root_bundle_launcher_can_still_emit_explicit_verify_shape_for_compatibility(tmp_path: Path) -> None:
    result = emit_root_bundle_launcher(tmp_path / "compat_bundle", mode="verify")

    assert result.mode == "verify"
    launcher_text = result.launcher_path.read_text(encoding="utf-8")
    assert launcher_text.startswith("param(")
    assert "py -m patchops.cli verify $manifestPath" in launcher_text
    assert "py -m patchops.cli apply $manifestPath" not in launcher_text


def test_resolve_root_bundle_launcher_path_accepts_bundle_root_or_explicit_launcher_path(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle_root"
    explicit = tmp_path / "custom" / ROOT_BUNDLE_LAUNCHER_NAME

    assert resolve_root_bundle_launcher_path(bundle_root) == bundle_root / ROOT_BUNDLE_LAUNCHER_NAME
    assert resolve_root_bundle_launcher_path(explicit) == explicit
