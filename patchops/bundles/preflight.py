from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .checker import check_bundle_zip
from .inspector import inspect_bundle_zip
from .launcher_heuristics import LauncherHeuristicFinding, find_common_launcher_mistakes


@dataclass(frozen=True)
class BundlePreflightLauncherAudit:
    path: Path
    findings: tuple[LauncherHeuristicFinding, ...] = ()

    @property
    def ok(self) -> bool:
        return len(self.findings) == 0

    @property
    def codes(self) -> tuple[str, ...]:
        return tuple(item.code for item in self.findings)


@dataclass(frozen=True)
class BundlePreflightResult:
    check: Any
    inspect: Any
    launcher_audits: tuple[BundlePreflightLauncherAudit, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return bool(getattr(self.check, "is_valid", False))

    @property
    def ok(self) -> bool:
        return self.is_valid and all(item.ok for item in self.launcher_audits)

    @property
    def warning_count(self) -> int:
        return len(self.warnings) + sum(len(item.findings) for item in self.launcher_audits)


def _load_bundle_meta(bundle_root: Path) -> dict[str, Any]:
    bundle_meta_path = bundle_root / "bundle_meta.json"
    if not bundle_meta_path.exists():
        return {}
    return json.loads(bundle_meta_path.read_text(encoding="utf-8"))


def _collect_launcher_paths(bundle_root: Path) -> tuple[Path, ...]:
    metadata = _load_bundle_meta(bundle_root)
    launchers = metadata.get("launchers") or {}
    collected: list[Path] = []

    def _add(path: Path) -> None:
        resolved = path.resolve()
        if any(existing.resolve() == resolved for existing in collected):
            return
        collected.append(resolved)

    for rel_path in launchers.values():
        if not rel_path:
            continue
        launcher_path = (bundle_root / str(rel_path)).resolve()
        if launcher_path.exists():
            _add(launcher_path)

    root_launcher = (bundle_root / "run_with_patchops.ps1").resolve()
    if root_launcher.exists():
        _add(root_launcher)

    return tuple(collected)


def preflight_bundle_zip(
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path,
    *,
    timestamp_token: str | None = None,
) -> BundlePreflightResult:
    check_result = check_bundle_zip(
        bundle_zip_path,
        wrapper_project_root,
        timestamp_token=timestamp_token,
    )
    inspect_result = inspect_bundle_zip(
        bundle_zip_path,
        wrapper_project_root,
        timestamp_token=timestamp_token,
    )

    if not getattr(check_result, "is_valid", False):
        return BundlePreflightResult(
            check=check_result,
            inspect=inspect_result,
            launcher_audits=(),
            warnings=("bundle_validation_failed",),
        )

    extraction = getattr(check_result, "extraction", None)
    bundle_root = getattr(extraction, "bundle_root", None)
    if bundle_root is None:
        return BundlePreflightResult(
            check=check_result,
            inspect=inspect_result,
            launcher_audits=(),
            warnings=("bundle_root_unavailable",),
        )

    audits: list[BundlePreflightLauncherAudit] = []
    for launcher_path in _collect_launcher_paths(Path(bundle_root)):
        findings = find_common_launcher_mistakes(
            launcher_path.read_text(encoding="utf-8")
        )
        audits.append(
            BundlePreflightLauncherAudit(
                path=launcher_path,
                findings=findings,
            )
        )

    warnings: list[str] = []
    if not audits:
        warnings.append("no_launchers_audited")

    return BundlePreflightResult(
        check=check_result,
        inspect=inspect_result,
        launcher_audits=tuple(audits),
        warnings=tuple(warnings),
    )
