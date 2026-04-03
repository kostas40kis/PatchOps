from __future__ import annotations

import json
from pathlib import Path

from patchops.project_packets import (
    build_project_packet,
    refresh_project_packet,
    refresh_project_packet_content,
    scaffold_project_packet,
)


def _assert_packet_header(content: str, project_name: str) -> None:
    first_line = content.splitlines()[0]
    assert first_line.startswith("# Project packet")
    assert project_name in first_line


def test_refresh_project_packet_content_updates_mutable_status_but_preserves_stable_sections(tmp_path) -> None:
    original = build_project_packet(
        project_name="Trader",
        target_root=r"C:\dev\trader",
        profile_name="trader",
        wrapper_project_root=tmp_path,
        initial_goals=["Create a first narrow manifest"],
    )

    updated = refresh_project_packet_content(
        original,
        current_phase="Phase C",
        current_objective="Add refresh support",
        latest_passed_patch="patch_77",
        latest_attempted_patch="patch_78",
        latest_known_report_path=r"C:\Users\kostas\Desktop\patch_78.txt",
        current_recommendation="Use refresh-project-doc conservatively.",
        next_action="Run compile and packet tests.",
        current_blockers=["Wrapper compatibility needs checking."],
        outstanding_risks=["Overwriting stable packet sections."],
    )

    _assert_packet_header(updated, "Trader")
    assert "## 1. Target identity" in updated
    assert r"`C:\dev\trader`" in updated
    assert "## 8. Current development state" in updated
    assert "**Current phase:** Phase C" in updated
    assert "**Current objective:** Add refresh support" in updated
    assert "**Latest passed patch:** patch_77" in updated
    assert "**Latest attempted patch:** patch_78" in updated
    assert r"**Latest known report path:** C:\Users\kostas\Desktop\patch_78.txt" in updated
    assert "**Current recommendation:** Use refresh-project-doc conservatively." in updated
    assert "**Next action:** Run compile and packet tests." in updated
    assert "- Wrapper compatibility needs checking." in updated
    assert "- Overwriting stable packet sections." in updated


def test_refresh_project_packet_uses_handoff_json_conservatively(tmp_path) -> None:
    scaffold_payload = scaffold_project_packet(
        project_name="OSM Remediation",
        target_root=r"C:\dev\osm",
        profile_name="generic_python",
        wrapper_project_root=tmp_path,
        initial_goals=["Document the target", "Write the first patch"],
    )

    handoff_path = tmp_path / "handoff.json"
    handoff_path.write_text(
        json.dumps(
            {
                "latest_passed_patch": "patch_77",
                "latest_attempted_patch": "patch_78",
                "next_action": "Run refresh validation.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = refresh_project_packet(
        project_name="OSM Remediation",
        wrapper_project_root=tmp_path,
        handoff_json_path=handoff_path,
        latest_report_path=r"C:\Users\kostas\Desktop\patch_78_report.txt",
        current_phase="Phase C",
        current_objective="Refresh packet state from known artifacts.",
        current_recommendation="Stay conservative and preserve stable sections.",
    )

    packet_path = Path(scaffold_payload["packet_path"])
    content = packet_path.read_text(encoding="utf-8")

    assert payload["written"] is True
    assert payload["project_name"] == "OSM Remediation"
    assert payload["packet_path"] == str(packet_path.resolve())
    assert "patch_77" in content
    assert "patch_78" in content
    assert r"C:\Users\kostas\Desktop\patch_78_report.txt" in content
    assert "Run refresh validation." in content
    _assert_packet_header(content, "OSM Remediation")