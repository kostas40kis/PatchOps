from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = PROJECT_ROOT / "docs" / "projects" / "demo_roundtrip_current.md"
BOOTSTRAP_ROOT = PROJECT_ROOT / "onboarding"


def test_current_demo_project_packet_exists_and_is_target_facing() -> None:
    assert PACKET_PATH.exists(), f"Missing demo packet: {PACKET_PATH}"

    text = PACKET_PATH.read_text(encoding="utf-8")
    lowered = text.lower()

    assert "project packet" in lowered
    assert "demo roundtrip current" in lowered
    assert "selected patchops profile" in lowered
    assert "what must remain outside patchops" in lowered
    assert "current development state" in lowered or "current state" in lowered


def test_current_onboarding_bootstrap_artifacts_exist() -> None:
    required = [
        BOOTSTRAP_ROOT / "current_target_bootstrap.md",
        BOOTSTRAP_ROOT / "current_target_bootstrap.json",
        BOOTSTRAP_ROOT / "next_prompt.txt",
        BOOTSTRAP_ROOT / "starter_manifest.json",
    ]
    for path in required:
        assert path.exists(), f"Missing onboarding artifact: {path}"


def test_current_onboarding_bootstrap_payload_matches_demo_target() -> None:
    payload = json.loads((BOOTSTRAP_ROOT / "current_target_bootstrap.json").read_text(encoding="utf-8"))
    starter_manifest = json.loads((BOOTSTRAP_ROOT / "starter_manifest.json").read_text(encoding="utf-8"))
    bootstrap_md = (BOOTSTRAP_ROOT / "current_target_bootstrap.md").read_text(encoding="utf-8")
    next_prompt = (BOOTSTRAP_ROOT / "next_prompt.txt").read_text(encoding="utf-8")

    assert payload["project_name"] == "Demo Roundtrip Current"
    assert payload["selected_profile"] == "generic_python"
    assert payload["written"] is True
    assert Path(payload["packet_path"]) == PACKET_PATH.resolve()

    assert Path(payload["bootstrap_markdown_path"]) == (BOOTSTRAP_ROOT / "current_target_bootstrap.md").resolve()
    assert Path(payload["bootstrap_json_path"]) == (BOOTSTRAP_ROOT / "current_target_bootstrap.json").resolve()
    assert Path(payload["next_prompt_path"]) == (BOOTSTRAP_ROOT / "next_prompt.txt").resolve()
    assert Path(payload["starter_manifest_path"]) == (BOOTSTRAP_ROOT / "starter_manifest.json").resolve()

    assert starter_manifest["active_profile"] == "generic_python"
    assert starter_manifest["patch_name"] == "bootstrap_verify_only"
    assert starter_manifest["target_project_root"]

    assert "# Onboarding bootstrap - Demo Roundtrip Current" in bootstrap_md
    assert "## 2. Suggested reading order" in bootstrap_md
    assert "docs/project_packet_contract.md" in bootstrap_md
    assert "docs/project_packet_workflow.md" in bootstrap_md
    assert "## 4. Recommended command order" in bootstrap_md

    assert "You are onboarding the target project 'Demo Roundtrip Current' into PatchOps." in next_prompt
    assert "Read the generic PatchOps packet first, then use the project packet." in next_prompt
    assert "Selected profile: generic_python" in next_prompt
    assert "Then run check, inspect, and plan before any apply or verify-only execution." in next_prompt


def test_status_and_finalization_docs_track_patch_129_onboarding_proof() -> None:
    project_status = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
    finalization_master = (PROJECT_ROOT / "docs" / "finalization_master_plan.md").read_text(encoding="utf-8")

    assert "## Patch 129 - new-target onboarding flow proof" in project_status
    assert "latest confirmed green head: Patch 129" in project_status
    assert "remaining finalization sequence is F6 through F8, not a redesign wave" in project_status

    assert "## Patch 129 - prove new-target onboarding flow" in finalization_master
    assert "- **Latest confirmed green head:** Patch 129" in finalization_master
    assert "- **F6 — final release / maintenance gate**" in finalization_master
