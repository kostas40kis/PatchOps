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

    onboarding_dir = tmp_path / "onboarding"
    assert payload["written"] is True
    assert payload["project_name"] == "OSM Remediation"
    assert Path(payload["onboarding_dir"]).resolve() == onboarding_dir.resolve()

    md_path = onboarding_dir / "current_target_bootstrap.md"
    json_path = onboarding_dir / "current_target_bootstrap.json"
    prompt_path = onboarding_dir / "next_prompt.txt"
    starter_path = onboarding_dir / "starter_manifest.json"

    assert md_path.exists()
    assert json_path.exists()
    assert prompt_path.exists()
    assert starter_path.exists()

    md_text = md_path.read_text(encoding="utf-8")
    json_payload = json.loads(json_path.read_text(encoding="utf-8"))
    prompt_text = prompt_path.read_text(encoding="utf-8")
    starter_payload = json.loads(starter_path.read_text(encoding="utf-8"))

    assert "OSM Remediation" in md_text
    assert json_payload["project_name"] == "OSM Remediation"
    assert "Create the first target packet" in prompt_text or "Use the generated onboarding bundle" in prompt_text
    assert starter_payload["active_profile"] == "generic_python"


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

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["project_name"] == "Wrapper Self Hosted"
    assert Path(payload["onboarding_dir"]).exists()
    assert (Path(payload["onboarding_dir"]) / "current_target_bootstrap.md").exists()
    assert (Path(payload["onboarding_dir"]) / "starter_manifest.json").exists()
