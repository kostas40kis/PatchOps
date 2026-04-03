from __future__ import annotations

import json

from patchops.cli import main


def test_recommend_profile_command_prints_json(capsys) -> None:
    exit_code = main([
        "recommend-profile",
        "--target-root",
        r"C:\dev\trader",
    ])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["recommended_profile"] == "trader"
    assert payload["target_root"] == r"C:\dev\trader"
    assert "starter_examples" in payload
