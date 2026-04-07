from __future__ import annotations

from pathlib import Path

from patchops.package_runner import ProcessCapture, run_delivery_package


def _write_launcher(root: Path, name: str = "apply_with_patchops.ps1") -> Path:
    launcher = root / "launchers" / name
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text(
        "param([string]$WrapperRepoRoot)\n"
        "Write-Output 'launcher placeholder'\n",
        encoding="utf-8",
    )
    return launcher


def _write_inner_report(path: Path, *, exit_code: int, result_label: str, failure_category: str | None = None) -> None:
    lines: list[str] = [
        "PATCHOPS APPLY",
        "Patch Name           : bundle_report_renderer_bridge_probe",
        "",
    ]
    if failure_category:
        lines.extend(
            [
                "FAILURE DETAILS",
                "---------------",
                f"Failure Class : {failure_category}",
                f"Category : {failure_category}",
                "",
            ]
        )
    lines.extend(
        [
            "SUMMARY",
            "-------",
            f"ExitCode : {exit_code}",
            f"Result   : {result_label}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _fake_runner_factory(
    inner_report: Path | None,
    *,
    stdout_text: str = "stdout text",
    stderr_text: str = "stderr text",
    exit_code: int = 0,
    inner_exit_code: int = 0,
    inner_result_label: str = "PASS",
    inner_failure_category: str | None = None,
):
    def _runner(command: list[str], cwd: Path) -> ProcessCapture:
        stdout = stdout_text
        if inner_report is not None:
            _write_inner_report(
                inner_report,
                exit_code=inner_exit_code,
                result_label=inner_result_label,
                failure_category=inner_failure_category,
            )
            stdout = f"{stdout_text}\n{inner_report}"
        return ProcessCapture(
            command=command,
            working_directory=str(cwd),
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr_text,
        )

    return _runner


def test_run_delivery_package_outer_report_keeps_current_sections_and_detected_inner_report(tmp_path: Path) -> None:
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
        runner=_fake_runner_factory(inner_report),
    )

    outer_text = Path(result.outer_report_path).read_text(encoding="utf-8")

    assert result.ok is True
    assert result.inner_report_path == str(inner_report.resolve())
    assert "PATCHOPS RUN-PACKAGE OUTER REPORT" in outer_text
    assert f"Source Path         : {package_root.resolve()}" in outer_text
    assert "Source Kind         : folder" in outer_text
    assert f"Bundle Root         : {package_root.resolve()}" in outer_text
    assert f"Launcher Path       : {launcher.resolve()}" in outer_text
    assert f"Inner Report Path   : {inner_report.resolve()}" in outer_text
    assert "COMMAND" in outer_text
    assert "STDOUT" in outer_text
    assert "STDERR" in outer_text
    assert "NOTES" in outer_text
    assert "SUMMARY" in outer_text
    assert "stdout text" in outer_text
    assert "stderr text" in outer_text
    assert "InnerReportFound   : True" in outer_text


def test_run_delivery_package_outer_report_marks_missing_inner_report_when_not_detected(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()
    desktop_dir = tmp_path / "desktop"
    desktop_dir.mkdir()
    package_root = tmp_path / "delivery_folder"
    _write_launcher(package_root)

    result = run_delivery_package(
        package_root,
        wrapper_root=wrapper_root,
        desktop_dir=desktop_dir,
        runner=_fake_runner_factory(None, stdout_text="no inner report here", stderr_text="", exit_code=0),
    )

    outer_text = Path(result.outer_report_path).read_text(encoding="utf-8")

    assert result.inner_report_path is None
    assert "Inner Report Path   : (not detected)" in outer_text
    assert "InnerReportFound   : False" in outer_text
    assert "Result              : PASS" in outer_text


def test_run_delivery_package_outer_report_preserves_current_failure_note_when_inner_report_disagrees(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()
    desktop_dir = tmp_path / "desktop"
    desktop_dir.mkdir()
    package_root = tmp_path / "delivery_folder"
    _write_launcher(package_root)
    inner_report = desktop_dir / "inner_fail_report.txt"

    result = run_delivery_package(
        package_root,
        wrapper_root=wrapper_root,
        desktop_dir=desktop_dir,
        runner=_fake_runner_factory(
            inner_report,
            stdout_text="launcher says ok",
            stderr_text="",
            exit_code=0,
            inner_exit_code=1,
            inner_result_label="FAIL",
            inner_failure_category="target_content_failure",
        ),
    )

    outer_text = Path(result.outer_report_path).read_text(encoding="utf-8")

    assert result.ok is False
    assert "Result              : FAIL" in outer_text
    assert "Inner Report Path   : " in outer_text
    assert "InnerReportFound   : True" in outer_text
    assert "Inner report summary reported FAIL even though launcher exit code was 0." in outer_text
