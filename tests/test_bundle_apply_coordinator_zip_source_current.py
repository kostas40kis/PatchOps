from __future__ import annotations

import json
from pathlib import Path

from patchops.bundles.bundle_apply_coordinator import build_bundle_apply_plan


def _write_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _desktop_dir(explicit: Path | None = None) -> Path:
    if explicit is None:
        raise AssertionError("desktop dir should be passed explicitly in this test")
    explicit.mkdir(parents=True, exist_ok=True)
    return explicit


def _discover_launcher(bundle_root: Path, *, mode: str, launcher_relative_path: str | None, bundle_meta: dict) -> Path:
    if launcher_relative_path is not None:
        return (bundle_root / launcher_relative_path).resolve()
    rel = bundle_meta["launchers"][mode]
    return (bundle_root / rel).resolve()


def _build_launcher_command(
    launcher_path: Path,
    *,
    wrapper_root: Path,
    bundle_root: Path,
    source_path: Path,
    mode: str,
    profile: str | None,
    powershell_exe: str | None,
) -> list[str]:
    assert bundle_root.name == "delivery_bundle"
    assert source_path.suffix.lower() == ".zip"
    assert mode in {"apply", "verify"}
    assert profile in {"generic_python", "generic_python_powershell", None}
    return [powershell_exe or "powershell.exe", "-File", str(launcher_path), "-WrapperRepoRoot", str(wrapper_root)]


def test_build_bundle_apply_plan_for_zip_uses_extractor_and_profile_override(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()
    desktop = tmp_path / "desktop"
    source_zip = tmp_path / "delivery_bundle.zip"
    source_zip.write_text("placeholder", encoding="utf-8")

    extracted_root = tmp_path / "runtime" / "extracted"
    bundle_root = extracted_root / "delivery_bundle"
    launcher = _write_file(bundle_root / "launchers" / "apply_with_patchops.ps1", "Write-Output 'placeholder'\n")
    manifest = {
        "manifest_version": "1",
        "patch_name": "zp14_probe",
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

    def _extract_zip_source(source: Path, wrapper: Path) -> tuple[Path, Path]:
        assert source == source_zip.resolve()
        assert wrapper == wrapper_root.resolve()
        return extracted_root.resolve(), bundle_root.resolve()

    plan = build_bundle_apply_plan(
        source_zip,
        wrapper_root=wrapper_root,
        mode="apply",
        profile="generic_python_powershell",
        launcher_relative_path=None,
        report_path=None,
        powershell_exe="pwsh.exe",
        desktop_dir=desktop,
        resolve_desktop_dir=_desktop_dir,
        extract_zip_source=_extract_zip_source,
        load_bundle_meta=lambda root: bundle_meta,
        discover_launcher=_discover_launcher,
        build_launcher_command=_build_launcher_command,
        stamp_fn=lambda: "20260407_163000",
    )

    assert plan.source_kind == "zip"
    assert plan.extracted_path == extracted_root.resolve()
    assert plan.bundle_root == bundle_root.resolve()
    assert plan.manifest_path == (bundle_root / "manifest.json").resolve()
    assert plan.launcher_path == launcher.resolve()
    assert plan.launcher_working_directory == bundle_root.resolve()
    assert plan.active_profile == "generic_python_powershell"
    assert str(plan.target_project_root).replace("\\", "/") == "C:/dev/patchops"
    assert str(plan.report_path).endswith("patchops_run_package_20260407_163000.txt")
    assert plan.command == [
        "pwsh.exe",
        "-File",
        str(launcher.resolve()),
        "-WrapperRepoRoot",
        str(wrapper_root.resolve()),
    ]


def test_build_bundle_apply_plan_for_zip_honors_explicit_report_path(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()
    desktop = tmp_path / "desktop"
    source_zip = tmp_path / "delivery_bundle.zip"
    source_zip.write_text("placeholder", encoding="utf-8")

    extracted_root = tmp_path / "runtime" / "extracted"
    bundle_root = extracted_root / "delivery_bundle"
    launcher = _write_file(bundle_root / "launchers" / "verify_with_patchops.ps1", "Write-Output 'placeholder'\n")
    manifest = {
        "manifest_version": "1",
        "patch_name": "zp14_report_override",
        "active_profile": "generic_python",
        "target_project_root": "C:/dev/patchops",
    }
    _write_file(bundle_root / "manifest.json", json.dumps(manifest, indent=2))
    bundle_meta = {
        "launchers": {"verify": "launchers/verify_with_patchops.ps1"},
        "manifest_path": "manifest.json",
        "recommended_profile": "generic_python",
    }
    _write_file(bundle_root / "bundle_meta.json", json.dumps(bundle_meta, indent=2))
    explicit_report = tmp_path / "reports" / "coordinator_probe.txt"

    plan = build_bundle_apply_plan(
        source_zip,
        wrapper_root=wrapper_root,
        mode="verify",
        profile=None,
        launcher_relative_path=None,
        report_path=explicit_report,
        powershell_exe=None,
        desktop_dir=desktop,
        resolve_desktop_dir=_desktop_dir,
        extract_zip_source=lambda source, wrapper: (extracted_root.resolve(), bundle_root.resolve()),
        load_bundle_meta=lambda root: bundle_meta,
        discover_launcher=_discover_launcher,
        build_launcher_command=_build_launcher_command,
        stamp_fn=lambda: "20260407_163500",
    )

    assert plan.source_kind == "zip"
    assert plan.report_path == explicit_report.resolve()
    assert plan.launcher_path == launcher.resolve()
    assert plan.command[0] == "powershell.exe"
    assert plan.launcher_working_directory == bundle_root.resolve()
