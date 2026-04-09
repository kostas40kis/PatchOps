from __future__ import annotations

from dataclasses import dataclass

DEFAULT_LAUNCHER_ENCODING = "utf-8"
DEFAULT_LAUNCHER_NEWLINE = "\n"
SUPPORTED_LAUNCHER_MODES = ("apply", "verify")
SUPPORTED_SAFE_WRAPPER_MODES = ("auto", "always", "never", "preserve_param_script")


@dataclass(frozen=True)
class BundleLauncherFormatResult:
    script_text: str
    encoding: str = DEFAULT_LAUNCHER_ENCODING
    newline: str = DEFAULT_LAUNCHER_NEWLINE
    starts_with_safe_block: bool = False
    wrapper_normalized: bool = False


def normalize_launcher_newlines(text: str) -> str:
    return (text or "").replace("\r\n", "\n").replace("\r", "\n")


def _split_lines(text: str) -> list[str]:
    return normalize_launcher_newlines(text).lstrip("\ufeff").split("\n")


def strip_leading_launcher_artifacts(text: str) -> str:
    lines = _split_lines(text)
    while lines and lines[0].strip() in {"/", "\\"}:
        lines = lines[1:]
    return "\n".join(lines).lstrip("\n")


def is_top_level_param_script(text: str) -> bool:
    trimmed = strip_leading_launcher_artifacts(text).lstrip()
    return trimmed.startswith("param(")


def is_launcher_safely_wrapped(text: str) -> bool:
    trimmed = strip_leading_launcher_artifacts(text).strip()
    return trimmed.startswith("& {") and trimmed.endswith("}")


def needs_safe_launcher_wrapper(text: str) -> bool:
    trimmed = strip_leading_launcher_artifacts(text).strip()
    if not trimmed:
        return False
    if is_launcher_safely_wrapped(trimmed):
        return False
    if is_top_level_param_script(trimmed):
        return False
    return True


def _indent_wrapper_body(text: str) -> str:
    lines = normalize_launcher_newlines(text).strip("\n").split("\n")
    return "\n".join(("    " + line.rstrip()) if line else "" for line in lines)


def ensure_safe_launcher_wrapper(text: str) -> str:
    cleaned = strip_leading_launcher_artifacts(text)
    cleaned = normalize_launcher_newlines(cleaned).strip("\n")
    if is_launcher_safely_wrapped(cleaned):
        return cleaned.rstrip() + "\n"

    body = _indent_wrapper_body(cleaned)
    return f"& {{\n{body}\n}}\n"


def resolve_safe_wrapper_mode(
    *,
    require_safe_wrapper: bool | None = None,
    safe_wrapper_mode: str = "auto",
) -> str:
    if require_safe_wrapper is not None:
        return "always" if require_safe_wrapper else "never"

    lowered = (safe_wrapper_mode or "").strip().lower()
    if lowered not in SUPPORTED_SAFE_WRAPPER_MODES:
        supported = ", ".join(SUPPORTED_SAFE_WRAPPER_MODES)
        raise ValueError(
            f"Unsupported safe wrapper mode: {safe_wrapper_mode}. Expected one of: {supported}"
        )
    return lowered


def _normalize_launcher_text_core(text: str) -> str:
    normalized = strip_leading_launcher_artifacts(text)
    normalized = normalize_launcher_newlines(normalized)
    normalized = "\n".join(line.rstrip() for line in normalized.strip("\n").split("\n"))
    return normalized + "\n" if normalized else ""


