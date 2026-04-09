from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from patchops.operator_scripts import emit_operator_script, render_operator_script


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _powershell_exe() -> str:
    candidates = [
        shutil.which("powershell"),
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    pytest.skip("powershell.exe not available for operator script live execution")


def test_run_package_operator_script_contains_repo_owned_command_and_ps51_argument_fallback() -> None:
    script = render_operator_script(
        "run-package-zip",
        wrapper_project_root=r"C:\dev\patchops",
        default_bundle_zip_path=r"D:\patch_22_bundle.zip",
    )

    assert script.startswith("[CmdletBinding()]")
    assert "param(" in script
    assert "patchops.cli', 'run-package'" in script
    assert "D:\\patch_22_bundle.zip" in script
    assert "$psi.PSObject.Properties['ArgumentList']" in script
    assert "$psi.Arguments = [string]::Join(' '" in script
    assert "ConvertTo-PatchOpsPsArgument" in script
    assert "Invoke-PatchOpsNative" in script


def test_maintenance_gate_operator_script_contains_repo_owned_command_and_optional_report_support() -> None:
    script = render_operator_script(
        "maintenance-gate",
        wrapper_project_root=r"C:\dev\patchops",
    )

    assert script.startswith("[CmdletBinding()]")
    assert "patchops.cli', 'maintenance-gate'" in script
    assert "--wrapper-root" in script
    assert "--core-tests-green" in script
    assert "--report-path" in script
    assert "$psi.PSObject.Properties['ArgumentList']" in script
    assert "$psi.Arguments = [string]::Join(' '" in script


def test_emit_operator_script_writes_utf8_powershell_file(tmp_path: Path) -> None:
    output_path = tmp_path / "scripts" / "run_patch_bundle.ps1"
    result = emit_operator_script(
        output_path,
        script_kind="run-package-zip",
        wrapper_project_root=r"C:\dev\patchops",
        default_bundle_zip_path=r"D:\patch_22_bundle.zip",
    )

    assert result.ok is True
    assert result.issue_count == 0
    assert result.output_path == output_path.resolve()
    text = output_path.read_text(encoding="utf-8")
    assert text == render_operator_script(
        "run-package-zip",
        wrapper_project_root=r"C:\dev\patchops",
        default_bundle_zip_path=r"D:\patch_22_bundle.zip",
    )


def test_operator_script_docs_mention_emitted_run_package_and_maintenance_gate_surfaces() -> None:
    quickstart = Path("docs/operator_quickstart.md").read_text(encoding="utf-8")
    emitter_doc = Path("docs/operator_script_emitter.md").read_text(encoding="utf-8")

    assert "emit-operator-script" in quickstart
    assert "run-package-zip" in quickstart
    assert "maintenance-gate" in quickstart
    assert "ArgumentList" in emitter_doc
    assert "Windows PowerShell 5.1" in emitter_doc
    assert "repo-owned template" in emitter_doc


def test_emitted_maintenance_gate_script_executes_against_live_repo(tmp_path: Path) -> None:
    powershell_exe = _powershell_exe()
    script_path = tmp_path / "emit_patchops_maintenance_gate.ps1"
    result = emit_operator_script(
        script_path,
        script_kind="maintenance-gate",
        wrapper_project_root=str(PROJECT_ROOT),
    )
    assert result.ok is True

    command = [
        powershell_exe,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        "-WrapperRepoRoot",
        str(PROJECT_ROOT),
    ]
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 0, (
        f"Generated maintenance gate script failed.\nstdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}"
    )
    payload = json.loads(completed.stdout)
    assert payload["wrapper_project_root"] == str(PROJECT_ROOT)
    assert payload["gate_results"]["bundle_manifest_regression"]["name"] == "bundle_manifest_regression"
    assert payload["gate_results"]["post_build_bundle_smoke"]["name"] == "post_build_bundle_smoke"
    assert payload["gate_results"]["release_readiness"]["name"] == "release_readiness"
