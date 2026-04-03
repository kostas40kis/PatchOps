from __future__ import annotations

import json
from pathlib import Path

from patchops.cli import main
from patchops.project_packets import bootstrap_target_onboarding


def test_bootstrap_target_onboarding_writes_expected_artifacts(tmp_path) -> None:
    payload = bootstrap_target_onboarding(
        project_name="OSM Remediation",
        target_root=r"C:\dev\osm",
        profile_name="generic_python",
        wrapper_project_root=tmp_path,
        initial_goals=["Document the target", "Create the first manifest"],
        starter_intent="documentation_patch",
    )

    onboarding_root = tmp_path / "onboarding"
    bootstrap_md = onboarding_root / "current_target_bootstrap.md"
    bootstrap_json = onboarding_root / "current_target_bootstrap.json"
    next_prompt = onboarding_root / "next_prompt.txt"
    starter_manifest = onboarding_root / "starter_manifest.json"

    assert payload["written"] is True
    assert payload["project_name"] == "OSM Remediation"
    assert payload["packet_path"].endswith("docs/projects/osm_remediation.md")
    assert payload["starter_manifest_path"] == str(starter_manifest.resolve())
    assert bootstrap_md.exists()
    assert bootstrap_json.exists()
    assert next_prompt.exists()
    assert starter_manifest.exists()

    md_text = bootstrap_md.read_text(encoding="utf-8")
    assert "# Current target bootstrap" in md_text
    assert "OSM Remediation" in md_text
    assert "Read these docs first:" in md_text
    assert "docs/projects/osm_remediation.md" in md_text

    json_payload = json.loads(bootstrap_json.read_text(encoding="utf-8"))
    assert json_payload["selected_profile"] == "generic_python"
    assert json_payload["starter_intent"] == "documentation_patch"
    assert json_payload["target_root"] == r"C:\dev\osm"
    assert json_payload["generic_docs"][0] == "README.md"

    starter_payload = json.loads(starter_manifest.read_text(encoding="utf-8"))
    assert starter_payload["active_profile"] == "generic_python"
    assert starter_payload["target_project_root"] == r"C:\dev\osm"
    assert starter_payload["intent"] == "documentation_patch"
    assert starter_payload["project_packet_path"].endswith("docs/projects/osm_remediation.md")

    prompt_text = next_prompt.read_text(encoding="utf-8")
    assert "Read these docs first:" in prompt_text
    assert "docs/projects/osm_remediation.md" in prompt_text
    assert "Then create or adapt the first manifest conservatively." in prompt_text


def test_bootstrap_target_cli_writes_bundle_and_returns_json(capsys, tmp_path) -> None:
    exit_code = main(
        [
            "bootstrap-target",
            "--project-name",
            "Wrapper Self Hosted",
            "--target-root",
            r"C:\dev\patchops",
            "--profile",
            "generic_python",
            "--wrapper-root",
            str(tmp_path),
            "--starter-intent",
            "documentation_patch",
            "--initial-goal",
            "Create onboarding bundle",
            "--initial-goal",
            "Create starter manifest stub",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)

    onboarding_root = tmp_path / "onboarding"
    assert payload["project_name"] == "Wrapper Self Hosted"
    assert Path(payload["packet_path"]).exists()
    assert (onboarding_root / "current_target_bootstrap.md").exists()
    assert (onboarding_root / "current_target_bootstrap.json").exists()
    assert (onboarding_root / "next_prompt.txt").exists()
    assert (onboarding_root / "starter_manifest.json").exists()
