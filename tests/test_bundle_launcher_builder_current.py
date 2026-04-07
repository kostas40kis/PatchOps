from __future__ import annotations

from patchops.bundles.launcher_builder import (
    build_patchops_bundle_launcher,
    build_run_package_bundle_root_launcher,
    ensure_powershell_block_wrapped,
)


def test_build_patchops_bundle_launcher_apply_mode_uses_safe_shape() -> None:
    script = build_patchops_bundle_launcher(
        launcher_directory_relative_to_bundle_root=True,
    )

    assert script.startswith("& {")
    assert "[string]$WrapperRepoRoot" in script
    assert "$bundleRoot = (Split-Path -Parent $PSScriptRoot)" in script
    assert "py -m patchops.cli apply $manifestPath" in script
    assert "py -m patchops.cli inspect $manifestPath" in script
    assert "py -m patchops.cli plan $manifestPath" in script
    assert not script.lstrip().startswith(("/", "\\"))
    assert "ProcessStartInfo.ArgumentList" not in script


def test_build_patchops_bundle_launcher_verify_mode_uses_verify_command() -> None:
    script = build_patchops_bundle_launcher(
        mode="verify",
        launcher_directory_relative_to_bundle_root=True,
    )

    assert "py -m patchops.cli verify $manifestPath" in script


def test_build_patchops_bundle_launcher_can_skip_wrapper_for_manual_audit_shapes() -> None:
    script = build_patchops_bundle_launcher(
        mode="apply",
        launcher_directory_relative_to_bundle_root=True,
        safe_wrapper_mode="never",
    )

    assert script.startswith("param(")
    assert not script.startswith("& {")


def test_build_run_package_bundle_root_launcher_calls_run_package() -> None:
    script = build_run_package_bundle_root_launcher()

    assert script.startswith("& {")
    assert "[string]$WrapperRepoRoot" in script
    assert "$bundleRoot = $PSScriptRoot" in script
    assert "py -m patchops.cli run-package $bundleRoot --wrapper-root $WrapperRepoRoot" in script
    assert "Push-Location -LiteralPath $WrapperRepoRoot" in script
    assert "Pop-Location" in script


def test_wrapper_helper_adds_ampersand_block_only_when_missing() -> None:
    wrapped = ensure_powershell_block_wrapped("Write-Host 'hello'")
    already = ensure_powershell_block_wrapped("& {\n    Write-Host 'hello'\n}\n")

    assert wrapped.startswith("& {")
    assert wrapped.rstrip().endswith("}")
    assert already.startswith("& {")
    assert already.count("& {") == 1
