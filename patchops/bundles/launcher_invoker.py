from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Mapping

ROOT_SINGLE_LAUNCHER_NAME = "run_with_patchops.ps1"
LEGACY_LAUNCHER_DIR = "launchers"
_LEGACY_APPLY_LAUNCHER_NAME = "apply_with_patchops.ps1"
_LEGACY_VERIFY_LAUNCHER_NAME = "verify_with_patchops.ps1"
_VALID_MODES = {"apply", "verify"}


@dataclass(frozen=True)
class BundleLauncherResolution:
    bundle_root: Path
    launcher_path: Path
    mode: str
    launcher_kind: str


@dataclass(frozen=True)
class BundleLauncherInvocationResult:
    resolution: BundleLauncherResolution
    command: tuple[str, ...]
    cwd: Path
    exit_code: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


def _normalize_mode(mode: str) -> str:
    normalized = str(mode).strip().lower()
    if normalized not in _VALID_MODES:
        supported = ", ".join(sorted(_VALID_MODES))
        raise ValueError(f"Unsupported bundle launcher mode: {mode!r}. Supported modes: {supported}")
    return normalized


def resolve_bundled_launcher(bundle_root: str | Path, mode: str = "apply") -> BundleLauncherResolution:
    normalized_mode = _normalize_mode(mode)
    resolved_root = Path(bundle_root)

    root_single_launcher = resolved_root / ROOT_SINGLE_LAUNCHER_NAME
    if root_single_launcher.exists():
        return BundleLauncherResolution(
            bundle_root=resolved_root,
            launcher_path=root_single_launcher,
            mode=normalized_mode,
            launcher_kind="root_single",
        )

    legacy_name = _LEGACY_APPLY_LAUNCHER_NAME if normalized_mode == "apply" else _LEGACY_VERIFY_LAUNCHER_NAME
    legacy_launcher = resolved_root / LEGACY_LAUNCHER_DIR / legacy_name
    if legacy_launcher.exists():
        return BundleLauncherResolution(
            bundle_root=resolved_root,
            launcher_path=legacy_launcher,
            mode=normalized_mode,
            launcher_kind="legacy_dual",
        )

    raise FileNotFoundError(
        f"No bundled launcher found for mode {normalized_mode!r} under {resolved_root}. "
        f"Expected {ROOT_SINGLE_LAUNCHER_NAME!r} at bundle root or {legacy_name!r} under {LEGACY_LAUNCHER_DIR!r}."
    )


resolve_bundle_launcher = resolve_bundled_launcher


def build_bundled_launcher_command(
    resolution: BundleLauncherResolution,
    wrapper_project_root: str | Path,
    *,
    powershell_program: str = "powershell",
) -> tuple[str, ...]:
    return (
        str(powershell_program),
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(resolution.launcher_path),
        "-WrapperRepoRoot",
        str(wrapper_project_root),
    )


def invoke_bundled_launcher(
    bundle_root: str | Path,
    wrapper_project_root: str | Path,
    *,
    mode: str = "apply",
    powershell_program: str = "powershell",
    env: Mapping[str, str] | None = None,
) -> BundleLauncherInvocationResult:
    resolution = resolve_bundled_launcher(bundle_root, mode=mode)
    command = build_bundled_launcher_command(
        resolution,
        wrapper_project_root,
        powershell_program=powershell_program,
    )
    completed = subprocess.run(
        command,
        cwd=str(resolution.bundle_root),
        capture_output=True,
        text=True,
        check=False,
        env=dict(env) if env is not None else None,
    )
    return BundleLauncherInvocationResult(
        resolution=resolution,
        command=tuple(str(part) for part in command),
        cwd=resolution.bundle_root,
        exit_code=int(completed.returncode),
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )
