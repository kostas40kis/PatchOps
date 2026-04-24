from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import patchops.package_runner as package_runner


def _run_cli_with_result(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, result: object) -> tuple[int, Path]:
    source = tmp_path / "bundle.zip"
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()
    outer_report = tmp_path / "outer_report.txt"

    def fake_run_delivery_package(*args, **kwargs):
        return result

    monkeypatch.setattr(package_runner, "run_delivery_package", fake_run_delivery_package)

    exit_code = package_runner.cli_main(
        [
            str(source),
            "--wrapper-root",
            str(wrapper_root),
            "--report-path",
            str(outer_report),
        ]
    )
    return exit_code, outer_report


def test_cli_main_accepts_simplenamespace_result_contract(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    inner_report = tmp_path / "inner_report.txt"
    inner_report.write_text("POST-APPLY DOUBLE CHECK\nDoubleCheckResult: PASS\n", encoding="utf-8")

    result = SimpleNamespace(
        ok=True,
        source_path=str(tmp_path / "bundle.zip"),
        source_kind="zip",
        extracted_path=str(tmp_path / "extracted"),
        bundle_root=str(tmp_path / "bundle_root"),
        launcher_path=str(tmp_path / "bundle_root" / "run_with_patchops.ps1"),
        launcher_command=["pwsh", "-File", "run_with_patchops.ps1"],
        launcher_working_directory=str(tmp_path / "bundle_root"),
        exit_code=0,
        stdout="apply ok\nPOST-APPLY DOUBLE CHECK\nDoubleCheckResult: PASS\n",
        stderr="",
        inner_report_path=str(inner_report),
        inner_result="PASS",
        inner_exit_code=0,
        inner_failure_category=None,
        outer_report_path=str(tmp_path / "outer_report.txt"),
        failure_category="none",
        notes=["attribute object result"],
    )

    exit_code, outer_report = _run_cli_with_result(monkeypatch, tmp_path, result)

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["exit_code"] == 0
    assert payload["failure_category"] == "none"
    assert payload["inner_result"] == "PASS"
    assert "DoubleCheckResult: PASS" in payload["stdout"]
    assert "failed closed to preserve the stable result contract" not in json.dumps(payload)
    assert outer_report.exists()


def test_cli_main_still_fails_closed_for_non_contract_attribute_object(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    result = SimpleNamespace(result=0, arbitrary="not a run-package contract")

    exit_code, outer_report = _run_cli_with_result(monkeypatch, tmp_path, result)

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 1
    assert payload["ok"] is False
    assert payload["exit_code"] == 1
    assert payload["failure_category"] == "wrapper_failure"
    assert "failed closed to preserve the stable result contract" in json.dumps(payload)
    assert outer_report.exists()
