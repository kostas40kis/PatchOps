from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_current_handoff_bundle_exists_with_expected_files() -> None:
    handoff_root = PROJECT_ROOT / "handoff"

    required_files = [
        handoff_root / "current_handoff.md",
        handoff_root / "current_handoff.json",
        handoff_root / "latest_report_copy.txt",
        handoff_root / "latest_report_index.json",
        handoff_root / "next_prompt.txt",
        handoff_root / "bundle" / "current" / "current_handoff.md",
        handoff_root / "bundle" / "current" / "current_handoff.json",
        handoff_root / "bundle" / "current" / "latest_report_copy.txt",
        handoff_root / "bundle" / "current" / "latest_report_index.json",
        handoff_root / "bundle" / "current" / "next_prompt.txt",
    ]

    for path in required_files:
        assert path.exists(), f"Missing handoff artifact: {path}"


def test_current_handoff_json_keeps_resume_contract() -> None:
    current_handoff = _read_json(PROJECT_ROOT / "handoff" / "current_handoff.json")
    latest_index = _read_json(PROJECT_ROOT / "handoff" / "latest_report_index.json")

    assert "repo_state" in current_handoff
    assert "resume" in current_handoff
    assert "latest_patch" in current_handoff

    assert isinstance(current_handoff["repo_state"].get("latest_run_mode"), str)
    assert current_handoff["repo_state"]["latest_run_mode"]
    assert isinstance(current_handoff["resume"].get("next_recommended_mode"), str)
    assert current_handoff["resume"]["next_recommended_mode"]

    assert isinstance(latest_index.get("latest_attempted_patch"), str)
    assert latest_index["latest_attempted_patch"]
    assert isinstance(latest_index.get("next_recommended_mode"), str)
    assert latest_index["next_recommended_mode"]


def test_next_prompt_and_latest_report_copy_stay_mechanical() -> None:
    prompt_text = (PROJECT_ROOT / "handoff" / "next_prompt.txt").read_text(encoding="utf-8")
    report_text = (PROJECT_ROOT / "handoff" / "latest_report_copy.txt").read_text(encoding="utf-8")

    assert "handoff/current_handoff.md" in prompt_text
    assert "handoff/current_handoff.json" in prompt_text
    assert "handoff/latest_report_copy.txt" in prompt_text
    assert "next recommended action" in prompt_text.lower()

    assert "SUMMARY" in report_text
    assert "Result" in report_text


def test_status_and_finalization_docs_keep_patch_128_proof_visible_after_f5() -> None:
    project_status = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
    finalization_master = (PROJECT_ROOT / "docs" / "finalization_master_plan.md").read_text(encoding="utf-8")
    handoff_surface = (PROJECT_ROOT / "docs" / "handoff_surface.md").read_text(encoding="utf-8")

    assert "## Patch 128 - active-work continuation flow proof" in project_status
    assert "latest confirmed green head: Patch 129" in project_status
    assert "remaining finalization sequence is F6 through F8, not a redesign wave" in project_status

    assert "## Patch 128 - prove active-work continuation flow" in finalization_master
    assert "- **Latest confirmed green head:** Patch 129" in finalization_master
    assert "- **F6 — final release / maintenance gate**" in finalization_master

    assert "## Patch 128 - active-work continuation proof" in handoff_surface
    assert "handoff/current_handoff.md" in handoff_surface
    assert "Handoff is the first resume surface for already-running PatchOps work." in handoff_surface
