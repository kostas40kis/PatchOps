from __future__ import annotations

from dataclasses import dataclass

DEFAULT_LAUNCHER_ENCODING = "utf-8"
DEFAULT_LAUNCHER_NEWLINE = "\n"
SUPPORTED_LAUNCHER_MODES = ("apply", "verify")
SUPPORTED_SAFE_WRAPPER_MODES = ("auto", "always", "never")


@dataclass(frozen=True)
class BundleLauncherFormatResult:
    script_text: str
    encoding: str = DEFAULT_LAUNCHER_ENCODING
    newline: str = DEFAULT_LAUNCHER_NEWLINE
    starts_with_safe_block: bool = True
    wrapper_normalized: bool = False


def normalize_launcher_newlines(text: str) -> str:
    return (text or "").replace("\r\n", "\n").replace("\r", "\n")


def strip_leading_launcher_artifacts(text: str) -> str:
    normalized = normalize_launcher_newlines(text).lstrip("\ufeff")
    trimmed = normalized.lstrip("\n").lstrip()

    if trimmed.startswith(("/", "\\")):
        remainder = trimmed[1:].lstrip()
        if remainder.startswith("& {") or remainder.startswith("param("):
            trimmed = remainder

    return trimmed


def is_launcher_safely_wrapped(text: str) -> bool:
    trimmed = strip_leading_launcher_artifacts(text).strip()
    return trimmed.startswith("& {") and trimmed.endswith("}")


def needs_safe_launcher_wrapper(text: str) -> bool:
    trimmed = strip_leading_launcher_artifacts(text).strip()
    return bool(trimmed) and not is_launcher_safely_wrapped(trimmed)


def _indent_wrapper_body(text: str) -> str:
    lines = normalize_launcher_newlines(text).strip("\n").split("\n")
    return "\n".join(("    " + line) if line else "" for line in lines)


def ensure_safe_launcher_wrapper(text: str) -> str:
    cleaned = normalize_launcher_newlines(strip_leading_launcher_artifacts(text)).strip("\n")
    if is_launcher_safely_wrapped(cleaned):
        return cleaned + "\n"

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
            f"Unsupported safe_wrapper_mode: {safe_wrapper_mode!r}. Supported values: {supported}."
        )
    return lowered


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
    cleaned = normalize_launcher_newlines(strip_leading_launcher_artifacts(text)).strip("\n")
    normalized_needed = needs_safe_launcher_wrapper(cleaned)

    if resolved_mode == "never":
        return cleaned + "\n", False
    if resolved_mode == "always":
        return ensure_safe_launcher_wrapper(cleaned), normalized_needed
    if normalized_needed:
        return ensure_safe_launcher_wrapper(cleaned), True
    return cleaned + "\n", False


def normalize_bundle_launcher_text(
    text: str,
    *,
    require_safe_wrapper: bool | None = None,
    safe_wrapper_mode: str = "auto",
) -> str:
    trimmed = strip_leading_launcher_artifacts(text)
    lines = [line.rstrip() for line in trimmed.split("\n")]
    normalized = "\n".join(lines).strip("\n")
    result, _ = apply_safe_wrapper_normalization(
        normalized,
        require_safe_wrapper=require_safe_wrapper,
        safe_wrapper_mode=safe_wrapper_mode,
    )
    return result


def build_standard_bundle_launcher(
    *,
    wrapper_repo_root: str = r"C:\dev\patchops",
    cli_mode: str = "apply",
    manifest_relative_path: str = "manifest.json",
    bundle_root_expression: str = "$PSScriptRoot",
    safe_wrapper_mode: str = "always",
) -> str:
    if cli_mode not in SUPPORTED_LAUNCHER_MODES:
        supported = ", ".join(SUPPORTED_LAUNCHER_MODES)
        raise ValueError(f"Unsupported cli_mode: {cli_mode!r}. Supported values: {supported}.")

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
    & py -m patchops.cli {cli_mode} $manifestPath
}}
finally {{
    Pop-Location
}}
"""
    return normalize_bundle_launcher_text(
        script,
        safe_wrapper_mode=safe_wrapper_mode,
    )


def format_bundle_launcher(
    text: str | None = None,
    *,
    wrapper_repo_root: str = r"C:\dev\patchops",
    cli_mode: str = "apply",
    manifest_relative_path: str = "manifest.json",
    bundle_root_expression: str = "$PSScriptRoot",
    require_safe_wrapper: bool | None = None,
    safe_wrapper_mode: str = "auto",
) -> BundleLauncherFormatResult:
    normalized_applied = False
    if text is None:
        resolved_mode = resolve_safe_wrapper_mode(
            require_safe_wrapper=require_safe_wrapper,
            safe_wrapper_mode=safe_wrapper_mode,
        )
        script_text = build_standard_bundle_launcher(
            wrapper_repo_root=wrapper_repo_root,
            cli_mode=cli_mode,
            manifest_relative_path=manifest_relative_path,
            bundle_root_expression=bundle_root_expression,
            safe_wrapper_mode=resolved_mode,
        )
    else:
        script_text, normalized_applied = apply_safe_wrapper_normalization(
            text,
            require_safe_wrapper=require_safe_wrapper,
            safe_wrapper_mode=safe_wrapper_mode,
        )

    return BundleLauncherFormatResult(
        script_text=script_text,
        starts_with_safe_block=is_launcher_safely_wrapped(script_text),
        wrapper_normalized=normalized_applied,
    )


render_standard_bundle_launcher = build_standard_bundle_launcher
