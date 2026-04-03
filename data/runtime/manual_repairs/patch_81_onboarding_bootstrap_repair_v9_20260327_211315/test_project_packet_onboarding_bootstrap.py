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

    assert payload["written"] is True
    bootstrap_md = Path(payload["bootstrap_markdown_path"])
    bootstrap_json = Path(payload["bootstrap_json_path"])
    next_prompt = Path(payload["next_prompt_path"])
    starter_manifest = Path(payload["starter_manifest_path"])

    assert bootstrap_md.exists()
    assert bootstrap_json.exists()
    assert next_prompt.exists()
    assert starter_manifest.exists()

    md_text = bootstrap_md.read_text(encoding="utf-8")
    assert md_text.startswith("# Current target bootstrap - OSM Remediation")
    assert "documentation_patch" in md_text
    assert "Create the first manifest" in md_text

    bootstrap_payload = json.loads(bootstrap_json.read_text(encoding="utf-8"))
    assert bootstrap_payload["project_name"] == "OSM Remediation"
    assert bootstrap_payload["starter_intent"] == "documentation_patch"

    starter_payload = json.loads(starter_manifest.read_text(encoding="utf-8"))
    assert starter_payload["active_profile"] == "generic_python"
    assert starter_payload["intent"] == "documentation_patch"


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
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["written"] is True
    assert payload["project_name"] == "Wrapper Self Hosted"
    assert payload["starter_intent"] == "documentation_patch"
    assert Path(payload["bootstrap_markdown_path"]).exists()
    assert Path(payload["starter_manifest_path"]).exists()
