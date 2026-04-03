from __future__ import annotations

import json
from pathlib import Path

from patchops.cli import main
from patchops.project_packets import build_onboarding_bootstrap


def _read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_current_onboarding_bootstrap_payload_matches_demo_target(capsys, tmp_path) -> None:
    wrapper_root = tmp_path

    direct_payload = build_onboarding_bootstrap(
        project_name="Demo Target",
        target_root=r"C:\\dev\\demo_target",
        profile_name="generic_python",
        wrapper_project_root=wrapper_root,
        initial_goals=["Create the packet", "Run check inspect and plan"],
    )
    expected_json = _read_json(direct_payload["bootstrap_json_path"])

    exit_code = main(
        [
            "bootstrap-target",
            "--project-name",
            "Demo Target",
            "--target-root",
            r"C:\\dev\\demo_target",
            "--profile",
            "generic_python",
            "--wrapper-root",
            str(wrapper_root),
            "--initial-goal",
            "Create the packet",
            "--initial-goal",
            "Run check inspect and plan",
        ]
    )

    assert exit_code == 0
    cli_payload = json.loads(capsys.readouterr().out)
    actual_json = _read_json(cli_payload["bootstrap_json_path"])

    assert cli_payload["written"] is True
    assert cli_payload["project_name"] == "Demo Target"
    assert Path(cli_payload["bootstrap_markdown_path"]).exists()
    assert Path(cli_payload["bootstrap_json_path"]).exists()
    assert Path(cli_payload["next_prompt_path"]).exists()
    assert Path(cli_payload["starter_manifest_path"]).exists()

    assert actual_json == expected_json
    assert actual_json["project_name"] == "Demo Target"
    assert actual_json["profile_name"] == "generic_python"

    md_text = Path(cli_payload["bootstrap_markdown_path"]).read_text(encoding="utf-8")
    assert "# Onboarding bootstrap - Demo Target" in md_text
    assert r"`C:\\dev\\demo_target`" in md_text

    next_prompt_text = Path(cli_payload["next_prompt_path"]).read_text(encoding="utf-8")
    assert "Demo Target" in next_prompt_text
    assert "generic_python" in next_prompt_text
