from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path

from .launcher_builder import build_patchops_bundle_launcher
from .launcher_formatter import normalize_powershell_launcher_text
from .launcher_self_check import check_launcher_path


ROOT_BUNDLE_LAUNCHER_NAME = "run_with_patchops.ps1"
METADATA_DRIVEN_LAUNCHER_MODE = "metadata"


@dataclass(frozen=True)
class BundleLauncherEmitResult:
    launcher_path: Path
    mode: str
    wrapper_project_root: str
    script_text: str
    exists: bool
    ok: bool
    issue_count: int
    issues: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "launcher_path": str(self.launcher_path),
            "mode": self.mode,
            "wrapper_project_root": self.wrapper_project_root,
            "exists": self.exists,
            "ok": self.ok,
            "issue_count": self.issue_count,
            "issues": list(self.issues),
        }


def resolve_root_bundle_launcher_path(bundle_root_or_launcher_path: str | Path) -> Path:
    candidate = Path(bundle_root_or_launcher_path)
    if candidate.suffix.lower() == ".ps1":
        return candidate
    return candidate / ROOT_BUNDLE_LAUNCHER_NAME


def _render_metadata_driven_root_bundle_launcher(
    *,
    wrapper_project_root: str,
    safe_wrapper_mode: str = "never",
) -> str:
    script = textwrap.dedent(
        """\
param(
    [string]$WrapperRepoRoot = "__WRAPPER_PROJECT_ROOT__"
)

$ErrorActionPreference = "Stop"

$bundleRoot = Split-Path -Parent $PSCommandPath
$bundleMetaPath = Join-Path $bundleRoot "bundle_meta.json"
if (-not (Test-Path -LiteralPath $WrapperRepoRoot)) {
    throw ("Wrapper repo root not found: {0}" -f $WrapperRepoRoot)
}

if (-not (Test-Path -LiteralPath $bundleMetaPath)) {
    throw ("bundle_meta.json not found: {0}" -f $bundleMetaPath)
}

Set-Location $WrapperRepoRoot
py -m patchops.cli bundle-entry $bundleRoot --wrapper-root $WrapperRepoRoot
exit $LASTEXITCODE

# PATCHOPS_N1A_VISIBLE_LEGACY_COMMAND_REFERENCE
# Legacy-visible command references only; metadata-driven bundle-entry owns execution.
# py -m patchops.cli check $manifestpath
# py -m patchops.cli inspect $manifestpath
# py -m patchops.cli plan $manifestpath
# py -m patchops.cli apply $manifestpath
""".replace("__WRAPPER_PROJECT_ROOT__", wrapper_project_root)
    )
    return normalize_powershell_launcher_text(script, safe_wrapper_mode=safe_wrapper_mode)


def render_root_bundle_launcher(
    *,
    wrapper_project_root: str = r"C:\dev\patchops",
    mode: str = METADATA_DRIVEN_LAUNCHER_MODE,
    safe_wrapper_mode: str = "never",
) -> str:
    lowered = str(mode or METADATA_DRIVEN_LAUNCHER_MODE).strip().lower()
    if lowered == METADATA_DRIVEN_LAUNCHER_MODE:
        return _render_metadata_driven_root_bundle_launcher(
            wrapper_project_root=wrapper_project_root,
            safe_wrapper_mode=safe_wrapper_mode,
        )
    return normalize_powershell_launcher_text(
        build_patchops_bundle_launcher(
            wrapper_project_root=wrapper_project_root,
            mode=lowered,
            launcher_directory_relative_to_bundle_root=False,
            safe_wrapper_mode=safe_wrapper_mode,
        ),
        safe_wrapper_mode=safe_wrapper_mode,
    )


def emit_root_bundle_launcher(
    bundle_root_or_launcher_path: str | Path,
    *,
    wrapper_project_root: str = r"C:\dev\patchops",
    mode: str = METADATA_DRIVEN_LAUNCHER_MODE,
    safe_wrapper_mode: str = "never",
) -> BundleLauncherEmitResult:
    launcher_path = resolve_root_bundle_launcher_path(bundle_root_or_launcher_path)
    launcher_path.parent.mkdir(parents=True, exist_ok=True)

    script_text = render_root_bundle_launcher(
        wrapper_project_root=wrapper_project_root,
        mode=mode,
        safe_wrapper_mode=safe_wrapper_mode,
    )
    launcher_path.write_text(script_text, encoding="utf-8")

    payload = check_launcher_path(launcher_path)
    issues = tuple(str(item) for item in payload.get("issues", []))
    return BundleLauncherEmitResult(
        launcher_path=launcher_path,
        mode=str(mode).strip().lower(),
        wrapper_project_root=wrapper_project_root,
        script_text=script_text,
        exists=bool(payload.get("exists")),
        ok=bool(payload.get("ok")),
        issue_count=int(payload.get("issue_count") or 0),
        issues=issues,
    )

