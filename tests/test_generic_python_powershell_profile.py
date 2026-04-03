from pathlib import Path

import patchops.profiles.generic_python_powershell as mixed_profile


def test_generic_python_powershell_runtime_candidates_are_conservative(tmp_path: Path) -> None:
    candidates = mixed_profile.generic_python_powershell_runtime_candidates(tmp_path)

    assert candidates[0] == str(tmp_path / ".venv" / "Scripts" / "python.exe")
    assert "py" in candidates
    assert "python" in candidates
    assert "pwsh" in candidates
    assert "powershell" in candidates


def test_generic_python_powershell_profile_summary_is_explicit(tmp_path: Path) -> None:
    summary = mixed_profile.generic_python_powershell_profile_summary(tmp_path)

    assert summary["profile_name"] == "generic_python_powershell"
    assert summary["markers"] == ("python", "powershell")
    assert summary["conservative"] is True
    assert summary["runtime_candidates"][0] == str(tmp_path / ".venv" / "Scripts" / "python.exe")
    assert any("mixed Python and PowerShell" in note for note in summary["notes"])


def test_generic_python_powershell_profile_markers_stay_explicit() -> None:
    assert mixed_profile.PATCHOPS_GENERIC_PYTHON_POWERSHELL_PROFILE_NAME == "generic_python_powershell"
    assert mixed_profile.PATCHOPS_GENERIC_PYTHON_POWERSHELL_MARKERS == ("python", "powershell")
