from __future__ import annotations

import json
from pathlib import Path

from patchops import package_runner


def test_cli_main_normalizes_dict_result_to_package_run_result(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    report = desktop / "dict_shape_report.txt"

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
    ) -> dict[str, object]:
        return {
            "ok": False,
            "source_path": str(source_path),
            "source_kind": "zip",
            "bundle_root": str(wrapper_root),
            "launcher_path": "(not discovered)",
            "launcher_command": ["fake"],
            "launcher_working_directory": str(wrapper_root),
            "exit_code": 7,
            "stdout": "dict stdout",
            "stderr": "dict stderr",
            "outer_report_path": str(report),
            "failure_category": "wrapper_failure",
            "notes": ["dict shape returned from fake runner"],
        }

    monkeypatch.setattr(package_runner, "run_delivery_package", fake_run_delivery_package)

    exit_code = package_runner.cli_main(
        [
            str(tmp_path / "bundle.zip"),
            "--wrapper-root",
            str(tmp_path),
            "--report-path",
            str(report),
            "--desktop-dir",
            str(desktop),
        ]
    )

    assert exit_code == 7
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["exit_code"] == 7
    assert payload["failure_category"] == "wrapper_failure"
    assert payload["stderr"] == "dict stderr"
    assert "Normalized non-PackageRunResult" in "\n".join(payload["notes"])
    assert report.exists()
    report_text = report.read_text(encoding="utf-8")
    assert "PATCHOPS RUN-PACKAGE OUTER REPORT" in report_text
    assert "Result              : FAIL" in report_text
    assert "dict stderr" in report_text


def test_cli_main_fails_closed_for_scalar_result_shape(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    report = desktop / "scalar_shape_report.txt"

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
    ) -> int:
        return 0

    monkeypatch.setattr(package_runner, "run_delivery_package", fake_run_delivery_package)

    exit_code = package_runner.cli_main(
        [
            str(tmp_path / "bundle.zip"),
            "--wrapper-root",
            str(tmp_path),
            "--report-path",
            str(report),
            "--desktop-dir",
            str(desktop),
        ]
    )

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["exit_code"] == 1
    assert payload["failure_category"] == "wrapper_failure"
    assert "int" in payload["stderr"]
    assert report.exists()
    assert "Non-PackageRunResult returned by run_delivery_package: int" in report.read_text(encoding="utf-8")


def test_run_delivery_package_missing_zip_still_returns_package_run_result(tmp_path: Path) -> None:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    report = desktop / "missing_zip_report.txt"

    result = package_runner.run_delivery_package(
        tmp_path / "missing_bundle.zip",
        wrapper_root=tmp_path,
        report_path=report,
        desktop_dir=desktop,
    )

    assert isinstance(result, package_runner.PackageRunResult)
    assert result.ok is False
    assert result.exit_code != 0
    assert result.failure_category == "package_authoring_failure"
    assert result.outer_report_path == str(report.resolve())
    assert report.exists()