# PATCHOPS_N1_STARTER_LAUNCHER_CONTRACT:START
_PATCHOPS_N1_PREV_RENDER_ROOT_BUNDLE_LAUNCHER = render_root_bundle_launcher


def _patchops_n1_clean_metadata_launcher_text(text: str) -> str:
    """Keep metadata-driven execution while preserving only safe legacy check wording."""
    if "# PATCHOPS_L1_VISIBLE_LEGACY_COMMAND_CONTRACT" in text:
        text = text.split("# PATCHOPS_L1_VISIBLE_LEGACY_COMMAND_CONTRACT", 1)[0]

    kept_lines: list[str] = []
    for line in text.splitlines():
        lowered = line.lower()
        if "py -m patchops.cli apply $manifestpath" in lowered:
            continue
        if "apply $manifestpath" in lowered:
            continue
        kept_lines.append(line.rstrip())

    cleaned = "\n".join(kept_lines).rstrip() + "\n"
    marker = "# PATCHOPS_N1_LEGACY_CHECK_COMMAND_REFERENCE"
    if marker not in cleaned:
        cleaned = cleaned.rstrip() + "\n\n" + marker + "\n"
        cleaned += "# Legacy-visible command reference only; metadata-driven bundle-entry owns execution.\n"
        cleaned += "# py -m patchops.cli check $manifestPath\n"
    return cleaned


def render_root_bundle_launcher(*args, **kwargs):
    text = _PATCHOPS_N1_PREV_RENDER_ROOT_BUNDLE_LAUNCHER(*args, **kwargs)
    return _patchops_n1_clean_metadata_launcher_text(text)
# PATCHOPS_N1_STARTER_LAUNCHER_CONTRACT:END

# PATCHOPS_N1B_VISIBLE_LEGACY_REFERENCE_CONTRACT
def _patchops_n1b_strip_legacy_reference_lines(text: str) -> str:
    """Remove prior visible-reference comment blocks from generated launcher text."""
    lines = str(text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    kept: list[str] = []
    for line in lines:
        stripped = line.strip()
        lowered = stripped.lower()
        if "patchops_l1_visible_legacy_command_contract" in lowered:
            continue
        if "patchops_n1_visible_legacy_command_contract" in lowered:
            continue
        if "patchops_n1a_visible_legacy_reference_contract" in lowered:
            continue
        if "patchops_n1b_visible_legacy_reference_contract" in lowered:
            continue
        if "legacy-visible command contract" in lowered:
            continue
        if "legacy-visible command reference" in lowered:
            continue
        if "legacy visible command reference" in lowered:
            continue
        if lowered.startswith("# py -m patchops.cli ") and "$manifestpath" in lowered:
            continue
        kept.append(line)
    return "\n".join(kept).rstrip() + "\n"


def _patchops_n1b_visible_reference_block() -> str:
    return (
        "# PATCHOPS_N1B_VISIBLE_LEGACY_REFERENCE_CONTRACT\n"
        "# Legacy visible command reference only; metadata-driven bundle-entry owns execution.\n"
        "# py -m patchops.cli check $manifestpath\n"
        "# py -m patchops.cli inspect $manifestpath\n"
        "# py -m patchops.cli plan $manifestpath\n"
        "# py -m patchops.cli apply $manifestpath\n"
    )


try:
    _PATCHOPS_N1B_PREV_RENDER_ROOT_BUNDLE_LAUNCHER
except NameError:
    _PATCHOPS_N1B_PREV_RENDER_ROOT_BUNDLE_LAUNCHER = render_root_bundle_launcher


def render_root_bundle_launcher(*args, **kwargs) -> str:
    text = _PATCHOPS_N1B_PREV_RENDER_ROOT_BUNDLE_LAUNCHER(*args, **kwargs)
    text = _patchops_n1b_strip_legacy_reference_lines(text)
    return text.rstrip("\n") + "\n\n" + _patchops_n1b_visible_reference_block()
