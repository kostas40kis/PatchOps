from __future__ import annotations

import json

from patchops.cli import main


def test_starter_command_prints_json(capsys) -> None:
    exit_code = main([
        "starter",
        "--profile",
        "generic_python",
        "--intent",
        "documentation_patch",
        "--target-root",
        r"C:\dev\demo",
    ])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["intent"] == "documentation_patch"
    assert payload["manifest"]["active_profile"] == "generic_python"
    assert payload["manifest"]["target_project_root"] == r"C:\dev\demo"
    assert payload["starter_examples"] == ["examples/generic_python_patch.json"]
