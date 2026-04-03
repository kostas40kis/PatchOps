from __future__ import annotations

import json
from pathlib import Path

from patchops.cli import main
from patchops.project_packets import build_onboarding_bootstrap


def test_build_onboarding_bootstrap_writes_expected_files(tmp_path) -> None:
    payload = build_onboarding_bootstrap(
        project_name="OSM Remediation",
        target_root=r"C:\dev\osm",
        profile_name="generic_python",
        wrapper_project_root=tmp_path,
        initial_goals=["Document the target", "Choose the first safe manifest"],
        current_stage="Discovery",
    )

    bootstrap_md = Path(payload["bootstrap_markdown_path"])
    bootstrap_json = Path(payload["bootstrap_json_path"])
    next_prompt = Path(payload["next_prompt_path"])
    starter_manifest = Path(payload["starter_manifest_path"])

    assert payload["written"] is True
    assert bootstrap_md.exists()
    assert bootstrap_json.exists()
    assert next_prompt.exists()
    assert starter_manifest.exists()

    md_text = bootstrap_md.read_text(encoding="utf-8")
    assert "# Onboarding bootstrap - OSM Remediation" in md_text
    assert r"`C:\dev\osm`" in md_text
    assert "`generic_python`" in md_text
    assert "Choose the first safe manifest" in md_text

    json_payload = json.loads(bootstrap_json.read_text(encoding="utf-8"))
    assert json_payload["project_name"] == "OSM Remediation"
    assert json_payload["profile_name"] == "generic_python"
    assert json_payload["current_stage"] == "Discovery"

    starter_payload = json.loads(starter_manifest.read_text(encoding="utf-8"))
    assert starter_payload["active_profile"] == "generic_python"
    assert starter_payload["patch_name"] == "bootstrap_verify_only"
    assert starter_payload["files_to_write"] == []


def test_bootstrap_target_command_prints_json_and_writes_artifacts(capsys, tmp_path) -> None:
    exit_code = main(
        [
            "bootstrap-target",
            "--project-name",
            "Demo Project",
            "--target-root",
            r"C:\dev\demo",
            "--profile",
            "generic_python",
            "--wrapper-root",
            str(tmp_path),
            "--initial-goal",
            "Create the packet",
            "--initial-goal",
            "Run check inspect and plan",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["written"] is True
    assert payload["project_name"] == "Demo Project"
    assert Path(payload["bootstrap_markdown_path"]).exists()
    assert Path(payload["bootstrap_json_path"]).exists()
    assert Path(payload["next_prompt_path"]).exists()
    assert Path(payload["starter_manifest_path"]).exists()
