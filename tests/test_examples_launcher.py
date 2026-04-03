from __future__ import annotations

from pathlib import Path


def test_examples_launcher_exists_and_targets_examples() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    launcher = repo_root / 'powershell' / 'Invoke-PatchExamples.ps1'
    text = launcher.read_text(encoding='utf-8')
    assert launcher.exists()
    assert 'patchops.cli' in text
    assert 'examples' in text
