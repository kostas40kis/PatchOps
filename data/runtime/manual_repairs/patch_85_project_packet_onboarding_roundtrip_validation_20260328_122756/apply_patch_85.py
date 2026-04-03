from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_project_packet_onboarding_roundtrip.py"
PATCH_LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"
PROJECT_STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def upsert_block(path: Path, start_marker: str, end_marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start_marker in text and end_marker in text:
        start_index = text.index(start_marker)
        end_index = text.index(end_marker, start_index) + len(end_marker)
        new_text = text[:start_index] + block + text[end_index:]
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        if text:
            text += "\n"
        new_text = text + block
    path.write_text(new_text.rstrip() + "\n", encoding="utf-8")


test_content = textwrap.dedent(
    """\
    from __future__ import annotations

    import json
    from pathlib import Path

    from patchops.cli import main


    def test_onboarding_helper_roundtrip_for_generic_target(capsys, tmp_path) -> None:
        target_root = r"C:\\dev\\demo_roundtrip"
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
        manifest_path.write_text(json.dumps(starter_payload["manifest"], indent=2) + "\\n", encoding="utf-8")
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
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH85_LEDGER:START -->
    ## Patch 85

    Patch 85 adds a combined onboarding-helper roundtrip validation surface.

    It proves that `recommend-profile`, `init-project-doc`, `starter`, and `refresh-project-doc` remain aligned for a conservative generic-target flow.

    The goal is to protect the helper-first onboarding story as one maintained operator flow without widening the PatchOps architecture.
    <!-- PATCHOPS_PATCH85_LEDGER:END -->
    """
)

project_status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH85_STATUS:START -->
    ## Patch 85 - onboarding helper roundtrip validation

    ### Current state

    - Patch 85 adds one combined validation test for the helper-first onboarding flow.
    - The new test exercises `recommend-profile`, `init-project-doc`, `starter`, and `refresh-project-doc` in one conservative roundtrip.
    - The goal is to protect helper alignment as a maintained operator-visible flow without widening the architecture.

    ### Why this matters

    - the onboarding layer is now protected as one practical flow, not only as isolated helper surfaces,
    - the patch stays maintenance-sized and validation-first,
    - handoff remains the resume surface for already-running work.

    ### Remaining posture

    - continue with maintenance, refinement, or target-specific expansion,
    - prefer narrow validation or repair patches before any new architecture work.
    <!-- PATCHOPS_PATCH85_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH85_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH85_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH85_STATUS:START -->",
    "<!-- PATCHOPS_PATCH85_STATUS:END -->",
    project_status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")