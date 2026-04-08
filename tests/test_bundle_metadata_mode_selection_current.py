from __future__ import annotations

from pathlib import Path

from patchops.bundles.authoring import (
    create_starter_bundle,
    resolve_bundle_execution_metadata,
    resolve_bundle_workflow_mode,
)


def test_resolve_bundle_execution_metadata_reads_required_paths_from_bundle_meta(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "apply_bundle",
        patch_name="metadata_apply_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
        mode="apply",
    )

    metadata = resolve_bundle_execution_metadata(result.bundle_root)

    assert metadata.bundle_root == result.bundle_root.resolve()
    assert metadata.bundle_mode == "apply"
    assert metadata.manifest_path == result.manifest_path.resolve()
    assert metadata.content_root == result.content_root.resolve()
    assert metadata.launcher_path == result.launcher_path.resolve()
    assert metadata.recommended_profile == "generic_python"


def test_resolve_bundle_workflow_mode_uses_verify_only_for_verify_metadata(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "verify_bundle",
        patch_name="metadata_verify_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
        mode="verify",
    )

    metadata = resolve_bundle_execution_metadata(result.bundle_root)

    assert metadata.bundle_mode == "verify"
    assert resolve_bundle_workflow_mode(metadata) == "verify"


def test_apply_and_verify_bundles_share_the_same_saved_root_launcher_shape(tmp_path: Path) -> None:
    apply_bundle = create_starter_bundle(
        tmp_path / "apply_bundle",
        patch_name="shared_launcher_apply",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
        mode="apply",
    )
    verify_bundle = create_starter_bundle(
        tmp_path / "verify_bundle",
        patch_name="shared_launcher_verify",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
        mode="verify",
    )

    apply_launcher = apply_bundle.launcher_path.read_text(encoding="utf-8")
    verify_launcher = verify_bundle.launcher_path.read_text(encoding="utf-8")

    assert apply_launcher == verify_launcher
    assert "bundle-entry" in apply_launcher
    assert "apply $manifestPath" not in apply_launcher
    assert "verify $manifestPath" not in apply_launcher


def test_proof_mode_still_resolves_to_apply_workflow_from_metadata(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "proof_bundle",
        patch_name="metadata_proof_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
        mode="proof",
    )

    metadata = resolve_bundle_execution_metadata(result.bundle_root)

    assert metadata.bundle_mode == "proof"
    assert resolve_bundle_workflow_mode(metadata) == "apply"
