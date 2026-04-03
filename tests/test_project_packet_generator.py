from __future__ import annotations

from pathlib import Path

from patchops.project_packets import build_project_packet, default_project_packet_path, scaffold_project_packet


def test_build_project_packet_contains_required_sections(tmp_path) -> None:
    content = build_project_packet(
        project_name="Trader",
        target_root=r"C:\dev\trader",
        profile_name="trader",
        wrapper_project_root=tmp_path,
        initial_goals=["Create a first narrow manifest", "Keep PowerShell thin"],
    )

    required_fragments = [
        "# Project packet â€” Trader",
        "## 1. Target identity",
        "## 2. Target roots and runtime",
        "## 3. Selected PatchOps profile",
        "## 4. What PatchOps owns",
        "## 5. What must remain outside PatchOps",
        "## 6. Recommended examples and starting surfaces",
        "## 7. Phase guidance",
        "## 8. Current development state",
        "### Mutable status",
        "**Current phase:** Initial onboarding",
        "**Current objective:** Create the first narrow target-specific manifest.",
        "**Latest passed patch:** (none yet)",
        "**Next action:** Run check, inspect, and plan before the first apply or verify execution.",
        r"`C:\dev\trader`",
        "`trader`",
    ]

    for fragment in required_fragments:
        assert fragment in content, f"Missing fragment: {fragment}"


def test_scaffold_project_packet_writes_expected_location_and_is_deterministic(tmp_path) -> None:
    payload_one = scaffold_project_packet(
        project_name="OSM Remediation",
        target_root=r"C:\dev\osm",
        profile_name="generic_python",
        wrapper_project_root=tmp_path,
        initial_goals=["Document the target", "Write the first patch"],
    )
    payload_two = scaffold_project_packet(
        project_name="OSM Remediation",
        target_root=r"C:\dev\osm",
        profile_name="generic_python",
        wrapper_project_root=tmp_path,
        initial_goals=["Document the target", "Write the first patch"],
    )

    packet_path = Path(payload_one["packet_path"])
    assert packet_path == default_project_packet_path("OSM Remediation", wrapper_project_root=tmp_path)
    assert packet_path.exists()

    first_content = packet_path.read_text(encoding="utf-8")
    second_content = Path(payload_two["packet_path"]).read_text(encoding="utf-8")
    assert first_content == second_content
    assert "docs/projects/osm_remediation.md" in first_content
    assert "- Document the target" in first_content
    assert "- Write the first patch" in first_content