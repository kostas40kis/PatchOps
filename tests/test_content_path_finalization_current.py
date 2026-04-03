from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_finalization_plan_mentions_content_path_repair_completion() -> None:
    content = (PROJECT_ROOT / "docs" / "finalization_master_plan.md").read_text(encoding="utf-8")
    assert "## content_path wrapper-root repair completion note" in content
    assert "CP1 proved the duplicated nested patch-prefix bug" in content
    assert "CP7 refreshed the new-target onboarding surfaces" in content
    assert "wrapper-relative paths from the wrapper project root" in content
    assert "compatibility fallback rather than the primary contract" in content
    assert "do not reopen this area unless new contrary repo evidence appears" in content
    assert "Any future work here should be narrow maintenance, not redesign." in content
