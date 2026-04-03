from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_keeps_final_maintenance_posture_visible() -> None:
    text = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "## Final maintenance posture" in text
    assert "maintained utility rather than an open-ended architecture buildout" in text
    assert "handoff/current_handoff.md" in text
    assert "docs/finalization_master_plan.md" in text
    assert "maintenance-mode wrapper" in text


def test_llm_usage_keeps_final_maintenance_reading_order_visible() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_usage.md").read_text(encoding="utf-8")

    assert "## Final maintenance-mode reading order" in text
    assert "handoff/current_handoff.md" in text
    assert "docs/projects/<project_name>.md" in text
    assert "verify reality," in text
    assert "repair narrowly," in text
    assert "docs/finalization_master_plan.md" in text


def test_operator_quickstart_keeps_final_split_visible() -> None:
    text = (PROJECT_ROOT / "docs" / "operator_quickstart.md").read_text(encoding="utf-8")

    assert "## Final maintenance-mode quickstart" in text
    assert "### Already-running PatchOps work" in text
    assert "### Brand-new target onboarding" in text
    assert "Read the handoff bundle first when it exists." in text
    assert "docs/finalization_master_plan.md" in text


def test_project_status_tracks_post_f4_state() -> None:
    text = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")

    assert "## Patch 127 - final contract-lock validation sweep" in text
    assert "## Patch 128 - active-work continuation flow proof" in text
    assert "latest confirmed green head: Patch 128" in text
    assert "remaining finalization sequence is F5 through F8, not a redesign wave" in text
    assert "maintenance / refinement posture" in text


def test_finalization_master_plan_tracks_post_f4_state() -> None:
    text = (PROJECT_ROOT / "docs" / "finalization_master_plan.md").read_text(encoding="utf-8")

    assert "- **Latest confirmed green head:** Patch 128" in text
    assert "## Patch 127 - final contract-lock validation sweep" in text
    assert "## Patch 128 - prove active-work continuation flow" in text
    assert "- **F5 — prove the new-target onboarding flow**" in text
    assert "finished enough to freeze" in text
