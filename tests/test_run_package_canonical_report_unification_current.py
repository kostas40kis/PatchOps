from __future__ import annotations

from pathlib import Path

import pytest

from patchops import package_runner
from patchops.package_runner import ProcessCapture, run_delivery_package


def _write_bundle(root: Path) -> Path:
    bundle_root = root / "demo_bundle"
    (bundle_root / "content").mkdir(parents=True)
    (bundle_root / "manifest.json").write_text("{}\n", encoding="utf-8")
    (bundle_root / "bundle_meta.json").write_text(
        '{"launcher_path": "run_with_patchops.ps1"}\n',
        encoding="utf-8",
    )
    (bundle_root / "README.txt").write_text("demo\n", encoding="utf-8")
    (bundle_root / "run_with_patchops.ps1").write_text(
        "param([string]$WrapperRepoRoot)\nWrite-Host 'demo launcher'\n",
        encoding="utf-8",
    )
    return bundle_root


def test_inner_report_is_rewritten_as_the_single_canonical_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle_root = _write_bundle(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    requested_outer = desktop_dir / "requested_outer.txt"
    inner_report = desktop_dir / "inner_report.txt"
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
        report_path=requested_outer,
        desktop_dir=desktop_dir,
        runner=fake_runner,
    )

    assert result.ok is True
    assert result.outer_report_path == str(inner_report.resolve())
    assert not requested_outer.exists()

    report_text = inner_report.read_text(encoding="utf-8")
    assert "PATCHOPS RUN-PACKAGE CANONICAL REPORT" in report_text
    assert f"Canonical Report Path: {inner_report.resolve()}" in report_text
    assert f"Requested Outer Path : {requested_outer.resolve()}" in report_text
    assert f"Outer Report Path    : {inner_report.resolve()}" in report_text
    assert "Inner Result         : PASS" in report_text
    assert "Canonical run-package context merged into inner report; no separate outer report artifact was kept." in report_text
    assert "PATCHOPS APPLY" in report_text



def test_outer_report_remains_the_single_failure_artifact_when_no_inner_report_exists(tmp_path: Path) -> None:
    bundle_root = _write_bundle(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    requested_outer = desktop_dir / "outer_failure.txt"
    desktop_dir.mkdir()

    def fake_runner(command: list[str], cwd: Path) -> ProcessCapture:
        return ProcessCapture(
            command=command,
            working_directory=str(cwd),
            exit_code=1,
            stdout="",
            stderr="ModuleNotFoundError: No module named 'patchops'\n",
        )

    result = run_delivery_package(
        bundle_root,
        wrapper_root=tmp_path,
        report_path=requested_outer,
        desktop_dir=desktop_dir,
        runner=fake_runner,
    )

    assert result.ok is False
    assert result.failure_category == "wrapper_failure"
    assert result.inner_report_path is None
    assert result.outer_report_path == str(requested_outer.resolve())
    assert requested_outer.exists()

    report_text = requested_outer.read_text(encoding="utf-8")
    assert "PATCHOPS RUN-PACKAGE OUTER REPORT" in report_text
    assert "Result              : FAIL" in report_text
    assert "Failure Category    : wrapper_failure" in report_text
    assert "Inner Report Path   : (not detected)" in report_text
    assert "COMMAND" in report_text
    assert "ModuleNotFoundError: No module named 'patchops'" in report_text
