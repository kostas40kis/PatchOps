from __future__ import annotations

import json
from pathlib import Path

import patchops.package_runner as package_runner


def test_exception_helper_returns_fail_closed_package_result(tmp_path: Path) -> None:
    report_path = tmp_path / "outer_exception_report.txt"

    result = package_runner._package_run_exception_result(
        RuntimeError("synthetic wrapper exception"),
        source_path=tmp_path / "bundle.zip",
        wrapper_root=tmp_path,
        report_path=report_path,
        desktop_dir=tmp_path,
    )

    assert isinstance(result, package_runner.PackageRunResult)
    assert result.ok is False
    assert result.exit_code == 1
    assert result.failure_category == "wrapper_failure"
    assert "RuntimeError" in result.stderr
    assert "synthetic wrapper exception" in result.stderr
    assert result.outer_report_path == str(report_path.resolve())
    assert report_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert "Result              : FAIL" in report_text
    assert "Failure Category    : wrapper_failure" in report_text


def test_cli_main_converts_unexpected_run_delivery_exception_to_json_and_report(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source = tmp_path / "bundle.zip"
    source.write_bytes(b"not a real zip; run_delivery_package is monkeypatched")
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()
    report_path = tmp_path / "outer_cli_report.txt"

    def boom(*args, **kwargs):
        raise ValueError("synthetic run_delivery_package explosion")

    monkeypatch.setattr(package_runner, "run_delivery_package", boom)

    exit_code = package_runner.cli_main(
        [
            str(source),
            "--wrapper-root",
            str(wrapper_root),
            "--report-path",
            str(report_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.err == ""

    payload = json.loads(captured.out)
    assert payload["ok"] is False
    assert payload["exit_code"] == 1
    assert payload["failure_category"] == "wrapper_failure"
    assert "ValueError" in payload["stderr"]
    assert "synthetic run_delivery_package explosion" in payload["stderr"]
    assert payload["outer_report_path"] == str(report_path.resolve())
    assert report_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert "PATCHOPS RUN-PACKAGE OUTER REPORT" in report_text
    assert "Failure Category    : wrapper_failure" in report_text
