from __future__ import annotations

import json
from pathlib import Path

from patchops.cli import main


def test_onboarding_helper_roundtrip_for_generic_target(capsys, tmp_path) -> None:
    target_root = r"C:\dev\demo_roundtrip"
    packet_path = tmp_path / "docs" / "projects" / "demo_roundtrip.md"
    report_path = tmp_path / "reports" / "demo_roundtrip_report.txt"

    exit_code = main([
        "recommend-profile",
        "--target-root",
        target_root,
    ])
    assert exit_code == 0
    recommend_payload = json.loads(capsys.readouterr().out)
    assert recommend_payload["recommended_profile"] == "generic_python"
    assert recommend_payload["target_root"] == target_root
    assert "examples/generic_python_verify_patch.json" in recommend_payload["starter_examples"]

    exit_code = main([
        "init-project-doc",
        "--project-name",
        "Demo Roundtrip",
        "--target-root",
        target_root,
        "--profile",
        "generic_python",
        "--wrapper-root",
        str(tmp_path),
        "--output-path",
        str(packet_path),
        "--initial-goal",
        "Create the packet",
        "--initial-goal",
        "Generate the first starter manifest",
    ])
    assert exit_code == 0
    init_payload = json.loads(capsys.readouterr().out)
    assert Path(init_payload["packet_path"]) == packet_path.resolve()
    assert packet_path.exists()

    initial_text = packet_path.read_text(encoding="utf-8")
    lowered_initial = initial_text.lower()
    assert "project packet" in lowered_initial
    assert "demo roundtrip" in lowered_initial
    assert target_root.lower() in lowered_initial
    assert "selected patchops profile" in lowered_initial
    assert "what must remain outside patchops" in lowered_initial
    assert "current development state" in lowered_initial or "current state" in lowered_initial

    exit_code = main([
        "starter",
        "--profile",
        "generic_python",
        "--intent",
        "documentation_patch",
        "--target-root",
        target_root,
    ])
    assert exit_code == 0
    starter_payload = json.loads(capsys.readouterr().out)
    assert starter_payload["intent"] == "documentation_patch"
    assert starter_payload["manifest"]["active_profile"] == "generic_python"
    assert starter_payload["manifest"]["target_project_root"] == target_root
    assert starter_payload["starter_examples"] == ["examples/generic_python_doc_patch.json"]

    manifest_path = tmp_path / "generated" / "starter_documentation_patch.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(starter_payload["manifest"], indent=2) + "\n", encoding="utf-8")
    assert manifest_path.exists()

    exit_code = main([
        "refresh-project-doc",
        "--project-name",
        "Demo Roundtrip",
        "--wrapper-root",
        str(tmp_path),
        "--packet-path",
        str(packet_path),
        "--report-path",
        str(report_path),
        "--current-phase",
        "Phase 1 - onboarding rehearsal",
        "--current-objective",
        "Prove the helper roundtrip stays aligned.",
        "--latest-passed-patch",
        "Patch 84",
        "--latest-attempted-patch",
        "Patch 85",
        "--current-recommendation",
        "Use the starter manifest as a narrow documentation-only starting point.",
        "--next-action",
        "Run check, inspect, and plan against the generated starter manifest.",
        "--blocker",
        "No blocking repo issue is known; validate the generated manifest before apply.",
    ])
    assert exit_code == 0
    refresh_payload = json.loads(capsys.readouterr().out)
    assert Path(refresh_payload["packet_path"]) == packet_path.resolve()

    refreshed_text = packet_path.read_text(encoding="utf-8")
    lowered_refreshed = refreshed_text.lower()
    assert target_root.lower() in lowered_refreshed
    assert "phase 1 - onboarding rehearsal" in lowered_refreshed
    assert "patch 84" in lowered_refreshed
    assert "patch 85" in lowered_refreshed
    assert "run check, inspect, and plan against the generated starter manifest" in lowered_refreshed
    assert str(report_path).lower() in lowered_refreshed
    assert "what must remain outside patchops" in lowered_refreshed
