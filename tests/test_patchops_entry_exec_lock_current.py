from __future__ import annotations

import json
import subprocess
from pathlib import Path

from patchops.operator_scripts import emit_operator_script


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _powershell_exe() -> str:
    candidate = Path(r"C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.EXE")
    assert candidate.exists(), f"Windows PowerShell 5.1 executable not found: {candidate}"
    return str(candidate)


def _emit_patchops_entry(script_path: Path) -> Path:
    result = emit_operator_script(
        script_path,
        script_kind="patchops-entry-ps1",
        wrapper_project_root=str(PROJECT_ROOT),
    )
    assert result.ok is True
    assert result.output_path.exists()
    return result.output_path


def _run_patchops_entry(script_path: Path, *patchops_args: str) -> subprocess.CompletedProcess[str]:
    command = [
        _powershell_exe(),
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        "-WrapperRepoRoot",
        str(PROJECT_ROOT),
        *patchops_args,
    ]
    return subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True)


def test_emitted_patchops_entry_ps1_forwards_profiles_against_live_repo(tmp_path: Path) -> None:
    script_path = _emit_patchops_entry(tmp_path / "emit_patchops_entry_profiles.ps1")
    completed = _run_patchops_entry(script_path, "profiles")

    assert completed.returncode == 0, (
        "Generated patchops-entry-ps1 script failed for profiles.\n"
        f"stdout:\n{completed.stdout}\n\n"
        f"stderr:\n{completed.stderr}"
    )
    assert "generic_python" in completed.stdout
    assert "trader" in completed.stdout


def test_emitted_patchops_entry_ps1_forwards_maintenance_gate_against_live_repo(tmp_path: Path) -> None:
    script_path = _emit_patchops_entry(tmp_path / "emit_patchops_entry_maintenance_gate.ps1")
    completed = _run_patchops_entry(script_path, "maintenance-gate")

    assert completed.returncode == 0, (
        "Generated patchops-entry-ps1 script failed for maintenance-gate.\n"
        f"stdout:\n{completed.stdout}\n\n"
        f"stderr:\n{completed.stderr}"
    )
    payload = json.loads(completed.stdout)
    assert payload["wrapper_project_root"] == str(PROJECT_ROOT)
    assert payload["gate_results"]["bundle_manifest_regression"]["name"] == "bundle_manifest_regression"


def test_emitted_patchops_entry_ps1_forwards_setup_windows_env_dry_run_against_live_repo(tmp_path: Path) -> None:
    script_path = _emit_patchops_entry(tmp_path / "emit_patchops_entry_setup_windows_env.ps1")
    reports_root = tmp_path / "Desktop" / "PatchOpsReports"
    bin_root = tmp_path / "bin" / "PatchOps"
    completed = _run_patchops_entry(
        script_path,
        "setup-windows-env",
        "--dry-run",
        "--wrapper-root",
        str(PROJECT_ROOT),
        "--reports-root",
        str(reports_root),
        "--bin-root",
        str(bin_root),
    )

    assert completed.returncode == 0, (
        "Generated patchops-entry-ps1 script failed for setup-windows-env --dry-run.\n"
        f"stdout:\n{completed.stdout}\n\n"
        f"stderr:\n{completed.stderr}"
    )
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["applied"] is False
    assert payload["dry_run"] is True
    assert payload["env_vars"]["PATCHOPS_WRAPPER_ROOT"] == str(PROJECT_ROOT.resolve())
    assert payload["env_vars"]["PATCHOPS_REPORTS_ROOT"] == str(reports_root)
    assert payload["env_vars"]["PATCHOPS_BIN"] == str(bin_root)
