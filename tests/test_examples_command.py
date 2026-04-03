from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_examples_command_outputs_json() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "examples"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["example_count"] >= 1
    assert any(item["file_name"] == "generic_backup_patch.json" for item in payload["examples"])


def test_examples_command_profile_filter() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "examples", "--profile", "generic_python"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["example_count"] >= 1
    assert all(item["active_profile"] == "generic_python" for item in payload["examples"])
