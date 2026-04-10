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


def test_run_package_merges_outer_context_into_inner_fail_report_when_launcher_exit_is_zero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle_root = _write_bundle(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    outer_report = desktop_dir / "outer.txt"
    inner_report = desktop_dir / "inner.txt"
    desktop_dir.mkdir()
    inner_report.write_text(
        "PATCHOPS APPLY\n"
        "SUMMARY\n"
        "-------\n"
        "ExitCode : 3\n"
        "Result   : FAIL\n"
        "\n"
        "FAILURE DETAILS\n"
        "---------------\n"
        "Failure Class : target_project_failure\n"
        "Category : target_project_failure\n",
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

    assert result.ok is False
    assert result.exit_code == 3
    assert result.failure_category == "target_content_failure"
    assert result.inner_result == "FAIL"
    assert result.inner_exit_code == 3
    assert result.inner_failure_category == "target_content_failure"
    assert result.inner_report_path == str(inner_report.resolve())
    assert result.outer_report_path == str(inner_report.resolve())
    assert not outer_report.exists()

    report_text = inner_report.read_text(encoding="utf-8")
    assert "PATCHOPS RUN-PACKAGE CANONICAL REPORT" in report_text
    assert f"Canonical Report Path: {inner_report.resolve()}" in report_text
    assert f"Requested Outer Path : {outer_report.resolve()}" in report_text
    assert "Failure Category     : target_content_failure" in report_text
    assert f"Inner Report Path    : {inner_report.resolve()}" in report_text
    assert "Inner Result         : FAIL" in report_text
    assert "Inner Exit Code      : 3" in report_text
    assert "Inner Failure        : target_content_failure" in report_text
    assert f"Outer Report Path    : {inner_report.resolve()}" in report_text
    assert "Canonical run-package context merged into inner report; no separate outer report artifact was kept." in report_text
    assert "Inner report summary reported FAIL even though launcher exit code was 0." in report_text
    assert "PATCHOPS APPLY" in report_text
    assert "ExitCode : 3" in report_text
    assert "Result   : FAIL" in report_text


def test_run_package_merges_outer_context_into_inner_pass_report_when_inner_report_exists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle_root = _write_bundle(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    outer_report = desktop_dir / "outer_pass.txt"
    inner_report = desktop_dir / "inner_pass.txt"
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
    assert result.failure_category == ""
    assert result.inner_result == "PASS"
    assert result.inner_exit_code == 0
    assert result.outer_report_path == str(inner_report.resolve())
    assert not outer_report.exists()

    report_text = inner_report.read_text(encoding="utf-8")
    assert "PATCHOPS RUN-PACKAGE CANONICAL REPORT" in report_text
    assert "Result               : PASS" in report_text
    assert f"Inner Report Path    : {inner_report.resolve()}" in report_text
    assert "Inner Result         : PASS" in report_text
    assert "Inner Exit Code      : 0" in report_text
    assert "Inner Failure        : (none)" in report_text
    assert f"Outer Report Path    : {inner_report.resolve()}" in report_text
    assert "PATCHOPS APPLY" in report_text
    assert "Result   : PASS" in report_text


def test_run_package_keeps_outer_report_as_single_artifact_when_no_inner_report_exists(tmp_path: Path) -> None:
    missing_source = tmp_path / "missing_bundle.zip"
    desktop_dir = tmp_path / "Desktop"
    desktop_dir.mkdir()
    outer_report = desktop_dir / "outer_only.txt"

    result = run_delivery_package(
        missing_source,
        wrapper_root=tmp_path,
        report_path=outer_report,
        desktop_dir=desktop_dir,
    )

    assert result.ok is False
    assert result.failure_category == "package_authoring_failure"
    assert result.inner_report_path is None
    assert result.outer_report_path == str(outer_report.resolve())
    assert outer_report.exists()

    report_text = outer_report.read_text(encoding="utf-8")
    assert "PATCHOPS RUN-PACKAGE OUTER REPORT" in report_text
    assert "Inner Report Path   : (not detected)" in report_text
    assert f"Outer Report Path   : {outer_report.resolve()}" in report_text



def test_run_package_utc_stamp_uses_timezone_aware_utc() -> None:
    source = Path(package_runner.__file__).read_text(encoding="utf-8")

    assert "datetime.utcnow(" not in source
    assert "datetime.now(UTC)" in source


def test_run_package_fails_when_fatal_syntaxerror_stderr_exists_without_inner_report(tmp_path: Path) -> None:
    bundle_root = _write_bundle(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    outer_report = desktop_dir / "outer_syntaxerror.txt"
    desktop_dir.mkdir()

    def fake_runner(command: list[str], cwd: Path) -> ProcessCapture:
        return ProcessCapture(
            command=command,
            working_directory=str(cwd),
            exit_code=0,
            stdout="launcher looked successful\n",
            stderr="SyntaxError: invalid syntax\n",
        )

    result = run_delivery_package(
        bundle_root,
        wrapper_root=tmp_path,
        report_path=outer_report,
        desktop_dir=desktop_dir,
        runner=fake_runner,
    )

    assert result.ok is False
    assert result.exit_code == 1
    assert result.failure_category == "package_authoring_failure"
    assert result.inner_report_path is None
    assert result.outer_report_path == str(outer_report.resolve())

    report_text = outer_report.read_text(encoding="utf-8")
    assert "Result              : FAIL" in report_text
    assert "Failure Category    : package_authoring_failure" in report_text
    assert "Inner Report Path   : (not detected)" in report_text
    assert "SyntaxError: invalid syntax" in report_text
    assert "Fatal launcher stderr was detected without a real inner report; treating run-package outcome as FAIL." in report_text


def test_run_package_fails_when_modulenotfound_stderr_exists_without_inner_report(tmp_path: Path) -> None:
    bundle_root = _write_bundle(tmp_path)
    desktop_dir = tmp_path / "Desktop"
    outer_report = desktop_dir / "outer_module_not_found.txt"
    desktop_dir.mkdir()

    def fake_runner(command: list[str], cwd: Path) -> ProcessCapture:
        return ProcessCapture(
            command=command,
            working_directory=str(cwd),
            exit_code=0,
            stdout="launcher looked successful\n",
            stderr="ModuleNotFoundError: No module named 'patchops'\n",
        )

    result = run_delivery_package(
        bundle_root,
        wrapper_root=tmp_path,
        report_path=outer_report,
        desktop_dir=desktop_dir,
        runner=fake_runner,
    )

    assert result.ok is False
    assert result.exit_code == 1
    assert result.failure_category == "wrapper_failure"
    assert result.inner_report_path is None
    assert result.outer_report_path == str(outer_report.resolve())

    report_text = outer_report.read_text(encoding="utf-8")
    assert "Result              : FAIL" in report_text
    assert "Failure Category    : wrapper_failure" in report_text
    assert "Inner Report Path   : (not detected)" in report_text
    assert "ModuleNotFoundError: No module named 'patchops'" in report_text
    assert "Fatal launcher stderr was detected without a real inner report; treating run-package outcome as FAIL." in report_text