def apply_safe_wrapper_normalization(
    text: str,
    *,
    require_safe_wrapper: bool | None = None,
    safe_wrapper_mode: str = "auto",
) -> tuple[str, bool]:
    resolved_mode = resolve_safe_wrapper_mode(
        require_safe_wrapper=require_safe_wrapper,
        safe_wrapper_mode=safe_wrapper_mode,
    )
    normalized = _normalize_launcher_text_core(text)

    if resolved_mode == "never":
        return normalized, False

    if resolved_mode == "always":
        wrapped = ensure_safe_launcher_wrapper(normalized)
        return wrapped, wrapped != normalized

    if resolved_mode == "preserve_param_script":
        if not normalized.strip():
            return normalized, False
        if is_top_level_param_script(normalized):
            return normalized, False
        if is_launcher_safely_wrapped(normalized):
            return normalized, False
        wrapped = ensure_safe_launcher_wrapper(normalized)
        return wrapped, True

    # auto
    if not normalized.strip():
        return normalized, False
    if is_top_level_param_script(normalized):
        return normalized, False
    if is_launcher_safely_wrapped(normalized):
        return normalized, False
    wrapped = ensure_safe_launcher_wrapper(normalized)
    return wrapped, True


def normalize_bundle_launcher_text(
    text: str,
    *,
    require_safe_wrapper: bool | None = None,
    safe_wrapper_mode: str = "auto",
) -> str:
    normalized, _ = apply_safe_wrapper_normalization(
        text,
        require_safe_wrapper=require_safe_wrapper,
        safe_wrapper_mode=safe_wrapper_mode,
    )
    return normalized.rstrip("\n") + "\n" if normalized else ""


def normalize_powershell_launcher_text(
    text: str,
    *,
    require_safe_wrapper: bool | None = None,
    safe_wrapper_mode: str = "auto",
) -> str:
    return normalize_bundle_launcher_text(
        text,
        require_safe_wrapper=require_safe_wrapper,
        safe_wrapper_mode=safe_wrapper_mode,
    )


def build_standard_bundle_launcher(
    *,
    wrapper_repo_root: str = r"C:\dev\patchops",
    cli_mode: str = "apply",
    manifest_relative_path: str = "manifest.json",
    bundle_root_expression: str = "$bundleRoot",
    safe_wrapper_mode: str = "always",
) -> str:
    lowered_mode = (cli_mode or "").strip().lower()
    if lowered_mode not in SUPPORTED_LAUNCHER_MODES:
        supported = ", ".join(SUPPORTED_LAUNCHER_MODES)
        raise ValueError(f"Unsupported launcher mode: {cli_mode}. Expected one of: {supported}")

    script = f"""param(
    [string]$WrapperRepoRoot = '{wrapper_repo_root}'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$bundleRoot = {bundle_root_expression}
$manifestPath = Join-Path $bundleRoot '{manifest_relative_path}'

if (-not (Test-Path -LiteralPath $WrapperRepoRoot)) {{
    throw ("Wrapper repo root not found: {{0}}" -f $WrapperRepoRoot)
}}

if (-not (Test-Path -LiteralPath $manifestPath)) {{
    throw ("Manifest not found: {{0}}" -f $manifestPath)
}}

Push-Location -LiteralPath $WrapperRepoRoot
try {{
    & py -m patchops.cli check $manifestPath
    & py -m patchops.cli inspect $manifestPath
    & py -m patchops.cli plan $manifestPath
    & py -m patchops.cli {lowered_mode} $manifestPath
}}
finally {{
    Pop-Location
}}
"""
    return normalize_bundle_launcher_text(script, safe_wrapper_mode=safe_wrapper_mode)


def format_bundle_launcher(
    text: str,
    *,
    encoding: str = DEFAULT_LAUNCHER_ENCODING,
    newline: str = DEFAULT_LAUNCHER_NEWLINE,
    require_safe_wrapper: bool | None = None,
    safe_wrapper_mode: str = "auto",
) -> BundleLauncherFormatResult:
    normalized, wrapper_normalized = apply_safe_wrapper_normalization(
        text,
        require_safe_wrapper=require_safe_wrapper,
        safe_wrapper_mode=safe_wrapper_mode,
    )
    normalized = normalized.replace("\n", newline)
    return BundleLauncherFormatResult(
        script_text=normalized,
        encoding=encoding,
        newline=newline,
        starts_with_safe_block=normalized.lstrip().startswith("& {"),
        wrapper_normalized=wrapper_normalized,
    )
