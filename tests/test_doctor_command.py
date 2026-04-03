from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_doctor_command_outputs_json() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, '-m', 'patchops.cli', 'doctor', '--profile', 'trader'],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data['profile_requested'] == 'trader'
    assert 'available_profiles' in data
    assert 'ok' in data
    assert 'issue_count' in data


def test_doctor_command_with_generic_profile() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, '-m', 'patchops.cli', 'doctor', '--profile', 'generic_python'],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data['profile_requested'] == 'generic_python'
    assert 'generic_python' in data['available_profiles']
