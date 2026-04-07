from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_example_bundle_launchers_match_safe_contract() -> None:
    apply_text = _read("examples/bundles/example_generic_python_patch_bundle/launchers/apply_with_patchops.ps1")
    verify_text = _read("examples/bundles/example_generic_python_patch_bundle/launchers/verify_with_patchops.ps1")
    root_text = _read("examples/bundles/example_generic_python_patch_bundle/run_with_patchops.ps1")

    for text in (apply_text, verify_text, root_text):
        assert text.startswith("& {")
        assert "[string]$WrapperRepoRoot" in text
        assert (
            "Push-Location -LiteralPath $WrapperRepoRoot" in text
            or "py -m patchops.cli run-package $bundleRoot --wrapper-root $WrapperRepoRoot" in text
        )
        assert not text.lstrip().startswith(("/", "\\"))
        assert "ProcessStartInfo.ArgumentList" not in text

    assert "$bundleRoot = (Split-Path -Parent $PSScriptRoot)" in apply_text
    assert "$bundleRoot = (Split-Path -Parent $PSScriptRoot)" in verify_text
    assert "$bundleRoot = $PSScriptRoot" in root_text
    assert "py -m patchops.cli apply $manifestPath" in apply_text
    assert "py -m patchops.cli verify $manifestPath" in verify_text
    assert "py -m patchops.cli run-package $bundleRoot --wrapper-root $WrapperRepoRoot" in root_text
