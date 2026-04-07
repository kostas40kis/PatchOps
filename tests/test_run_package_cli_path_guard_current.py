from __future__ import annotations

from pathlib import Path

import pytest

from patchops import package_runner


def test_cli_main_rejects_missing_drive_letter_in_source_path(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        package_runner.cli_main([r":\Users\kostas\Desktop\bundle.zip", "--wrapper-root", r"C:\dev\patchops"])

    assert excinfo.value.code == 2
    captured = capsys.readouterr()
    assert "source_path looks like a Windows path but is missing its drive letter" in captured.err
    assert "C:\\dev\\patchops" in captured.err


def test_cli_main_rejects_missing_drive_letter_in_wrapper_root(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        package_runner.cli_main([r"C:\Users\kostas\Desktop\bundle.zip", "--wrapper-root", r":\dev\patchops"])

    assert excinfo.value.code == 2
    captured = capsys.readouterr()
    assert "wrapper_root looks like a Windows path but is missing its drive letter" in captured.err
    assert "C:\\dev\\patchops" in captured.err


def test_cli_main_passes_valid_paths_through_to_runner(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    captured_call: dict[str, object] = {}

    def fake_run_delivery_package(
        source_path: Path,
        *,
        wrapper_root: Path,
        mode: str = "apply",
        profile: str | None = None,
        launcher_relative_path: str | None = None,
        report_path: Path | None = None,
        powershell_exe: str | None = None,
        desktop_dir: Path | None = None,
        runner=None,
    ) -> package_runner.PackageRunResult:
        captured_call["source_path"] = source_path
        captured_call["wrapper_root"] = wrapper_root
        captured_call["mode"] = mode
        captured_call["report_path"] = report_path
        captured_call["desktop_dir"] = desktop_dir
        return package_runner.PackageRunResult(
            ok=True,
            source_path=str(source_path),
            source_kind="zip",
            extracted_path=None,
            bundle_root=str(source_path.parent),
            launcher_path="launcher.ps1",
            launcher_command=["powershell.exe"],
            launcher_working_directory=str(source_path.parent),
            exit_code=0,
            stdout="",
            stderr="",
            inner_report_path=None,
            inner_result=None,
            inner_exit_code=None,
            inner_failure_category=None,
            outer_report_path="report.txt",
            failure_category="",
            notes=[],
        )

    monkeypatch.setattr(package_runner, "run_delivery_package", fake_run_delivery_package)

    exit_code = package_runner.cli_main(
        [
            r"C:\Users\kostas\Desktop\bundle.zip",
            "--wrapper-root",
            r"C:\dev\patchops",
            "--report-path",
            r"C:\Users\kostas\Desktop\report.txt",
            "--desktop-dir",
            r"C:\Users\kostas\Desktop",
        ]
    )

    assert exit_code == 0
    assert captured_call["source_path"] == Path(r"C:\Users\kostas\Desktop\bundle.zip")
    assert captured_call["wrapper_root"] == Path(r"C:\dev\patchops")
    assert captured_call["report_path"] == Path(r"C:\Users\kostas\Desktop\report.txt")
    assert captured_call["desktop_dir"] == Path(r"C:\Users\kostas\Desktop")
    out = capsys.readouterr().out
    assert '"ok": true' in out.lower()
