from __future__ import annotations

from pathlib import Path


def test_doctor_launcher_exists_and_targets_doctor() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    launcher = repo_root / 'powershell' / 'Invoke-PatchDoctor.ps1'
    assert launcher.exists()
    text = launcher.read_text(encoding='utf-8')
    assert 'patchops.cli' in text
    assert 'doctor' in text
    assert '--profile' in text
