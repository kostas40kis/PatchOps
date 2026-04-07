from __future__ import annotations

from pathlib import Path

import pytest

from patchops import package_runner
from patchops.package_runner import ProcessCapture, run_delivery_package


def _write_bundle(root: Path) -> Path:
    bundle_root = root / "demo_bundle"
    (bundle_root / "launchers").mkdir(parents=True)
    (bundle_root / "content").mkdir(parents=True)
    (bundle_root / "manifest.json").write_text("{}\n", encoding="utf-8")
    (bundle_root / "bundle_meta.json").write_text("{}\n", encoding="utf-8")
    (bundle_root / "README.txt").write_text("demo\n", encoding="utf-8")
    (bundle_root / "launchers" / "apply_with_patchops.ps1").write_text(
        "& {\nparam([string]$WrapperRepoRoot)\nWrite-Host 'demo launcher'\n}\n",
        encoding="utf-8",
    )
    return bundle_root


def test_live_proof_surface_uses_inner_report_as_single_canonical_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle_root = _write_bundle(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    outer_report = desktop_dir / "outer_requested.txt"
    inner_report = desktop_dir / "inner_existing.txt"
    desktop_dir.mkdir()

    inner_report.write_text(
        "PATCHOPS APPLY\n"
        "SUMMARY\n"
        "-------\n"
        "ExitCode : 0\n"
        "Result   : PASS\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(package_runner, "_detect_inner_report_path", lambda **_: inner_report)

    def fake_runner(command: list[str], cwd: Path) -> ProcessCapture:
        return ProcessCapture(
            command=command,
            working_directory=str(cwd),
            exit_code=0,
            stdout="launcher ok\n",
            stderr="",
        )

    result = run_delivery_package(
        bundle_root,
        wrapper_root=tmp_path,
        report_path=outer_report,
        desktop_dir=desktop_dir,
        runner=fake_runner,
    )

    assert result.ok is True
    assert result.exit_code == 0
    assert result.inner_report_path == str(inner_report.resolve())
    assert result.outer_report_path == str(inner_report.resolve())
    assert not outer_report.exists()

    merged_text = inner_report.read_text(encoding="utf-8")
    assert "PATCHOPS RUN-PACKAGE CANONICAL REPORT" in merged_text
    assert f"Canonical Report Path: {inner_report.resolve()}" in merged_text
    assert f"Requested Outer Path : {outer_report.resolve()}" in merged_text
    assert "PATCHOPS APPLY" in merged_text
    assert "Result   : PASS" in merged_text


def test_live_proof_surface_keeps_one_outer_fallback_when_no_inner_report_exists(tmp_path: Path) -> None:
    missing_source = tmp_path / "missing_bundle.zip"
    desktop_dir = tmp_path / "Desktop"
    outer_report = desktop_dir / "outer_only.txt"
    desktop_dir.mkdir()

    result = run_delivery_package(
        missing_source,
        wrapper_root=tmp_path,
        report_path=outer_report,
        desktop_dir=desktop_dir,
    )

    assert result.ok is False
    assert result.inner_report_path is None
    assert result.outer_report_path == str(outer_report.resolve())
    assert outer_report.exists()

    outer_text = outer_report.read_text(encoding="utf-8")
    assert "PATCHOPS RUN-PACKAGE OUTER REPORT" in outer_text
    assert "Inner Report Path   : (not detected)" in outer_text
