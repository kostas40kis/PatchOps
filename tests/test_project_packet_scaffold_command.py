from __future__ import annotations

import json
from pathlib import Path

from patchops.cli import main


def test_init_project_doc_command_writes_packet_and_returns_json(capsys, tmp_path) -> None:
    exit_code = main(
        [
            "init-project-doc",
            "--project-name",
            "OSM Remediation",
            "--target-root",
            r"C:\dev\osm",
            "--profile",
            "generic_python",
            "--wrapper-root",
            str(tmp_path),
            "--initial-goal",
            "Document the target contract",
            "--initial-goal",
            "Create the first manifest",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)

    packet_path = Path(payload["packet_path"])
    assert payload["written"] is True
    assert payload["project_name"] == "OSM Remediation"
    assert payload["project_slug"] == "osm_remediation"
    assert payload["profile_name"] == "generic_python"
    assert payload["target_root"] == r"C:\dev\osm"
    assert payload["initial_goal_count"] == 2
    assert packet_path.exists()

    content = packet_path.read_text(encoding="utf-8")
    assert "# Project packet â€” OSM Remediation" in content
    assert "## 8. Current development state" in content
    assert "- Document the target contract" in content
    assert "- Create the first manifest" in content


def test_init_project_doc_command_respects_output_path(capsys, tmp_path) -> None:
    explicit_output = tmp_path / "custom" / "wrapper_self_hosted.md"

    exit_code = main(
        [
            "init-project-doc",
            "--project-name",
            "Wrapper Self Hosted",
            "--target-root",
            r"C:\dev\patchops",
            "--profile",
            "generic_python",
            "--wrapper-root",
            str(tmp_path),
            "--output-path",
            str(explicit_output),
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert Path(payload["packet_path"]) == explicit_output.resolve()
    assert explicit_output.exists()