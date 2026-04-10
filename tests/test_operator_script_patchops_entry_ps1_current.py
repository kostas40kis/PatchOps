from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from patchops.operator_scripts import SUPPORTED_OPERATOR_SCRIPT_KINDS, emit_operator_script, render_operator_script

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _powershell_exe() -> str:
    candidates = [shutil.which("powershell"), r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    pytest.skip("powershell.exe not available for operator script execution test")


def test_patchops_entry_ps1_kind_is_supported() -> None:
    assert "patchops-entry-ps1" in SUPPORTED_OPERATOR_SCRIPT_KINDS


def test_patchops_entry_ps1_render_contains_patchops_passthrough() -> None:
    script = render_operator_script("patchops-entry-ps1", wrapper_project_root=str(PROJECT_ROOT))
    assert script.startswith("[CmdletBinding()]")
    assert "patchops.cli" in script
    assert "ValueFromRemainingArguments=$true" in script
    assert "$PatchOpsArguments" in script
    assert "$args" not in script


def test_emitted_patchops_entry_ps1_script_executes_profiles_against_live_repo(tmp_path: Path) -> None:
    powershell_exe = _powershell_exe()
    script_path = tmp_path / "emit_patchops_entry.ps1"
    result = emit_operator_script(script_path, script_kind="patchops-entry-ps1", wrapper_project_root=str(PROJECT_ROOT))
    assert result.ok is True

    command = [powershell_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path), "-WrapperRepoRoot", str(PROJECT_ROOT), "profiles"]
    completed = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True)

    assert completed.returncode == 0, f"Generated patchops-entry-ps1 script failed.\nstdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}"
    payload_text = completed.stdout + completed.stderr
    assert "generic_python" in payload_text
