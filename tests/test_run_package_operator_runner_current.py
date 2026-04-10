from pathlib import Path


def test_quiet_runner_is_canonical_operator_runner_and_has_parser_safe_shape() -> None:
    runner = Path("powershell/Invoke-QuietRunPackage.ps1").read_text(encoding="utf-8")
    doc = Path("docs/quiet_run_package_helper.md").read_text(encoding="utf-8")

    assert runner.splitlines()[0] == "param("
    assert "[CmdletBinding()]" not in runner
    assert not runner.startswith("\\")

    assert "patchops.cli" in runner
    assert "run-package" in runner
    assert "ReportPath" in runner
    assert "Failure" in runner
    assert "PassThruRawOutput" in runner

    assert "single canonical operator-facing" in doc
    assert "Invoke-QuietRunPackage.ps1" in doc
    assert "compatibility shim" in doc
    assert "Keep PowerShell thin" in doc
    assert "canonical Desktop txt report" in doc


def test_run_runner_is_only_a_compatibility_shim_and_has_parser_safe_shape() -> None:
    shim = Path("powershell/Invoke-RunPackage.ps1").read_text(encoding="utf-8")
    doc = Path("docs/run_package_operator_runner.md").read_text(encoding="utf-8")

    assert shim.splitlines()[0] == "param("
    assert "[CmdletBinding()]" not in shim
    assert not shim.startswith("\\")

    assert "compatibility shim" in shim
    assert "Invoke-QuietRunPackage.ps1" in shim
    assert "canonical operator-facing runner" in shim

    assert "compatibility shim" in doc
    assert "Invoke-QuietRunPackage.ps1" in doc
    assert "canonical operator-facing runner" in doc
