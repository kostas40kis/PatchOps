from __future__ import annotations

import json
from pathlib import Path

from patchops.bundles.bundle_apply_coordinator import build_bundle_apply_plan


def _write_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _desktop_dir(path: Path | None) -> Path:
    assert path is not None
    path.mkdir(parents=True, exist_ok=True)
    return path


def _discover_launcher(bundle_root: Path, *, mode: str, bundle_meta: dict, launcher_relative_path: str | None) -> Path:
    if launcher_relative_path:
        return (bundle_root / launcher_relative_path).resolve()
    launchers = bundle_meta.get("launchers") if isinstance(bundle_meta, dict) else None
    if isinstance(launchers, dict) and isinstance(launchers.get(mode), str):
        return (bundle_root / launchers[mode]).resolve()
    return (bundle_root / "launchers" / "apply_with_patchops.ps1").resolve()


def _build_launcher_command(**kwargs) -> list[str]:
    return [
        "powershell",
        "-File",
        str(kwargs["launcher_path"]),
        "-WrapperRepoRoot",
        str(kwargs["wrapper_root"]),
        "-Mode",
        kwargs["mode"],
        "-Profile",
        kwargs["profile"] or "(none)",
    ]


def test_build_bundle_apply_plan_for_folder_uses_bundle_meta_and_manifest_preview(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()
    desktop = tmp_path / "desktop"
    bundle_root = tmp_path / "delivery_bundle"
    launcher = _write_file(bundle_root / "launchers" / "apply_with_patchops.ps1", "Write-Output 'placeholder'\n")
    manifest = {
        "manifest_version": "1",
        "patch_name": "zp13_probe",
        "active_profile": "generic_python",
        "target_project_root": "C:/dev/patchops",
    }
    _write_file(bundle_root / "manifest.json", json.dumps(manifest, indent=2))
    bundle_meta = {
        "launchers": {"apply": "launchers/apply_with_patchops.ps1"},
        "manifest_path": "manifest.json",
        "recommended_profile": "generic_python",
    }
    _write_file(bundle_root / "bundle_meta.json", json.dumps(bundle_meta, indent=2))

    plan = build_bundle_apply_plan(
        bundle_root,
        wrapper_root=wrapper_root,
        mode="apply",
        profile=None,
        launcher_relative_path=None,
        report_path=None,
        powershell_exe=None,
        desktop_dir=desktop,
        resolve_desktop_dir=_desktop_dir,
        extract_zip_source=lambda source, wrapper: (_ for _ in ()).throw(AssertionError("zip extractor should not run for folder source")),
        load_bundle_meta=lambda root: bundle_meta,
        discover_launcher=_discover_launcher,
        build_launcher_command=_build_launcher_command,
        stamp_fn=lambda: "20260407_160000",
    )

    assert plan.source_kind == "folder"
    assert plan.extracted_path is None
    assert plan.bundle_root == bundle_root.resolve()
    assert plan.manifest_path == (bundle_root / "manifest.json").resolve()
    assert plan.launcher_path == launcher.resolve()
    assert plan.launcher_working_directory == bundle_root.resolve()
    assert plan.active_profile == "generic_python"
    assert plan.target_project_root.as_posix() == "C:/dev/patchops"
    assert plan.report_path.name == "patchops_run_package_20260407_160000.txt"
    assert any("Folder source used directly without extraction." == note for note in plan.notes)
    assert any("bundle_meta.json detected and consulted during launcher discovery." == note for note in plan.notes)
    assert "-WrapperRepoRoot" in plan.command
    assert plan.as_dict()["launcher_path"] == str(launcher.resolve())


def test_build_bundle_apply_plan_for_zip_tracks_extraction_root_and_requested_profile(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()
    desktop = tmp_path / "desktop"
    source_zip = _write_file(tmp_path / "delivery_bundle.zip", "zip placeholder")
    extraction_root = wrapper_root / "data" / "runtime" / "package_runs" / "probe" / "extracted"
    bundle_root = extraction_root / "delivery_bundle"
    launcher = _write_file(bundle_root / "launchers" / "apply_with_patchops.ps1", "Write-Output 'placeholder'\n")
    manifest = {
        "manifest_version": "1",
        "patch_name": "zp13_probe",
        "active_profile": "generic_python",
        "target_project_root": "C:/dev/patchops",
    }
    _write_file(bundle_root / "manifest.json", json.dumps(manifest, indent=2))

    plan = build_bundle_apply_plan(
        source_zip,
        wrapper_root=wrapper_root,
        mode="apply",
        profile="generic_python",
        launcher_relative_path=None,
        report_path=None,
        powershell_exe=None,
        desktop_dir=desktop,
        resolve_desktop_dir=_desktop_dir,
        extract_zip_source=lambda source, wrapper: (extraction_root, bundle_root),
        load_bundle_meta=lambda root: {},
        discover_launcher=_discover_launcher,
        build_launcher_command=_build_launcher_command,
        stamp_fn=lambda: "20260407_160500",
    )

    assert plan.source_kind == "zip"
    assert plan.extracted_path == extraction_root
    assert plan.bundle_root == bundle_root.resolve()
    assert plan.launcher_path == launcher.resolve()
    assert plan.active_profile == "generic_python"
    assert plan.report_path.name == "patchops_run_package_20260407_160500.txt"
    assert any("Zip source extracted by PatchOps." == note for note in plan.notes)
    assert plan.command[0] == "powershell"


def test_build_bundle_apply_plan_supports_explicit_report_path_and_launcher_override(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()
    desktop = tmp_path / "desktop"
    bundle_root = tmp_path / "delivery_bundle"
    launcher = _write_file(bundle_root / "tools" / "custom_apply.ps1", "Write-Output 'placeholder'\n")
    _write_file(bundle_root / "manifest.json", json.dumps({"active_profile": "generic_python"}, indent=2))
    report_path = tmp_path / "reports" / "custom_outer.txt"

    plan = build_bundle_apply_plan(
        bundle_root,
        wrapper_root=wrapper_root,
        mode="apply",
        profile="explicit_profile",
        launcher_relative_path="tools/custom_apply.ps1",
        report_path=report_path,
        powershell_exe=None,
        desktop_dir=desktop,
        resolve_desktop_dir=_desktop_dir,
        extract_zip_source=lambda source, wrapper: (_ for _ in ()).throw(AssertionError("zip extractor should not run for folder source")),
        load_bundle_meta=lambda root: {},
        discover_launcher=_discover_launcher,
        build_launcher_command=_build_launcher_command,
        stamp_fn=lambda: "20260407_161000",
    )

    assert plan.launcher_path == launcher.resolve()
    assert plan.report_path == report_path.resolve()
    assert plan.requested_profile == "explicit_profile"
    assert plan.active_profile == "explicit_profile"
    assert plan.as_dict()["report_path"] == str(report_path.resolve())
