from __future__ import annotations

from pathlib import Path

from patchops.bundles.launcher_formatter import (
    build_standard_bundle_launcher,
    ensure_safe_launcher_wrapper,
    format_bundle_launcher,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_example_launchers_remain_safely_wrapped_after_formatter_refactor() -> None:
    apply_text = _read("examples/bundles/example_generic_python_patch_bundle/launchers/apply_with_patchops.ps1")
    verify_text = _read("examples/bundles/example_generic_python_patch_bundle/launchers/verify_with_patchops.ps1")
    root_text = _read("examples/bundles/example_generic_python_patch_bundle/run_with_patchops.ps1")

    for text in (apply_text, verify_text, root_text):
        assert text.startswith("& {")
        assert text.endswith("}\n")
        assert not text.lstrip().startswith(("/", "\\"))


def test_wrapper_normalization_preserves_existing_safe_shape() -> None:
    current = "& {\n    Write-Host 'hi'\n}\n"

    assert ensure_safe_launcher_wrapper(current) == current
    result = format_bundle_launcher(current, safe_wrapper_mode="auto")
    assert result.script_text == current
    assert result.wrapper_normalized is False


def test_standard_builder_still_emits_safe_shape_by_default() -> None:
    script = build_standard_bundle_launcher()

    assert script.startswith("& {")
    assert "param(" in script
