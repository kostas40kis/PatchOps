from __future__ import annotations

import zipfile
from pathlib import Path

from patchops.package_runner import ProcessCapture, run_delivery_package


def _write_launcher(root: Path, name: str = "apply_with_patchops.ps1") -> Path:
    launcher = root / "launchers" / name
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text(
        "param([string]$WrapperRoot, [string]$Profile)\n"
        "Write-Output 'launcher placeholder'\n",
        encoding="utf-8",
    )
    return launcher


def _fake_runner_factory(inner_report: Path, *, stdout_text: str = "stdout text", stderr_text: str = "stderr text", exit_code: int = 7):
    def _runner(command: list[str], cwd: Path) -> ProcessCapture:
        inner_report.write_text("inner report\n", encoding="utf-8")
        return ProcessCapture(
            command=command,
            working_directory=str(cwd),
            exit_code=exit_code,
            stdout=f"{stdout_text}\n{inner_report}",
            stderr=stderr_text,
        )
    return _runner


def test_run_delivery_package_consumes_extracted_folder_and_surfaces_inner_report(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()
    desktop_dir = tmp_path / "desktop"
    desktop_dir.mkdir()
    package_root = tmp_path / "delivery_folder"
    launcher = _write_launcher(package_root)
    inner_report = desktop_dir / "inner_folder_report.txt"

    result = run_delivery_package(
        package_root,
        wrapper_root=wrapper_root,
        desktop_dir=desktop_dir,
        runner=_fake_runner_factory(inner_report, exit_code=7),
    )

    assert result.source_kind == "folder"
    assert result.extracted_path is None
    assert Path(result.bundle_root) == package_root.resolve()
    assert Path(result.launcher_path) == launcher.resolve()
    assert result.exit_code == 7
    assert "stdout text" in result.stdout
    assert result.stderr == "stderr text"
    assert result.inner_report_path == str(inner_report.resolve())
    assert result.failure_category in {"target_content_failure", "wrapper_failure", "package_authoring_failure", "ambiguous_evidence"}


def test_run_delivery_package_consumes_zip_and_discovers_packaged_launcher_deterministically(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()
    desktop_dir = tmp_path / "desktop"
    desktop_dir.mkdir()
    source_root = tmp_path / "source_package"
    bundle_root = source_root / "delivery_bundle"
    launcher = _write_launcher(bundle_root)
    inner_report = desktop_dir / "inner_zip_report.txt"

    zip_path = tmp_path / "delivery_bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in bundle_root.rglob("*"):
            archive.write(path, path.relative_to(source_root))

    result = run_delivery_package(
        zip_path,
        wrapper_root=wrapper_root,
        desktop_dir=desktop_dir,
        runner=_fake_runner_factory(inner_report, exit_code=3, stdout_text="zip stdout", stderr_text="zip stderr"),
    )

    assert result.source_kind == "zip"
    assert result.extracted_path is not None
    assert Path(result.launcher_path).name == launcher.name
    assert "zip stdout" in result.stdout
    assert result.stderr == "zip stderr"
    assert result.exit_code == 3
    assert result.inner_report_path == str(inner_report.resolve())
    assert Path(result.bundle_root).name == "delivery_bundle"
