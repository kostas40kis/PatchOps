from __future__ import annotations

from patchops.bundles.launcher_formatter import (
    DEFAULT_LAUNCHER_ENCODING,
    DEFAULT_LAUNCHER_NEWLINE,
    BundleLauncherFormatResult,
    SUPPORTED_SAFE_WRAPPER_MODES,
    apply_safe_wrapper_normalization,
    build_standard_bundle_launcher,
    ensure_safe_launcher_wrapper,
    format_bundle_launcher,
    is_launcher_safely_wrapped,
    needs_safe_launcher_wrapper,
    normalize_bundle_launcher_text,
    resolve_safe_wrapper_mode,
    strip_leading_launcher_artifacts,
)


def test_build_standard_bundle_launcher_matches_safe_shape() -> None:
    script = build_standard_bundle_launcher()

    assert script.startswith("& {")
    assert "param(" in script
    assert "[string]$WrapperRepoRoot" in script
    assert "py -m patchops.cli apply $manifestPath" in script
    assert "Push-Location -LiteralPath $WrapperRepoRoot" in script
    assert script.endswith("\n")
    assert "\r" not in script
    assert not script.lstrip().startswith(("/", "\\"))
    assert "ProcessStartInfo.ArgumentList" not in script


def test_build_standard_bundle_launcher_supports_verify_mode() -> None:
    script = build_standard_bundle_launcher(cli_mode="verify")

    assert "py -m patchops.cli verify $manifestPath" in script


def test_build_standard_bundle_launcher_can_emit_unwrapped_shape_when_requested() -> None:
    script = build_standard_bundle_launcher(safe_wrapper_mode="never")

    assert script.startswith("param(")
    assert not script.startswith("& {")


def test_strip_leading_launcher_artifacts_removes_stray_backslash_before_safe_block() -> None:
    dirty = "\\\n& {\n    Write-Host 'hi'\n}\n"

    cleaned = strip_leading_launcher_artifacts(dirty)

    assert cleaned.startswith("& {")


def test_normalize_bundle_launcher_text_removes_leading_backslash_and_normalizes_lines() -> None:
    dirty = "\\\r\n& {\n    Write-Host 'hi'   \n}\r\n\r\n"

    normalized = normalize_bundle_launcher_text(dirty)

    assert normalized == "& {\n    Write-Host 'hi'\n}\n"


def test_format_bundle_launcher_result_uses_standard_metadata() -> None:
    result = format_bundle_launcher()

    assert isinstance(result, BundleLauncherFormatResult)
    assert result.encoding == DEFAULT_LAUNCHER_ENCODING
    assert result.newline == DEFAULT_LAUNCHER_NEWLINE
    assert result.starts_with_safe_block is True
    assert result.script_text.startswith("& {")


def test_is_launcher_safely_wrapped_detects_wrapped_and_unwrapped_shapes() -> None:
    wrapped = "& {\n    Write-Host 'hi'\n}\n"
    unwrapped = "Write-Host 'hi'\n"

    assert is_launcher_safely_wrapped(wrapped) is True
    assert is_launcher_safely_wrapped(unwrapped) is False


def test_needs_safe_launcher_wrapper_detects_unwrapped_shape() -> None:
    wrapped = "& {\n    Write-Host 'hi'\n}\n"
    unwrapped = "param(\n    [string]$Name = 'x'\n)\n"

    assert needs_safe_launcher_wrapper(wrapped) is False
    assert needs_safe_launcher_wrapper(unwrapped) is True


def test_ensure_safe_launcher_wrapper_adds_block_when_missing() -> None:
    raw = "Write-Host 'hi'\nWrite-Host 'bye'\n"

    wrapped = ensure_safe_launcher_wrapper(raw)

    assert wrapped.startswith("& {\n")
    assert "    Write-Host 'hi'" in wrapped
    assert "    Write-Host 'bye'" in wrapped
    assert wrapped.endswith("}\n")


def test_ensure_safe_launcher_wrapper_does_not_double_wrap() -> None:
    wrapped = "& {\n    Write-Host 'hi'\n}\n"

    result = ensure_safe_launcher_wrapper(wrapped)

    assert result == wrapped


def test_resolve_safe_wrapper_mode_supports_boolean_backcompat() -> None:
    assert resolve_safe_wrapper_mode(require_safe_wrapper=True) == "always"
    assert resolve_safe_wrapper_mode(require_safe_wrapper=False) == "never"


def test_resolve_safe_wrapper_mode_validates_explicit_mode() -> None:
    for mode in SUPPORTED_SAFE_WRAPPER_MODES:
        assert resolve_safe_wrapper_mode(safe_wrapper_mode=mode) == mode


def test_apply_safe_wrapper_normalization_auto_wraps_only_when_needed() -> None:
    wrapped_text, wrapped_changed = apply_safe_wrapper_normalization(
        "& {\n    Write-Host 'hi'\n}\n",
        safe_wrapper_mode="auto",
    )
    unwrapped_text, unwrapped_changed = apply_safe_wrapper_normalization(
        "Write-Host 'hi'\n",
        safe_wrapper_mode="auto",
    )

    assert wrapped_text.startswith("& {")
    assert wrapped_changed is False
    assert unwrapped_text.startswith("& {")
    assert unwrapped_changed is True


def test_apply_safe_wrapper_normalization_never_keeps_manual_shape() -> None:
    text, changed = apply_safe_wrapper_normalization(
        "Write-Host 'hi'\n",
        safe_wrapper_mode="never",
    )

    assert text == "Write-Host 'hi'\n"
    assert changed is False


def test_format_bundle_launcher_reports_wrapper_normalized_for_unwrapped_input() -> None:
    result = format_bundle_launcher(
        "Write-Host 'hi'\n",
        safe_wrapper_mode="auto",
    )

    assert result.script_text.startswith("& {")
    assert result.wrapper_normalized is True
