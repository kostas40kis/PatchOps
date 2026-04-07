from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(slots=True)
class BundleApplyCoordinatorPlan:
    source_path: Path
    source_kind: str
    extracted_path: Path | None
    bundle_root: Path
    manifest_path: Path
    launcher_path: Path
    launcher_working_directory: Path
    report_path: Path
    desktop_dir: Path
    run_root: Path
    command: list[str]
    mode: str
    requested_profile: str | None
    active_profile: str | None
    target_project_root: Path | None
    notes: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "source_path": str(self.source_path),
            "source_kind": self.source_kind,
            "extracted_path": None if self.extracted_path is None else str(self.extracted_path),
            "bundle_root": str(self.bundle_root),
            "manifest_path": str(self.manifest_path),
            "launcher_path": str(self.launcher_path),
            "launcher_working_directory": str(self.launcher_working_directory),
            "report_path": str(self.report_path),
            "desktop_dir": str(self.desktop_dir),
            "run_root": str(self.run_root),
            "command": list(self.command),
            "mode": self.mode,
            "requested_profile": self.requested_profile,
            "active_profile": self.active_profile,
            "target_project_root": None if self.target_project_root is None else str(self.target_project_root),
            "notes": list(self.notes),
        }


def _first_non_empty(*values: object) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _manifest_path(bundle_root: Path, bundle_meta: dict[str, Any]) -> Path:
    rel = _first_non_empty(
        bundle_meta.get("manifest_path"),
        bundle_meta.get("manifest"),
        bundle_meta.get("manifest_relative_path"),
    )
    if rel is not None:
        return (bundle_root / rel).resolve()
    return (bundle_root / "manifest.json").resolve()


def build_bundle_apply_plan(
    source_path: Path,
    *,
    wrapper_root: Path,
    mode: str = "apply",
    profile: str | None = None,
    launcher_relative_path: str | None = None,
    report_path: Path | None = None,
    powershell_exe: str | None = None,
    desktop_dir: Path | None = None,
    resolve_desktop_dir: Callable[[Path | None], Path],
    extract_zip_source: Callable[[Path, Path], tuple[Path, Path]],
    load_bundle_meta: Callable[[Path], dict[str, Any]],
    discover_launcher: Callable[..., Path],
    build_launcher_command: Callable[..., list[str]],
    stamp_fn: Callable[[], str],
) -> BundleApplyCoordinatorPlan:
    source_path = source_path.resolve()
    wrapper_root = wrapper_root.resolve()
    desktop = resolve_desktop_dir(desktop_dir).resolve()
    report = (report_path or (desktop / f"patchops_run_package_{stamp_fn()}.txt")).resolve()
    report.parent.mkdir(parents=True, exist_ok=True)

    notes: list[str] = []
    if not source_path.exists():
        raise FileNotFoundError(f"Package source does not exist: {source_path}")

    extracted_path: Path | None = None
    if source_path.is_file():
        if source_path.suffix.lower() != ".zip":
            raise ValueError(f"Unsupported package file type: {source_path.suffix}")
        source_kind = "zip"
        extracted_path, bundle_root = extract_zip_source(source_path, wrapper_root)
        notes.append("Zip source extracted by PatchOps.")
    elif source_path.is_dir():
        source_kind = "folder"
        bundle_root = source_path
        notes.append("Folder source used directly without extraction.")
    else:
        raise ValueError(f"Unsupported package source: {source_path}")

    bundle_meta = load_bundle_meta(bundle_root)
    if bundle_meta:
        notes.append("bundle_meta.json detected and consulted during launcher discovery.")

    manifest_path = _manifest_path(bundle_root, bundle_meta)
    manifest_preview = _load_json(manifest_path)
    active_profile = _first_non_empty(
        profile,
        bundle_meta.get("recommended_profile"),
        bundle_meta.get("profile"),
        manifest_preview.get("active_profile"),
    )

    target_root_text = _first_non_empty(manifest_preview.get("target_project_root"))
    target_project_root = None if target_root_text is None else Path(target_root_text)

    launcher_path = discover_launcher(
        bundle_root,
        mode=mode,
        bundle_meta=bundle_meta,
        launcher_relative_path=launcher_relative_path,
    )
    command = build_launcher_command(
        launcher_path=launcher_path,
        wrapper_root=wrapper_root,
        bundle_root=bundle_root,
        source_path=source_path,
        mode=mode,
        profile=active_profile,
        powershell_exe=powershell_exe,
    )

    run_root = wrapper_root / "data" / "runtime" / "package_runs" / f"run_package_{stamp_fn()}"
    run_root.mkdir(parents=True, exist_ok=True)

    return BundleApplyCoordinatorPlan(
        source_path=source_path,
        source_kind=source_kind,
        extracted_path=extracted_path,
        bundle_root=bundle_root.resolve(),
        manifest_path=manifest_path,
        launcher_path=launcher_path.resolve(),
        launcher_working_directory=bundle_root.resolve(),
        report_path=report,
        desktop_dir=desktop,
        run_root=run_root,
        command=command,
        mode=mode,
        requested_profile=profile,
        active_profile=active_profile,
        target_project_root=None if target_project_root is None else target_project_root,
        notes=notes,
    )
