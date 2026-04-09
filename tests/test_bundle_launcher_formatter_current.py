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
    is_top_level_param_script,
    needs_safe_launcher_wrapper,
    normalize_bundle_launcher_text,
    normalize_powershell_launcher_text,
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


def test_normalize_powershell_launcher_text_is_backward_compatible_alias() -> None:
    dirty = "/\nparam()\nWrite-Host hi\n"
    normalized = normalize_powershell_launcher_text(dirty, safe_wrapper_mode="never")
    assert normalized == "param()\nWrite-Host hi\n"


def test_ensure_safe_launcher_wrapper_wraps_unwrapped_launcher() -> None:
    wrapped = ensure_safe_launcher_wrapper("param()\nWrite-Host hi\n")
    assert wrapped.startswith("& {\n")
    assert "param()" in wrapped
    assert wrapped.endswith("}\n")


def test_needs_and_is_launcher_safely_wrapped_are_consistent() -> None:
    raw = "Write-Host hi\n"
    wrapped = ensure_safe_launcher_wrapper(raw)
    assert needs_safe_launcher_wrapper(raw) is True
    assert is_launcher_safely_wrapped(wrapped) is True


def test_auto_mode_preserves_top_level_param_script_shape() -> None:
    script = "param()\nWrite-Host hi\n"
    normalized = normalize_bundle_launcher_text(script, safe_wrapper_mode="auto")
    assert normalized == "param()\nWrite-Host hi\n"
    assert is_top_level_param_script(normalized) is True


def test_auto_mode_wraps_non_param_non_wrapped_script() -> None:
    script = "Write-Host hi\n"
    normalized = normalize_bundle_launcher_text(script, safe_wrapper_mode="auto")
    assert normalized.startswith("& {\n")
    assert "Write-Host hi" in normalized


def test_auto_mode_avoids_double_wrapping_existing_safe_block() -> None:
    wrapped = "& {\n    Write-Host hi\n}\n"
    normalized = normalize_bundle_launcher_text(wrapped, safe_wrapper_mode="auto")
    assert normalized == wrapped


def test_preserve_param_script_mode_wraps_non_param_script_but_keeps_param_script() -> None:
    raw = "Write-Host hi\n"
    wrapped = normalize_bundle_launcher_text(raw, safe_wrapper_mode="preserve_param_script")
    assert wrapped.startswith("& {\n")

    param_script = "param()\nWrite-Host hi\n"
    preserved = normalize_bundle_launcher_text(param_script, safe_wrapper_mode="preserve_param_script")
    assert preserved == param_script


def test_resolve_safe_wrapper_mode_supports_expected_values() -> None:
    assert resolve_safe_wrapper_mode(safe_wrapper_mode="auto") == "auto"
    assert resolve_safe_wrapper_mode(require_safe_wrapper=True) == "always"
    assert resolve_safe_wrapper_mode(require_safe_wrapper=False) == "never"
    assert set(SUPPORTED_SAFE_WRAPPER_MODES) == {"auto", "always", "never", "preserve_param_script"}


def test_apply_safe_wrapper_normalization_reports_when_wrapper_was_added() -> None:
    normalized, changed = apply_safe_wrapper_normalization("Write-Host hi\n", safe_wrapper_mode="always")
    assert changed is True
    assert normalized.startswith("& {\n")


def test_format_bundle_launcher_returns_result_model() -> None:
    result = format_bundle_launcher("param()\nWrite-Host hi\n", safe_wrapper_mode="never")
    assert isinstance(result, BundleLauncherFormatResult)
    assert result.encoding == DEFAULT_LAUNCHER_ENCODING
    assert result.newline == DEFAULT_LAUNCHER_NEWLINE
    assert result.script_text.endswith("\n")
    assert result.starts_with_safe_block is False
