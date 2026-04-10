from __future__ import annotations

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


def _run_patchops_entry(script_path: Path, cwd: Path, *patchops_args: str) -> subprocess.CompletedProcess[str]:
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
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True)


def test_emitted_patchops_entry_ps1_profiles_works_outside_wrapper_root_cwd(tmp_path: Path) -> None:
    script_path = _emit_patchops_entry(tmp_path / "emit_patchops_entry_profiles_outside_cwd.ps1")
    neutral_cwd = tmp_path / "outside_wrapper_root"
    neutral_cwd.mkdir()

    completed = _run_patchops_entry(script_path, neutral_cwd, "profiles")

    assert completed.returncode == 0, (
        "Generated patchops-entry-ps1 script failed for profiles when launched outside the wrapper root.\n"
        f"stdout:\n{completed.stdout}\n\n"
        f"stderr:\n{completed.stderr}"
    )
    assert "ModuleNotFoundError" not in completed.stderr
    assert "generic_python" in completed.stdout
    assert "trader" in completed.stdout
