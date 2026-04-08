from __future__ import annotations

import json
from pathlib import Path

from patchops.bundles.authoring import create_starter_bundle
from patchops.bundles.launcher_emitter import METADATA_DRIVEN_LAUNCHER_MODE, render_root_bundle_launcher
from patchops.bundles.launcher_self_check import check_launcher_path


def test_create_starter_bundle_writes_required_root_files(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "starter_bundle",
        patch_name="zp18_demo_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
    )

    assert result.bundle_root.exists()
    assert result.content_root.exists()
    assert result.manifest_path.exists()
    assert result.bundle_meta_path.exists()
    assert result.readme_path.exists()
    assert result.launcher_path.exists()

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["patch_name"] == "zp18_demo_bundle"
    assert manifest["active_profile"] == "generic_python"
    assert manifest["target_project_root"] == "C:/dev/patchops"
    assert manifest["files_to_write"] == []
    assert manifest["validation_commands"] == []
    assert manifest["report_preferences"]["report_name_prefix"] == "zp18_demo_bundle"

    bundle_meta = json.loads(result.bundle_meta_path.read_text(encoding="utf-8"))
    assert bundle_meta["patch_name"] == "zp18_demo_bundle"
    assert bundle_meta["target_project"] == "patchops"
    assert bundle_meta["recommended_profile"] == "generic_python"
    assert bundle_meta["manifest_path"] == "manifest.json"
    assert bundle_meta["launcher_path"] == "run_with_patchops.ps1"
    assert bundle_meta["content_root"] == "content"
    assert bundle_meta["bundle_mode"] == "apply"

    launcher_text = result.launcher_path.read_text(encoding="utf-8")
    assert launcher_text.startswith("param(")
    assert launcher_text == render_root_bundle_launcher(mode=METADATA_DRIVEN_LAUNCHER_MODE)
    assert "py -m patchops.cli bundle-entry $bundleRoot --wrapper-root $WrapperRepoRoot" in launcher_text
    assert "py -m patchops.cli apply $manifestPath" not in launcher_text
    assert "py -m patchops.cli verify $manifestPath" not in launcher_text

    payload = check_launcher_path(result.launcher_path)
    assert payload["ok"] is True
    assert payload["issue_count"] == 0


def test_create_starter_bundle_supports_verify_mode_and_custom_profile(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "verify_bundle",
        patch_name="zp18_verify_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
        wrapper_project_root="C:/work/custom_wrapper",
        recommended_profile="generic_python_powershell",
        mode="verify",
    )

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["active_profile"] == "generic_python_powershell"

    bundle_meta = json.loads(result.bundle_meta_path.read_text(encoding="utf-8"))
    assert bundle_meta["wrapper_project_root"] == "C:/work/custom_wrapper"
    assert bundle_meta["recommended_profile"] == "generic_python_powershell"
    assert bundle_meta["bundle_mode"] == "verify"

    launcher_text = result.launcher_path.read_text(encoding="utf-8")
    assert launcher_text.startswith("param(")
    assert launcher_text == render_root_bundle_launcher(mode=METADATA_DRIVEN_LAUNCHER_MODE, wrapper_project_root="C:/work/custom_wrapper")
    assert "py -m patchops.cli bundle-entry $bundleRoot --wrapper-root $WrapperRepoRoot" in launcher_text
    assert "py -m patchops.cli verify $manifestPath" not in launcher_text
    assert "py -m patchops.cli apply $manifestPath" not in launcher_text
